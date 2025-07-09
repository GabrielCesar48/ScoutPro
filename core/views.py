from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import User, Player, Team, Game, PlayerEvaluation

class HomeView(TemplateView):
    """
    View da página inicial - redireciona baseado no tipo de usuário
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == 'coach':
                return redirect('core:coach_dashboard')
            elif request.user.user_type == 'player':
                return redirect('core:player_dashboard')
            else:
                return redirect('core:dashboard')
        else:
            return redirect('core:login')


class CustomLoginView(LoginView):
    """
    View customizada para login
    """
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """
        Redireciona baseado no tipo de usuário após login
        """
        user = self.request.user
        if user.user_type == 'coach':
            return reverse_lazy('core:coach_dashboard')
        elif user.user_type == 'player':
            return reverse_lazy('core:player_dashboard')
        else:
            return reverse_lazy('core:dashboard')
    
    def form_invalid(self, form):
        """
        Adiciona mensagem de erro personalizada
        """
        messages.error(
            self.request,
            'Nome de usuário ou senha incorretos. Tente novamente.'
        )
        return super().form_invalid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard geral (fallback)
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class CoachDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard da Comissão Técnica - VERSÃO CORRIGIDA
    """
    template_name = 'core/coach_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário é da comissão técnica
        if request.user.user_type != 'coach':
            messages.error(request, 'Acesso negado. Área restrita para comissão técnica.')
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 📊 ESTATÍSTICAS BÁSICAS
        context['total_players'] = Player.objects.filter(is_active=True).count()
        context['total_teams'] = Team.objects.count()
        
        # 📅 CÁLCULOS DE DATA
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_week = today - timedelta(days=today.weekday())
        
        # 🎯 JOGOS ESTE MÊS - CORRIGIDO
        games_this_month = Game.objects.filter(
            date__date__gte=start_of_month,
            date__date__lte=today
        ).count()
        context['games_this_month'] = games_this_month
        
        # 📝 AVALIAÇÕES HOJE - CORRIGIDO  
        evaluations_today = PlayerEvaluation.objects.filter(
            created_at__date=today
        ).count()
        context['evaluations_today'] = evaluations_today
        
        # ⚡ ESTATÍSTICAS ADICIONAIS
        context['games_today'] = Game.objects.filter(
            date__date=today
        ).count()
        
        context['games_this_week'] = Game.objects.filter(
            date__date__gte=start_of_week,
            date__date__lte=today
        ).count()
        
        context['evaluations_this_week'] = PlayerEvaluation.objects.filter(
            created_at__date__gte=start_of_week,
            created_at__date__lte=today
        ).count()
        
        context['active_games'] = Game.objects.filter(
            status__in=['in_progress', 'paused']
        ).count()
        
        # 🎮 PRÓXIMOS JOGOS (para o widget)
        context['upcoming_games'] = Game.objects.filter(
            date__gt=timezone.now(),
            status='scheduled'
        ).order_by('date')[:3]
        
        # 📈 JOGOS POR STATUS
        context['scheduled_games'] = Game.objects.filter(
            status='scheduled'
        ).count()
        
        context['finished_games'] = Game.objects.filter(
            status='finished'
        ).count()
        
        # 🏆 ESTATÍSTICAS DE PERFORMANCE (se necessário)
        context['total_evaluations'] = PlayerEvaluation.objects.count()
        
        return context


class PlayerDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard do Jogador
    """
    template_name = 'core/player_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o usuário é jogador
        if request.user.user_type != 'player':
            messages.error(request, 'Acesso negado. Área restrita para jogadores.')
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['player'] = Player.objects.get(user=self.request.user)
        except Player.DoesNotExist:
            context['player'] = None
            messages.warning(
                self.request,
                'Perfil de jogador não encontrado. Entre em contato com a comissão técnica.'
            )
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View do perfil do usuário
    """
    template_name = 'core/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # Se for jogador, buscar dados do player
        if self.request.user.user_type == 'player':
            try:
                context['player'] = Player.objects.get(user=self.request.user)
            except Player.DoesNotExist:
                context['player'] = None
        
        return context