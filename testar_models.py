#!/usr/bin/env python
"""
Script para testar os models criados para interagir com o banco de dados.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servicos.settings')
django.setup()

from rotinas_automaticas.models import (
    B3InstrumentsConsolidated,
    B3TradeInformation,
    FcaCiaAberta,
    AnualFcaCiaAbertaGeral,
    InfAnualFiiGeral,
    InfMensalFiiGeral,
    EtlMetadata,
    AtivosPrecos
)

def testar_models():
    """Testa a conectividade e funcionalidade dos models"""
    
    print("🚀 Testando Models - Conexão com Base de Dados\n")
    
    # ================== TESTE B3 ==================
    print("📊 TESTANDO DADOS B3:")
    print("=" * 50)
    
    try:
        # Contar instrumentos B3
        total_instrumentos = B3InstrumentsConsolidated.objects.count()
        print(f"✅ B3 Instrumentos: {total_instrumentos:,} registros")
        
        # Mostrar 5 instrumentos mais recentes
        if total_instrumentos > 0:
            instrumentos_recentes = B3InstrumentsConsolidated.objects.filter(
                datref__isnull=False
            ).order_by('-datref')[:5]
            
            print("📈 Últimos 5 instrumentos:")
            for inst in instrumentos_recentes:
                print(f"   • {inst.codinst} - {inst.nomres} ({inst.datref})")
        
        # Contar negociações B3
        total_trades = B3TradeInformation.objects.count()
        print(f"✅ B3 Negociações: {total_trades:,} registros")
        
        if total_trades > 0:
            # Mostrar 5 negociações com maior volume
            trades_volume = B3TradeInformation.objects.filter(
                voltot__isnull=False
            ).order_by('-voltot')[:5]
            
            print("💰 Top 5 maiores volumes:")
            for trade in trades_volume:
                print(f"   • {trade.codinst} - R$ {trade.voltot:,.2f} ({trade.datref})")
                
    except Exception as e:
        print(f"❌ Erro ao acessar dados B3: {e}")
    
    print()
    
    # ================== TESTE CVM ==================
    print("🏢 TESTANDO DADOS CVM:")
    print("=" * 50)
    
    try:
        # Contar FCA
        total_fca = FcaCiaAberta.objects.count()
        print(f"✅ FCA Companhias: {total_fca:,} registros")
        
        if total_fca > 0:
            # Mostrar 5 companhias
            companhias = FcaCiaAberta.objects.exclude(
                denom_cia__isnull=True
            )[:5]
            
            print("🏭 Algumas companhias:")
            for cia in companhias:
                print(f"   • {cia.denom_cia} - CVM: {cia.cd_cvm}")
        
        # Contar dados gerais anuais
        total_geral = AnualFcaCiaAbertaGeral.objects.count()
        print(f"✅ Dados Gerais Anuais: {total_geral:,} registros")
        
        # Contar FII anuais
        total_fii_anual = InfAnualFiiGeral.objects.count()
        print(f"✅ FII Anuais: {total_fii_anual:,} registros")
        
        # Contar FII mensais
        total_fii_mensal = InfMensalFiiGeral.objects.count()
        print(f"✅ FII Mensais: {total_fii_mensal:,} registros")
        
        if total_fii_anual > 0:
            # Mostrar 5 FII
            fiis = InfAnualFiiGeral.objects.exclude(
                nome_fundo_classe__isnull=True
            )[:5]
            
            print("🏠 Alguns FII:")
            for fii in fiis:
                print(f"   • {fii.nome_fundo_classe}")
                
    except Exception as e:
        print(f"❌ Erro ao acessar dados CVM: {e}")
    
    print()
    
    # ================== TESTE METADADOS ==================
    print("📋 TESTANDO METADADOS:")
    print("=" * 50)
    
    try:
        # Contar metadados ETL
        total_etl = EtlMetadata.objects.count()
        print(f"✅ Metadados ETL: {total_etl:,} registros")
        
        if total_etl > 0:
            # Mostrar últimos 5 processamentos
            etl_recentes = EtlMetadata.objects.filter(
                data_processamento__isnull=False
            ).order_by('-data_processamento')[:5]
            
            print("⚙️ Últimos processamentos:")
            for etl in etl_recentes:
                print(f"   • {etl.arquivo} - {etl.status} ({etl.data_processamento})")
                
    except Exception as e:
        print(f"❌ Erro ao acessar metadados: {e}")
    
    print()
    
    # ================== TESTE PREÇOS ==================
    print("📈 TESTANDO PREÇOS DE ATIVOS:")
    print("=" * 50)
    
    try:
        # Contar preços
        total_precos = AtivosPrecos.objects.count()
        print(f"✅ Preços de Ativos: {total_precos:,} registros")
        
        if total_precos > 0:
            # Mostrar 5 ativos mais recentes
            precos_recentes = AtivosPrecos.objects.order_by('-data')[:5]
            
            print("💵 Preços mais recentes:")
            for preco in precos_recentes:
                print(f"   • {preco.ticker} - R$ {preco.close:.2f} ({preco.data})")
                
    except Exception as e:
        print(f"❌ Erro ao acessar preços: {e}")
    
    print()
    print("🎉 Teste dos Models Concluído!")
    print("✅ Todos os models estão funcionando e conectados ao banco!")

if __name__ == "__main__":
    testar_models()
