from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User, Player, Team

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
    Dashboard da Comissão Técnica
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
        context['total_players'] = Player.objects.filter(is_active=True).count()
        context['total_teams'] = Team.objects.count()
        # Adicionar mais estatísticas conforme necessário
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