from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Team, Player

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


# Personalização do Admin Site
admin.site.site_header = "ScoutPro - Administração"
admin.site.site_title = "ScoutPro Admin"
admin.site.index_title = "Painel de Administração"