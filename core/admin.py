from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Team, Player, Game, GamePlayer, 
    EvaluationCriteria, PlayerEvaluation, Substitution
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para o modelo User
    """
    list_display = ('username', 'full_name', 'email', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'full_name', 'email')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('user_type', 'full_name', 'phone')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('user_type', 'full_name', 'phone', 'email')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Team
    """
    list_display = ('name', 'logo_preview', 'primary_color', 'secondary_color', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />',
                obj.logo.url
            )
        return "Sem logo"
    logo_preview.short_description = "Logo"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Player
    """
    list_display = ('user', 'team', 'shirt_number', 'position', 'age_display', 'is_active', 'created_at')
    list_filter = ('team', 'position', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__full_name', 'shirt_number')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'team', 'shirt_number', 'position', 'is_active')
        }),
        ('Dados Físicos', {
            'fields': ('height', 'weight', 'birth_date', 'photo'),
            'classes': ('collapse',)
        }),
    )
    
    def age_display(self, obj):
        return f"{obj.age} anos" if obj.age else "Não informado"
    age_display.short_description = "Idade"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'team')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Game
    """
    list_display = ('title', 'game_type', 'date', 'status', 'duration_formatted', 'created_by', 'created_at')
    list_filter = ('game_type', 'status', 'date', 'created_at')
    search_fields = ('title', 'opponent', 'location')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'game_type', 'date', 'location', 'opponent')
        }),
        ('Status e Duração', {
            'fields': ('status', 'duration'),
            'classes': ('collapse',)
        }),
        ('Dados Adicionais', {
            'fields': ('game_data',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    """
    Admin para o modelo GamePlayer
    """
    list_display = ('game', 'player', 'status', 'time_formatted')
    list_filter = ('status', 'game__date', 'player__position')
    search_fields = ('game__title', 'player__user__full_name', 'player__user__username')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('game', 'player__user')


@admin.register(EvaluationCriteria)
class EvaluationCriteriaAdmin(admin.ModelAdmin):
    """
    Admin para o modelo EvaluationCriteria
    """
    list_display = ('name', 'code', 'criteria_type', 'player_type', 'points', 'icon_preview', 'is_active')
    list_filter = ('criteria_type', 'player_type', 'is_active')
    search_fields = ('name', 'code', 'description')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'code', 'description')
        }),
        ('Configurações', {
            'fields': ('criteria_type', 'player_type', 'points', 'is_active')
        }),
        ('Aparência', {
            'fields': ('icon', 'color'),
            'classes': ('collapse',)
        }),
    )
    
    def icon_preview(self, obj):
        return format_html(
            '<i class="{}" style="color: var(--bs-{}); font-size: 1.2rem;"></i>',
            obj.icon,
            obj.color
        )
    icon_preview.short_description = "Preview"


@admin.register(PlayerEvaluation)
class PlayerEvaluationAdmin(admin.ModelAdmin):
    """
    Admin para o modelo PlayerEvaluation
    """
    list_display = ('game_player', 'criteria', 'game_time_formatted', 'evaluated_by', 'created_at')
    list_filter = ('criteria__criteria_type', 'game_player__game__date', 'evaluated_by')
    search_fields = ('game_player__player__user__full_name', 'criteria__name', 'notes')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'game_player__player__user', 
            'criteria', 
            'evaluated_by'
        )


@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    """
    Admin para o modelo Substitution
    """
    list_display = ('game', 'player_out', 'player_in', 'game_time_formatted', 'made_by', 'created_at')
    list_filter = ('game__date', 'made_by')
    search_fields = ('game__title', 'player_out__user__full_name', 'player_in__user__full_name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'game', 
            'player_out__user', 
            'player_in__user', 
            'made_by'
        )


# Personalização do Admin Site
admin.site.site_header = "ScoutPro - Administração"
admin.site.site_title = "ScoutPro Admin"
admin.site.index_title = "Painel de Administração"