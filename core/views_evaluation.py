from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json

from .models import (
    Game, Player, GamePlayer, PlayerEvaluation, 
    EvaluationCriteria, Substitution, get_player_stats
)


class GameListView(LoginRequiredMixin, ListView):
    """
    Lista de jogos (apenas para comissão técnica)
    """
    model = Game
    template_name = 'evaluation/game_list.html'
    context_object_name = 'games'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'coach':
            messages.error(request, 'Acesso negado. Área restrita para comissão técnica.')
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Game.objects.all().order_by('-date')


class GameCreateView(LoginRequiredMixin, CreateView):
    """
    Criar novo jogo/treino
    """
    model = Game
    template_name = 'evaluation/game_create.html'
    fields = ['title', 'game_type', 'date', 'location', 'opponent']
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.user_type != 'coach':
            messages.error(request, 'Acesso negado. Área restrita para comissão técnica.')
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Jogo criado com sucesso!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('core:game_detail', kwargs={'pk': self.object.pk})


class GameDetailView(LoginRequiredMixin, DetailView):
    """
    Detalhes do jogo
    """
    model = Game
    template_name = 'evaluation/game_detail.html'
    context_object_name = 'game'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.object
        
        # Buscar jogadores do jogo
        context['game_players'] = GamePlayer.objects.filter(game=game).select_related('player__user')
        context['selected_players'] = context['game_players'].filter(status='selected')
        context['starting_players'] = context['game_players'].filter(status__in=['starting', 'playing'])
        context['bench_players'] = context['game_players'].filter(status='bench')
        
        # Buscar substituições
        context['substitutions'] = Substitution.objects.filter(game=game).order_by('game_time')
        
        return context


@login_required
def player_selection_view(request, game_id):
    """
    Tela de seleção de jogadores para o jogo
    """
    if request.user.user_type != 'coach':
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        selected_player_ids = request.POST.getlist('selected_players')
        
        if len(selected_player_ids) < 5:
            messages.error(request, 'Selecione pelo menos 5 jogadores.')
        else:
            # Limpar seleções anteriores
            GamePlayer.objects.filter(game=game).delete()
            
            # Adicionar jogadores selecionados
            for player_id in selected_player_ids:
                player = get_object_or_404(Player, id=player_id)
                GamePlayer.objects.create(
                    game=game,
                    player=player,
                    status='selected'
                )
            
            messages.success(request, f'{len(selected_player_ids)} jogadores selecionados!')
            return redirect('core:game_lineup', game_id=game.id)
    
    # Buscar todos os jogadores disponíveis
    all_players = Player.objects.filter(is_active=True).select_related('user', 'team')
    selected_players = GamePlayer.objects.filter(game=game).values_list('player_id', flat=True)
    
    context = {
        'game': game,
        'all_players': all_players,
        'selected_players': list(selected_players),
    }
    
    return render(request, 'evaluation/player_selection.html', context)


@login_required
def game_lineup_view(request, game_id):
    """
    Tela de escalação inicial
    """
    if request.user.user_type != 'coach':
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    
    game = get_object_or_404(Game, id=game_id)
    game_players = GamePlayer.objects.filter(game=game).select_related('player__user')
    
    if request.method == 'POST':
        starting_player_ids = request.POST.getlist('starting_players')
        
        if len(starting_player_ids) != 5:
            messages.error(request, 'Selecione exatamente 5 jogadores titulares.')
        else:
            with transaction.atomic():
                # Resetar todos para 'selected'
                game_players.update(status='selected')
                
                # Definir titulares
                for player_id in starting_player_ids:
                    GamePlayer.objects.filter(
                        game=game, 
                        player_id=player_id
                    ).update(status='starting')
                
                # Definir reservas
                GamePlayer.objects.filter(game=game).exclude(
                    player_id__in=starting_player_ids
                ).update(status='bench')
            
            messages.success(request, 'Escalação definida com sucesso!')
            return redirect('core:game_evaluation', game_id=game.id)
    
    context = {
        'game': game,
        'game_players': game_players,
        'selected_players': game_players.filter(status='selected'),
        'starting_players': game_players.filter(status='starting'),
        'bench_players': game_players.filter(status='bench'),
    }
    
    return render(request, 'evaluation/game_lineup.html', context)


