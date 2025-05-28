from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Modelo de usuário customizado
    """
    USER_TYPE_CHOICES = [
        ('coach', 'Comissão Técnica'),
        ('player', 'Jogador'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='player',
        verbose_name='Tipo de Usuário'
    )
    
    full_name = models.CharField(
        max_length=100,
        verbose_name='Nome Completo',
        blank=True
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name='Telefone',
        blank=True
    )
    
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Cadastro'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    def __str__(self):
        return f"{self.full_name or self.username} ({self.get_user_type_display()})"
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class Team(models.Model):
    """
    Modelo para times
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Time'
    )
    
    logo = models.ImageField(
        upload_to='teams/logos/',
        verbose_name='Logo',
        blank=True,
        null=True
    )
    
    primary_color = models.CharField(
        max_length=7,
        verbose_name='Cor Primária',
        default='#007bff',
        help_text='Código hexadecimal da cor (ex: #007bff)'
    )
    
    secondary_color = models.CharField(
        max_length=7,
        verbose_name='Cor Secundária',
        default='#6c757d',
        help_text='Código hexadecimal da cor (ex: #6c757d)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Time'
        verbose_name_plural = 'Times'


class Player(models.Model):
    """
    Modelo para jogadores (extensão do usuário)
    """
    POSITION_CHOICES = [
        ('goalkeeper', 'Goleiro'),
        ('defender', 'Defensor'),
        ('midfielder', 'Meio-campo'),
        ('forward', 'Atacante'),
        ('line', 'Linha'),  # Para futsal
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name='Time',
        related_name='players'
    )
    
    shirt_number = models.PositiveIntegerField(
        verbose_name='Número da Camisa',
        blank=True,
        null=True
    )
    
    position = models.CharField(
        max_length=15,
        choices=POSITION_CHOICES,
        verbose_name='Posição',
        default='line'
    )
    
    height = models.FloatField(
        verbose_name='Altura (cm)',
        blank=True,
        null=True
    )
    
    weight = models.FloatField(
        verbose_name='Peso (kg)',
        blank=True,
        null=True
    )
    
    birth_date = models.DateField(
        verbose_name='Data de Nascimento',
        blank=True,
        null=True
    )
    
    photo = models.ImageField(
        upload_to='players/photos/',
        verbose_name='Foto',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo no Time'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Cadastrado em'
    )
    
    def __str__(self):
        return f"{self.user.full_name or self.user.username} #{self.shirt_number or '?'}"
    
    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    class Meta:
        verbose_name = 'Jogador'
        verbose_name_plural = 'Jogadores'
        unique_together = ['team', 'shirt_number']  # Número único por time