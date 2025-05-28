from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Team, Player
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura dados iniciais do ScoutPro'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todos os dados existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando configuração do ScoutPro...')
        )

        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_data()
                
                self.create_superuser()
                self.create_team()
                self.create_demo_users()
                
            self.stdout.write(
                self.style.SUCCESS('✅ ScoutPro configurado com sucesso!')
            )
            self.print_credentials()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante a configuração: {str(e)}')
            )

    def reset_data(self):
        """Remove todos os dados existentes"""
        self.stdout.write('🔄 Removendo dados existentes...')
        
        Player.objects.all().delete()
        Team.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(
            self.style.WARNING('⚠️  Dados existentes removidos')
        )

    def create_superuser(self):
        """Cria o superusuário se não existir"""
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@scoutpro.com',
                password='admin123',
                full_name='Administrador do Sistema',
                user_type='coach'
            )
            self.stdout.write(
                self.style.SUCCESS('👤 Superusuário criado')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Superusuário já existe')
            )

    def create_team(self):
        """Cria time de exemplo"""
        team, created = Team.objects.get_or_create(
            name='Time Principal',
            defaults={
                'primary_color': '#007bff',
                'secondary_color': '#28a745',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('⚽ Time principal criado')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Time já existe')
            )
        
        return team

    def create_demo_users(self):
        """Cria usuários de demonstração"""
        team = Team.objects.get(name='Time Principal')
        
        # Criar usuário da comissão técnica
        coach, created = User.objects.get_or_create(
            username='coach',
            defaults={
                'email': 'coach@scoutpro.com',
                'full_name': 'João Silva',
                'user_type': 'coach',
                'phone': '(11) 99999-1111'
            }
        )
        if created:
            coach.set_password('coach123')
            coach.save()
            self.stdout.write(
                self.style.SUCCESS('👨‍💼 Usuário da comissão técnica criado')
            )

        # Criar jogadores de exemplo
        players_data = [
            {
                'username': 'player1',
                'full_name': 'Pedro Santos',
                'email': 'pedro@scoutpro.com',
                'phone': '(11) 99999-2222',
                'shirt_number': 10,
                'position': 'forward',
                'height': 175.0,
                'weight': 70.0,
            },
            {
                'username': 'player2',
                'full_name': 'Carlos Oliveira',
                'email': 'carlos@scoutpro.com',
                'phone': '(11) 99999-3333',
                'shirt_number': 9,
                'position': 'midfielder',
                'height': 180.0,
                'weight': 75.0,
            },
            {
                'username': 'player3',
                'full_name': 'Rafael Costa',
                'email': 'rafael@scoutpro.com',
                'phone': '(11) 99999-4444',
                'shirt_number': 1,
                'position': 'goalkeeper',
                'height': 185.0,
                'weight': 80.0,
            },
            {
                'username': 'player4',
                'full_name': 'Lucas Almeida',
                'email': 'lucas@scoutpro.com',
                'phone': '(11) 99999-5555',
                'shirt_number': 5,
                'position': 'defender',
                'height': 178.0,
                'weight': 73.0,
            },
            {
                'username': 'player5',
                'full_name': 'Gabriel Ferreira',
                'email': 'gabriel@scoutpro.com',
                'phone': '(11) 99999-6666',
                'shirt_number': 7,
                'position': 'line',
                'height': 172.0,
                'weight': 68.0,
            },
        ]
        
        for player_data in players_data:
            # Separar dados do usuário e do jogador
            user_data = {
                'username': player_data['username'],
                'full_name': player_data['full_name'],
                'email': player_data['email'],
                'phone': player_data['phone'],
                'user_type': 'player'
            }
            
            player_info = {
                'shirt_number': player_data['shirt_number'],
                'position': player_data['position'],
                'height': player_data['height'],
                'weight': player_data['weight'],
            }
            
            # Criar usuário
            user, user_created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if user_created:
                user.set_password('player123')
                user.save()
                
                # Criar perfil de jogador
                Player.objects.create(
                    user=user,
                    team=team,
                    **player_info
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'⚽ Jogador {user.full_name} criado')
                )

    def print_credentials(self):
        """Imprime as credenciais de acesso"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('🔑 CREDENCIAIS DE ACESSO')
        )
        self.stdout.write('='*50)
        
        self.stdout.write('\n👨‍💼 ADMINISTRADOR:')
        self.stdout.write('   Usuário: admin')
        self.stdout.write('   Senha: admin123')
        self.stdout.write('   URL: /admin/')
        
        self.stdout.write('\n👨‍💼 COMISSÃO TÉCNICA:')
        self.stdout.write('   Usuário: coach')
        self.stdout.write('   Senha: coach123')
        
        self.stdout.write('\n⚽ JOGADORES:')
        self.stdout.write('   Usuários: player1, player2, player3, player4, player5')
        self.stdout.write('   Senha: player123 (para todos)')
        
        self.stdout.write('\n🌐 Para acessar o sistema:')
        self.stdout.write('   1. Execute: python manage.py runserver')
        self.stdout.write('   2. Acesse: http://localhost:8000')
        
        self.stdout.write('\n' + '='*50)