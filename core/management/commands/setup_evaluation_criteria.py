from django.core.management.base import BaseCommand
from core.models import EvaluationCriteria
from django.db import transaction


class Command(BaseCommand):
    help = 'Configura critérios de avaliação padrão do ScoutPro'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove critérios existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Configurando critérios de avaliação...')
        )

        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_criteria()
                
                self.create_field_player_criteria()
                self.create_goalkeeper_criteria()
                
            self.stdout.write(
                self.style.SUCCESS('✅ Critérios de avaliação configurados!')
            )
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante a configuração: {str(e)}')
            )

    def reset_criteria(self):
        """Remove critérios existentes"""
        EvaluationCriteria.objects.all().delete()
        self.stdout.write(
            self.style.WARNING('⚠️  Critérios existentes removidos')
        )

    def create_field_player_criteria(self):
        """Cria critérios para jogadores de linha"""
        self.stdout.write('⚽ Criando critérios para jogadores de linha...')
        
        field_criteria = [
            # Critérios Positivos (+1)
            {
                'name': 'Ação Boa',
                'code': 'acao_boa',
                'description': 'Jogada ofensiva, passe decisivo, recuperação importante',
                'criteria_type': 'positive',
                'player_type': 'field',
                'points': 1,
                'icon': 'fas fa-check-circle',
                'color': 'success'
            },
            
            # Critérios Especiais (+2)
            {
                'name': 'Gol',
                'code': 'gol',
                'description': 'Gol marcado pelo jogador',
                'criteria_type': 'special',
                'player_type': 'field',
                'points': 2,
                'icon': 'fas fa-futbol',
                'color': 'warning'
            },
            {
                'name': 'Assistência',
                'code': 'assistencia',
                'description': 'Passe que resultou em gol',
                'criteria_type': 'special',
                'player_type': 'field',
                'points': 2,
                'icon': 'fas fa-hands-helping',
                'color': 'warning'
            },
            {
                'name': 'Jogada Genial',
                'code': 'jogada_genial',
                'description': 'Drible espetacular, passe impossível, decisão brilhante',
                'criteria_type': 'special',
                'player_type': 'field',
                'points': 2,
                'icon': 'fas fa-brain',
                'color': 'warning'
            },
            
            # Critérios Negativos (-1)
            {
                'name': 'Erro',
                'code': 'erro',
                'description': 'Perda de bola perigosa, falta boba, chance perdida',
                'criteria_type': 'negative',
                'player_type': 'field',
                'points': -1,
                'icon': 'fas fa-times-circle',
                'color': 'danger'
            },
        ]
        
        for criteria_data in field_criteria:
            criteria, created = EvaluationCriteria.objects.get_or_create(
                code=criteria_data['code'],
                defaults=criteria_data
            )
            if created:
                self.stdout.write(f'  ✅ {criteria.name} ({criteria.points:+d})')

    def create_goalkeeper_criteria(self):
        """Cria critérios específicos para goleiros"""
        self.stdout.write('🥅 Criando critérios para goleiros...')
        
        goalkeeper_criteria = [
            # Critérios Positivos (+1)
            {
                'name': 'Defesa Boa',
                'code': 'defesa_boa',
                'description': 'Salvou o chute, saída no tempo certo, reposição rápida',
                'criteria_type': 'positive',
                'player_type': 'goalkeeper',
                'points': 1,
                'icon': 'fas fa-hand-paper',
                'color': 'success'
            },
            
            # Critérios Especiais (+2)
            {
                'name': 'Defesa Salvadora',
                'code': 'defesa_salvadora',
                'description': 'Defesa espetacular, salvou gol certo',
                'criteria_type': 'special',
                'player_type': 'goalkeeper',
                'points': 2,
                'icon': 'fas fa-medal',
                'color': 'warning'
            },
            
            # Critérios Negativos (-1)
            {
                'name': 'Falha do Goleiro',
                'code': 'falha_goleiro',
                'description': 'Saída errada, passe errado, gol por falha',
                'criteria_type': 'negative',
                'player_type': 'goalkeeper',
                'points': -1,
                'icon': 'fas fa-times-circle',
                'color': 'danger'
            },
        ]
        
        for criteria_data in goalkeeper_criteria:
            criteria, created = EvaluationCriteria.objects.get_or_create(
                code=criteria_data['code'],
                defaults=criteria_data
            )
            if created:
                self.stdout.write(f'  ✅ {criteria.name} ({criteria.points:+d})')

    def print_summary(self):
        """Imprime resumo dos critérios criados"""
        total = EvaluationCriteria.objects.count()
        positive = EvaluationCriteria.objects.filter(criteria_type='positive').count()
        special = EvaluationCriteria.objects.filter(criteria_type='special').count()
        negative = EvaluationCriteria.objects.filter(criteria_type='negative').count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('📊 RESUMO DOS CRITÉRIOS')
        )
        self.stdout.write('='*50)
        
        self.stdout.write(f'📈 Critérios Positivos: {positive}')
        self.stdout.write(f'⭐ Critérios Especiais: {special}') 
        self.stdout.write(f'📉 Critérios Negativos: {negative}')
        self.stdout.write(f'📊 Total de Critérios: {total}')
        
        self.stdout.write('\n🎯 CRITÉRIOS PARA JOGADORES DE LINHA:')
        field_criteria = EvaluationCriteria.objects.filter(
            player_type__in=['field', 'all']
        ).order_by('criteria_type', '-points')
        
        for criteria in field_criteria:
            self.stdout.write(f'  • {criteria.name}: {criteria.points:+d} pontos')
        
        self.stdout.write('\n🥅 CRITÉRIOS PARA GOLEIROS:')
        gk_criteria = EvaluationCriteria.objects.filter(
            player_type__in=['goalkeeper', 'all']
        ).order_by('criteria_type', '-points')
        
        for criteria in gk_criteria:
            self.stdout.write(f'  • {criteria.name}: {criteria.points:+d} pontos')
        
        self.stdout.write('\n💡 Para usar os critérios:')
        self.stdout.write('1. Crie um jogo: /games/create/')
        self.stdout.write('2. Selecione jogadores')
        self.stdout.write('3. Defina escalação')
        self.stdout.write('4. Inicie avaliação em tempo real')
        
        self.stdout.write('\n' + '='*50)