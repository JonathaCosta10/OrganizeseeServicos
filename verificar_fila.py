#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')
django.setup()

from rotinas_automaticas.models import FilaExecucao
from datetime import datetime
import pytz

# Timezone do Brasil
brasil_tz = pytz.timezone('America/Sao_Paulo')

print("=== VERIFICAÇÃO DA FILA DE EXECUÇÃO ===")
print(f"Total de itens na fila: {FilaExecucao.objects.count()}")
print()

for item in FilaExecucao.objects.all():
    print(f"ID: {item.id}")
    print(f"Rotina: {item.scheduler_rotina.rotina_definicao.nome_exibicao}")
    print(f"Status: {item.get_status_display()}")
    print(f"Data execução: {item.data_execucao}")
    print(f"Horário execução: {item.horario_execucao}")
    print(f"Prioridade: {item.prioridade}")
    print(f"Tentativa: {item.tentativa_atual}/{item.max_tentativas}")
    if item.arquivo_processado:
        print(f"Arquivo: {item.arquivo_processado}")
    if item.erro_detalhes:
        print(f"Erro: {item.erro_detalhes}")
    print("-" * 50)

# Verificar se há itens para executar agora
agora = datetime.now(brasil_tz)
print(f"\nHorário atual: {agora}")

pendentes = FilaExecucao.objects.filter(
    status='PENDENTE',
    data_execucao__lte=agora.date()
)
print(f"Itens pendentes para hoje: {pendentes.count()}")
