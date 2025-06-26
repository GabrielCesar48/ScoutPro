"""
URLs do app core
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_evaluation

app_name = 'core'

urlpatterns = [
    # Página inicial (redireciona para dashboard baseado no usuário)
    path('', views.HomeView.as_view(), name='home'),
    
    # Autenticação
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboards
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/coach/', views.CoachDashboardView.as_view(), name='coach_dashboard'),
    path('dashboard/player/', views.PlayerDashboardView.as_view(), name='player_dashboard'),
    
    # Perfil
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Sistema de Avaliação
    path('games/', views_evaluation.GameListView.as_view(), name='game_list'),
    path('games/create/', views_evaluation.GameCreateView.as_view(), name='game_create'),
    path('games/<int:pk>/', views_evaluation.GameDetailView.as_view(), name='game_detail'),
    path('games/<int:game_id>/players/', views_evaluation.player_selection_view, name='player_selection'),
    path('games/<int:game_id>/lineup/', views_evaluation.game_lineup_view, name='game_lineup'),
    path('games/<int:game_id>/evaluation/', views_evaluation.game_evaluation_view, name='game_evaluation'),
    
    # APIs AJAX
    path('api/evaluation/add/', views_evaluation.api_add_evaluation, name='api_add_evaluation'),
    path('api/substitution/make/', views_evaluation.api_make_substitution, name='api_make_substitution'),
    path('api/games/<int:game_id>/stats/', views_evaluation.api_game_stats, name='api_game_stats'),
    path('api/games/<int:game_id>/time/', views_evaluation.api_update_game_time, name='api_update_game_time'),
    
    # NOVA API para salvamento completo
    path('api/games/save-complete/', views_evaluation.api_save_complete_game, name='api_save_complete_game'),
]