@login_required
def game_evaluation_view(request, game_id):
    """
    Tela principal de avaliação em tempo real
    """
    if request.user.user_type != 'coach':
        messages.error(request, 'Acesso negado.')
        return redirect('core:home')
    
    game = get_object_or_404(Game, id=game_id)
    
    # Buscar jogadores em campo
    playing_players = GamePlayer.objects.filter(
        game=game, 
        status__in=['starting', 'playing']
    ).select_related('player__user')
    
    # Buscar jogadores no banco
    bench_players = GamePlayer.objects.filter(
        game=game, 
        status='bench'
    ).select_related('player__user')
    
    # Buscar critérios de avaliação
    field_criteria = EvaluationCriteria.objects.filter(
        is_active=True,
        player_type__in=['field', 'all']
    ).order_by('criteria_type', 'points')
    
    goalkeeper_criteria = EvaluationCriteria.objects.filter(
        is_active=True,
        player_type__in=['goalkeeper', 'all']
    ).order_by('criteria_type', 'points')
    
    context = {
        'game': game,
        'playing_players': playing_players,
        'bench_players': bench_players,
        'field_criteria': field_criteria,
        'goalkeeper_criteria': goalkeeper_criteria,
    }
    
    return render(request, 'evaluation/game_evaluation.html', context)


# APIs AJAX para o sistema de avaliação

@login_required
@require_POST
def api_add_evaluation(request):
    """
    API para adicionar avaliação via AJAX - COM INTEGRAÇÃO DE PLACAR
    """
    if request.user.user_type != 'coach':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        data = json.loads(request.body)
        game_player_id = data.get('game_player_id')
        criteria_id = data.get('criteria_id')
        game_time = data.get('game_time', 0)
        notes = data.get('notes', '')
        
        game_player = get_object_or_404(GamePlayer, id=game_player_id)
        criteria = get_object_or_404(EvaluationCriteria, id=criteria_id)
        
        # Criar avaliação
        evaluation = PlayerEvaluation.objects.create(
            game_player=game_player,
            criteria=criteria,
            game_time=game_time,
            evaluated_by=request.user,
            notes=notes
        )
        
        # INTEGRAÇÃO COM PLACAR - SE FOR GOL, INCREMENTAR AUTOMATICAMENTE
        goal_added = False
        if criteria.code == 'gol':
            game = game_player.game
            game.team_goals += 1
            game.save()
            goal_added = True
        
        # Retornar estatísticas atualizadas
        stats = get_player_stats(game_player.player, game_player.game)
        
        response_data = {
            'success': True,
            'evaluation_id': evaluation.id,
            'stats': stats,
            'message': f'Avaliação adicionada: {criteria.name}'
        }
        
        # Adicionar dados do placar se foi gol
        if goal_added:
            response_data['goal_added'] = True
            response_data['team_goals'] = game.team_goals
            response_data['opponent_goals'] = game.opponent_goals
            response_data['score_display'] = game.score_display
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)


