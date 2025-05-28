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
        
        
        
    # ADICIONAR ESTES MODELS AO ARQUIVO core/models.py EXISTENTE

class Game(models.Model):
    """
    Model para jogos/treinos
    """
    GAME_TYPE_CHOICES = [
        ('training', 'Treino'),
        ('friendly', 'Amistoso'),
        ('official', 'Jogo Oficial'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Agendado'),
        ('in_progress', 'Em Andamento'),
        ('paused', 'Pausado'),
        ('finished', 'Finalizado'),
        ('cancelled', 'Cancelado'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título do Jogo'
    )
    
    game_type = models.CharField(
        max_length=20,
        choices=GAME_TYPE_CHOICES,
        default='training',
        verbose_name='Tipo'
    )
    
    date = models.DateTimeField(
        verbose_name='Data e Hora'
    )
    
    location = models.CharField(
        max_length=200,
        verbose_name='Local',
        blank=True
    )
    
    opponent = models.CharField(
        max_length=100,
        verbose_name='Adversário',
        blank=True,
        help_text='Deixe em branco para treinos'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Status'
    )
    
    # Dados do cronômetro
    duration = models.PositiveIntegerField(
        default=0,
        verbose_name='Duração (segundos)',
        help_text='Tempo total do jogo em segundos'
    )
    
    # Controle de criação
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Criado por',
        related_name='games_created'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    # Dados adicionais (JSON para flexibilidade)
    game_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Dados do Jogo',
        help_text='Dados adicionais como configurações específicas'
    )
    
    def __str__(self):
        return f"{self.title} - {self.date.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duration_formatted(self):
        """Retorna duração formatada em MM:SS"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    class Meta:
        verbose_name = 'Jogo'
        verbose_name_plural = 'Jogos'
        ordering = ['-date']


class GamePlayer(models.Model):
    """
    Model para jogadores participantes de cada jogo
    """
    STATUS_CHOICES = [
        ('selected', 'Selecionado'),
        ('starting', 'Titular'),
        ('bench', 'Banco'),
        ('playing', 'Em Campo'),
        ('substituted', 'Substituído'),
    ]
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        verbose_name='Jogo',
        related_name='game_players'
    )
    
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        verbose_name='Jogador',
        related_name='game_participations'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='selected',
        verbose_name='Status'
    )
    
    # Tempo de jogo
    total_time = models.PositiveIntegerField(
        default=0,
        verbose_name='Tempo Jogado (segundos)'
    )
    
    # Sessões de tempo (para controlar substituições)
    time_sessions = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Sessões de Tempo',
        help_text='Lista de períodos em campo'
    )
    
    def __str__(self):
        return f"{self.player.user.full_name} - {self.game.title}"
    
    @property
    def time_formatted(self):
        """Retorna tempo formatado em MM:SS"""
        minutes = self.total_time // 60
        seconds = self.total_time % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    class Meta:
        verbose_name = 'Jogador do Jogo'
        verbose_name_plural = 'Jogadores do Jogo'
        unique_together = ['game', 'player']


class EvaluationCriteria(models.Model):
    """
    Model para critérios de avaliação
    """
    CRITERIA_TYPE_CHOICES = [
        ('positive', 'Positivo'),
        ('special', 'Especial'),
        ('negative', 'Negativo'),
    ]
    
    PLAYER_TYPE_CHOICES = [
        ('field', 'Jogador de Linha'),
        ('goalkeeper', 'Goleiro'),
        ('all', 'Todos'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Critério'
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Código único para identificação'
    )
    
    description = models.TextField(
        verbose_name='Descrição',
        blank=True
    )
    
    criteria_type = models.CharField(
        max_length=20,
        choices=CRITERIA_TYPE_CHOICES,
        verbose_name='Tipo'
    )
    
    player_type = models.CharField(
        max_length=20,
        choices=PLAYER_TYPE_CHOICES,
        default='all',
        verbose_name='Aplicável a'
    )
    
    points = models.IntegerField(
        verbose_name='Pontos',
        help_text='Pontos atribuídos (pode ser negativo)'
    )
    
    icon = models.CharField(
        max_length=50,
        verbose_name='Ícone',
        default='fas fa-star',
        help_text='Classe do ícone Font Awesome'
    )
    
    color = models.CharField(
        max_length=20,
        verbose_name='Cor',
        default='primary',
        help_text='Classe de cor Bootstrap'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    def __str__(self):
        return f"{self.name} ({self.points:+d})"
    
    class Meta:
        verbose_name = 'Critério de Avaliação'
        verbose_name_plural = 'Critérios de Avaliação'
        ordering = ['criteria_type', 'points']


class PlayerEvaluation(models.Model):
    """
    Model para avaliações dos jogadores durante o jogo
    """
    game_player = models.ForeignKey(
        GamePlayer,
        on_delete=models.CASCADE,
        verbose_name='Jogador do Jogo',
        related_name='evaluations'
    )
    
    criteria = models.ForeignKey(
        EvaluationCriteria,
        on_delete=models.CASCADE,
        verbose_name='Critério'
    )
    
    # Quando a avaliação foi feita
    game_time = models.PositiveIntegerField(
        verbose_name='Tempo do Jogo (segundos)',
        help_text='Momento do jogo quando a avaliação foi feita'
    )
    
    # Quem fez a avaliação
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Avaliado por',
        related_name='evaluations_made'
    )
    
    # Observações adicionais
    notes = models.TextField(
        verbose_name='Observações',
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    def __str__(self):
        return f"{self.game_player.player.user.full_name} - {self.criteria.name}"
    
    @property
    def game_time_formatted(self):
        """Retorna tempo do jogo formatado em MM:SS"""
        minutes = self.game_time // 60
        seconds = self.game_time % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    class Meta:
        verbose_name = 'Avaliação de Jogador'
        verbose_name_plural = 'Avaliações de Jogadores'
        ordering = ['-created_at']


class Substitution(models.Model):
    """
    Model para substituições durante o jogo
    """
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        verbose_name='Jogo',
        related_name='substitutions'
    )
    
    player_out = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        verbose_name='Sai de Campo',
        related_name='substitutions_out'
    )
    
    player_in = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        verbose_name='Entra no Jogo',
        related_name='substitutions_in'
    )
    
    game_time = models.PositiveIntegerField(
        verbose_name='Tempo do Jogo (segundos)'
    )
    
    made_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Feita por',
        related_name='substitutions_made'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    def __str__(self):
        return f"{self.player_out.user.full_name} ⇄ {self.player_in.user.full_name}"
    
    @property
    def game_time_formatted(self):
        """Retorna tempo do jogo formatado em MM:SS"""
        minutes = self.game_time // 60
        seconds = self.game_time % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    class Meta:
        verbose_name = 'Substituição'
        verbose_name_plural = 'Substituições'
        ordering = ['-created_at']


# Método helper para estatísticas de jogador
def get_player_stats(player, game=None):
    """
    Retorna estatísticas de um jogador
    """
    from django.db.models import Sum, Count
    
    # Filtrar por jogo específico ou todos os jogos
    if game:
        evaluations = PlayerEvaluation.objects.filter(
            game_player__player=player,
            game_player__game=game
        )
    else:
        evaluations = PlayerEvaluation.objects.filter(
            game_player__player=player
        )
    
    # Agrupar por tipo de critério
    stats = {
        'positive': evaluations.filter(criteria__criteria_type='positive').aggregate(
            count=Count('id'),
            points=Sum('criteria__points')
        ),
        'special': evaluations.filter(criteria__criteria_type='special').aggregate(
            count=Count('id'),
            points=Sum('criteria__points')
        ),
        'negative': evaluations.filter(criteria__criteria_type='negative').aggregate(
            count=Count('id'),
            points=Sum('criteria__points')
        ),
    }
    
    # Calcular totais
    total_points = 0
    for category in stats.values():
        if category['points']:
            total_points += category['points']
    
    stats['total'] = {
        'count': evaluations.count(),
        'points': total_points
    }
    
    return stats