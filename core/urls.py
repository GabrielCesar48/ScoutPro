"""
URLs do app core
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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
]