@login_required
@require_POST
def api_make_substitution(request):
    """
    API para fazer substituição via AJAX
    """
    if request.user.user_type != 'coach':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        player_out_id = data.get('player_out_id')
        player_in_id = data.get('player_in_id')
        game_time = data.get('game_time', 0)
        
        game = get_object_or_404(Game, id=game_id)
        player_out = get_object_or_404(Player, id=player_out_id)
        player_in = get_object_or_404(Player, id=player_in_id)
        
        with transaction.atomic():
            # Atualizar status dos jogadores
            GamePlayer.objects.filter(
                game=game, player=player_out
            ).update(status='substituted')
            
            GamePlayer.objects.filter(
                game=game, player=player_in
            ).update(status='playing')
            
            # Registrar substituição
            substitution = Substitution.objects.create(
                game=game,
                player_out=player_out,
                player_in=player_in,
                game_time=game_time,
                made_by=request.user
            )
        
        return JsonResponse({
            'success': True,
            'substitution_id': substitution.id,
            'message': f'{player_out.user.full_name} ⇄ {player_in.user.full_name}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_game_stats(request, game_id):
    """
    API para buscar estatísticas do jogo
    """
    game = get_object_or_404(Game, id=game_id)
    
    # Buscar estatísticas de todos os jogadores do jogo
    game_players = GamePlayer.objects.filter(game=game).select_related('player__user')
    
    stats_data = []
    for gp in game_players:
        player_stats = get_player_stats(gp.player, game)
        stats_data.append({
            'player_id': gp.player.id,
            'player_name': gp.player.user.full_name or gp.player.user.username,
            'position': gp.player.get_position_display(),
            'status': gp.get_status_display(),
            'time_played': gp.time_formatted,
            'stats': player_stats
        })
    
    return JsonResponse({
        'game_title': game.title,
        'game_status': game.get_status_display(),
        'duration': game.duration_formatted,
        'players': stats_data
    })


@login_required
@require_POST
def api_update_game_time(request, game_id):
    """
    API para atualizar tempo do jogo
    """
    if request.user.user_type != 'coach':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        data = json.loads(request.body)
        duration = data.get('duration', 0)
        status = data.get('status', 'in_progress')
        
        game = get_object_or_404(Game, id=game_id)
        game.duration = duration
        game.status = status
        game.save()
        
        return JsonResponse({
            'success': True,
            'duration': game.duration_formatted,
            'status': game.get_status_display()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)        
        
@login_required
@require_POST
def api_opponent_goal(request):
    """
    API para controlar gols do adversário E do time
    """
    if request.user.user_type != 'coach':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        action = data.get('action')  # 'add' ou 'remove'
        team_goal = data.get('team_goal', False)  # True se for gol do time
        
        game = get_object_or_404(Game, id=game_id)
        
        if action == 'add':
            if team_goal:
                game.team_goals += 1
            else:
                game.opponent_goals += 1
        elif action == 'remove':
            if team_goal:
                game.team_goals = max(0, game.team_goals - 1)
            else:
                game.opponent_goals = max(0, game.opponent_goals - 1)
        else:
            return JsonResponse({'error': 'Ação inválida'}, status=400)
        
        game.save()
        
        return JsonResponse({
            'success': True,
            'team_goals': game.team_goals,
            'opponent_goals': game.opponent_goals,
            'score_display': game.score_display
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro: {str(e)}'}, status=500)

@login_required
@require_POST
def api_save_complete_game(request):
    """
    API para salvar jogo completo no banco de dados com placar
    """
    if request.user.user_type != 'coach':
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        
        game = get_object_or_404(Game, id=game_id)
        
        with transaction.atomic():
            # Atualizar dados básicos do jogo
            game.duration = data.get('duration', 0)
            game.status = data.get('status', 'finished')
            
            # ATUALIZAR PLACAR
            if 'team_goals' in data:
                game.team_goals = data['team_goals']
            if 'opponent_goals' in data:
                game.opponent_goals = data['opponent_goals']
            
            game.save()
            
            # Limpar avaliações antigas
            PlayerEvaluation.objects.filter(game_player__game=game).delete()
            
            # Salvar avaliações
            evaluation_data = data.get('evaluation_data', {})
            total_evaluations = 0
            
            for player_id, player_data in evaluation_data.items():
                try:
                    player = Player.objects.get(id=player_id)
                    game_player = GamePlayer.objects.get(game=game, player=player)
                    
                    # Salvar timeline de avaliações
                    timeline = player_data.get('timeline', [])
                    for evaluation in timeline:
                        # Criar ou buscar critério
                        criteria, created = EvaluationCriteria.objects.get_or_create(
                            code=evaluation['criteria'],
                            defaults={
                                'name': evaluation['criteria'].replace('_', ' ').title(),
                                'criteria_type': evaluation['category'],
                                'points': evaluation['points'],
                                'player_type': 'all',
                                'is_active': True
                            }
                        )
                        
                        PlayerEvaluation.objects.create(
                            game_player=game_player,
                            criteria=criteria,
                            game_time=evaluation.get('time', 0),
                            evaluated_by=request.user,
                            notes=f"Tempo: {evaluation.get('gameTime', '00:00')}"
                        )
                        total_evaluations += 1
                        
                except (Player.DoesNotExist, GamePlayer.DoesNotExist):
                    continue
            
            # Atualizar tempos dos jogadores
            player_times = data.get('player_times', {})
            for player_id, time_data in player_times.items():
                try:
                    player = Player.objects.get(id=player_id)
                    game_player = GamePlayer.objects.get(game=game, player=player)
                    game_player.total_time = time_data.get('totalTime', 0) // 1000  # Converter para segundos
                    game_player.save()
                except (Player.DoesNotExist, GamePlayer.DoesNotExist):
                    continue
            
            # Limpar substituições antigas
            Substitution.objects.filter(game=game).delete()
            
            # Salvar substituições
            substitutions = data.get('substitutions', [])
            total_substitutions = 0
            
            for sub_data in substitutions:
                try:
                    # Buscar jogadores pelos nomes (pode ser melhorado)
                    player_out = Player.objects.filter(
                        user__full_name__icontains=sub_data['playerOut']
                    ).first()
                    player_in = Player.objects.filter(
                        user__full_name__icontains=sub_data['playerIn']
                    ).first()
                    
                    if player_out and player_in:
                        Substitution.objects.create(
                            game=game,
                            player_out=player_out,
                            player_in=player_in,
                            game_time=sub_data.get('time', 0) // 1000,  # Converter para segundos
                            made_by=request.user
                        )
                        total_substitutions += 1
                        
                except Exception as e:
                    continue
            
            return JsonResponse({
                'success': True,
                'total_evaluations': total_evaluations,
                'total_substitutions': total_substitutions,
                'final_score': game.score_display,
                'message': 'Jogo salvo com sucesso!'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)