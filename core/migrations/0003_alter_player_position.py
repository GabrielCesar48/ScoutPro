# Generated by Django 5.2.1 on 2025-05-29 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_evaluationcriteria_game_gameplayer_playerevaluation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='position',
            field=models.CharField(choices=[('goalkeeper', 'Goleiro'), ('defender', 'Fixo'), ('winger', 'Ala'), ('Pivot', 'Pivo'), ('line', 'Linha')], default='line', max_length=15, verbose_name='Posição'),
        ),
    ]
