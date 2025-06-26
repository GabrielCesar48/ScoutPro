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
        count = EvaluationCriteria.objects.count()
        EvaluationCriteria.objects.all().delete()
        self.stdout.write(
            self.style.WARNING(f'⚠️  {count} critérios existentes removidos')
        )

    def create_field_player_criteria(self):
        """Cria critérios para jogadores de linha - IGUAIS AO SISTEMA ORIGINAL"""
        self.stdout.write('⚽ Criando critérios para jogadores de linha...')
        
        field_criteria = [
            # AÇÃO BOA (+1) - IGUAL AO ORIGINAL
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
            
            # IMPACTO NO JOGO (+2) - IGUAL AO ORIGINAL
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
            
            # ERRO (-1) - IGUAL AO ORIGINAL
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
            else:
                self.stdout.write(f'  ⚠️  {criteria.name} já existe')

    def create_goalkeeper_criteria(self):
        """Cria critérios específicos para goleiros - IGUAIS AO ORIGINAL"""
        self.stdout.write('🥅 Criando critérios para goleiros...')
        
        goalkeeper_criteria = [
            # DEFESA BOA (+1)
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
            
            # DEFESA SALVADORA (+2)
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
            
            # FALHA (-1)
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
            else:
                self.stdout.write(f'  ⚠️  {criteria.name} já existe')

    def print_summary(self):
        """Imprime resumo dos critérios criados"""
        total = EvaluationCriteria.objects.count()
        positive = EvaluationCriteria.objects.filter(criteria_type='positive').count()
        special = EvaluationCriteria.objects.filter(criteria_type='special').count()
        negative = EvaluationCriteria.objects.filter(criteria_type='negative').count()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('📊 RESUMO DOS CRITÉRIOS DE AVALIAÇÃO')
        )
        self.stdout.write('='*60)
        
        self.stdout.write(f'📈 Critérios Positivos: {positive}')
        self.stdout.write(f'⭐ Critérios Especiais: {special}') 
        self.stdout.write(f'📉 Critérios Negativos: {negative}')
        self.stdout.write(f'📊 Total de Critérios: {total}')
        
        self.stdout.write('\n🎯 CRITÉRIOS PARA JOGADORES DE LINHA:')
        field_criteria = EvaluationCriteria.objects.filter(
            player_type__in=['field', 'all']
        ).order_by('criteria_type', '-points')
        
        for criteria in field_criteria:
            icon = '📈' if criteria.criteria_type == 'positive' else '⭐' if criteria.criteria_type == 'special' else '📉'
            self.stdout.write(f'  {icon} {criteria.name}: {criteria.points:+d} pontos')
        
        self.stdout.write('\n🥅 CRITÉRIOS PARA GOLEIROS:')
        gk_criteria = EvaluationCriteria.objects.filter(
            player_type__in=['goalkeeper', 'all']
        ).order_by('criteria_type', '-points')
        
        for criteria in gk_criteria:
            icon = '📈' if criteria.criteria_type == 'positive' else '⭐' if criteria.criteria_type == 'special' else '📉'
            self.stdout.write(f'  {icon} {criteria.name}: {criteria.points:+d} pontos')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('🚀 SISTEMA PRONTO PARA USO!')
        )
        self.stdout.write('='*60)
        
        self.stdout.write('\n💡 COMO USAR:')
        self.stdout.write('1. Acesse: /games/create/ para criar um jogo')
        self.stdout.write('2. Selecione jogadores e defina escalação')
        self.stdout.write('3. Inicie avaliação em tempo real')
        self.stdout.write('4. Finalize e salve no final do jogo')
        
        self.stdout.write('\n📝 COMANDOS ÚTEIS:')
        self.stdout.write('• python manage.py setup_initial_data  # Criar dados demo')
        self.stdout.write('• python manage.py setup_evaluation_criteria --reset  # Recriar critérios')
        
        self.stdout.write('\n' + '='*60)