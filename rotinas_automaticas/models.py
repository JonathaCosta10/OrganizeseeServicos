from django.db import models
from django.contrib.auth.models import User

# ================== TABELAS B3 ==================

class B3InstrumentsConsolidated(models.Model):
    """Tabela de instrumentos consolidados da B3"""
    tipreg = models.CharField(max_length=10, null=True, blank=True)
    datref = models.DateField(null=True, blank=True)
    codinst = models.CharField(max_length=50, null=True, blank=True)
    isin = models.CharField(max_length=20, null=True, blank=True)
    nomres = models.CharField(max_length=200, null=True, blank=True)
    nomcom = models.CharField(max_length=200, null=True, blank=True)
    tipmerc = models.CharField(max_length=10, null=True, blank=True)
    tpativo = models.CharField(max_length=10, null=True, blank=True)
    segmento = models.CharField(max_length=50, null=True, blank=True)
    mercado = models.CharField(max_length=50, null=True, blank=True)
    setativ = models.CharField(max_length=100, null=True, blank=True)
    classi = models.CharField(max_length=100, null=True, blank=True)
    codcfi = models.CharField(max_length=10, null=True, blank=True)
    dtini = models.DateField(null=True, blank=True)
    dtfim = models.DateField(null=True, blank=True)
    data_carga = models.DateTimeField(auto_now_add=True)
    fonte = models.CharField(max_length=20, default='B3')

    class Meta:
        db_table = 'b3_instruments_consolidated'
        verbose_name = 'B3 Instrumento Consolidado'
        verbose_name_plural = 'B3 Instrumentos Consolidados'

    def __str__(self):
        return f"{self.codinst} - {self.nomres}"


class B3TradeInformation(models.Model):
    """Tabela de informações de negociação da B3"""
    tipreg = models.CharField(max_length=10, null=True, blank=True)
    datref = models.DateField(null=True, blank=True)
    codinst = models.CharField(max_length=50, null=True, blank=True)
    nomres = models.CharField(max_length=200, null=True, blank=True)
    especi = models.CharField(max_length=100, null=True, blank=True)
    prazot = models.CharField(max_length=10, null=True, blank=True)
    modref = models.CharField(max_length=10, null=True, blank=True)
    preabe = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    premax = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    premin = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    premed = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preult = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preofc = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preofv = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    totneg = models.IntegerField(null=True, blank=True)
    quatot = models.BigIntegerField(null=True, blank=True)
    voltot = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    preexe = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    indopc = models.CharField(max_length=10, null=True, blank=True)
    datven = models.DateField(null=True, blank=True)
    fatcot = models.IntegerField(null=True, blank=True)
    ptoexe = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    codisi = models.CharField(max_length=20, null=True, blank=True)
    dismes = models.IntegerField(null=True, blank=True)
    data_carga = models.DateTimeField(auto_now_add=True)
    fonte = models.CharField(max_length=20, default='B3')

    class Meta:
        db_table = 'b3_trade_information'
        verbose_name = 'B3 Informação de Negociação'
        verbose_name_plural = 'B3 Informações de Negociação'

    def __str__(self):
        return f"{self.codinst} - {self.datref}"


# ================== TABELAS CVM - COMPANHIAS ==================

class FcaCiaAberta(models.Model):
    """Tabela FCA de Companhias Abertas da CVM"""
    cnpj_cia = models.TextField(null=True, blank=True)
    dt_refer = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    denom_cia = models.TextField(null=True, blank=True)
    cd_cvm = models.BigIntegerField(null=True, blank=True)
    categ_doc = models.TextField(null=True, blank=True)
    id_doc = models.BigIntegerField(null=True, blank=True)
    dt_receb = models.TextField(null=True, blank=True)
    link_doc = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_fca_cia_aberta'
        verbose_name = 'FCA Companhia Aberta'
        verbose_name_plural = 'FCA Companhias Abertas'

    def __str__(self):
        return f"{self.denom_cia} - {self.cd_cvm}"


class AnualFcaCiaAbertaGeral(models.Model):
    """Tabela de dados gerais anuais de companhias abertas"""
    cnpj_companhia = models.TextField(null=True, blank=True)
    data_referencia = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    id_documento = models.BigIntegerField(null=True, blank=True)
    nome_empresarial = models.TextField(null=True, blank=True)
    data_nome_empresarial = models.TextField(null=True, blank=True)
    nome_empresarial_anterior = models.TextField(null=True, blank=True)
    data_constituicao = models.TextField(null=True, blank=True)
    codigo_cvm = models.BigIntegerField(null=True, blank=True)
    data_registro_cvm = models.TextField(null=True, blank=True)
    categoria_registro_cvm = models.TextField(null=True, blank=True)
    data_categoria_registro_cvm = models.TextField(null=True, blank=True)
    situacao_registro_cvm = models.TextField(null=True, blank=True)
    data_situacao_registro_cvm = models.TextField(null=True, blank=True)
    pais_origem = models.TextField(null=True, blank=True)
    pais_custodia_valores_mobiliarios = models.TextField(null=True, blank=True)
    setor_atividade = models.TextField(null=True, blank=True)
    descricao_atividade = models.TextField(null=True, blank=True)
    situacao_emissor = models.TextField(null=True, blank=True)
    data_situacao_emissor = models.TextField(null=True, blank=True)
    especie_controle_acionario = models.TextField(null=True, blank=True)
    data_especie_controle_acionario = models.TextField(null=True, blank=True)
    dia_encerramento_exercicio_social = models.BigIntegerField(null=True, blank=True)
    mes_encerramento_exercicio_social = models.BigIntegerField(null=True, blank=True)
    data_alteracao_exercicio_social = models.TextField(null=True, blank=True)
    pagina_web = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_anual_fca_cia_aberta_geral'
        verbose_name = 'Dados Gerais Anuais - Companhia Aberta'
        verbose_name_plural = 'Dados Gerais Anuais - Companhias Abertas'

    def __str__(self):
        return f"{self.nome_empresarial} - {self.codigo_cvm}"


class AnualFcaCiaAbertaValorMobiliario(models.Model):
    """Tabela de valores mobiliários de companhias abertas"""
    cnpj_companhia = models.TextField(null=True, blank=True)
    data_referencia = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    id_documento = models.BigIntegerField(null=True, blank=True)
    nome_empresarial = models.TextField(null=True, blank=True)
    valor_mobiliario = models.TextField(null=True, blank=True)
    sigla_classe_acao_preferencial = models.TextField(null=True, blank=True)
    classe_acao_preferencial = models.TextField(null=True, blank=True)
    codigo_negociacao = models.TextField(null=True, blank=True)
    composicao_bdr_unit = models.TextField(null=True, blank=True)
    mercado = models.TextField(null=True, blank=True)
    sigla_entidade_administradora = models.TextField(null=True, blank=True)
    entidade_administradora = models.TextField(null=True, blank=True)
    data_inicio_negociacao = models.TextField(null=True, blank=True)
    data_fim_negociacao = models.TextField(null=True, blank=True)
    segmento = models.TextField(null=True, blank=True)
    data_inicio_listagem = models.TextField(null=True, blank=True)
    data_fim_listagem = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_anual_fca_cia_aberta_valor_mobiliario'
        verbose_name = 'Valor Mobiliário - Companhia Aberta'
        verbose_name_plural = 'Valores Mobiliários - Companhias Abertas'

    def __str__(self):
        return f"{self.nome_empresarial} - {self.codigo_negociacao}"


# ================== TABELAS CVM - FUNDOS IMOBILIÁRIOS ==================

class InfAnualFiiGeral(models.Model):
    """Tabela de informações anuais gerais de FII"""
    tipo_fundo_classe = models.TextField(null=True, blank=True)
    cnpj_fundo_classe = models.TextField(null=True, blank=True)
    data_referencia = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    data_entrega = models.TextField(null=True, blank=True)
    nome_fundo_classe = models.TextField(null=True, blank=True)
    data_funcionamento = models.TextField(null=True, blank=True)
    publico_alvo = models.TextField(null=True, blank=True)
    codigo_isin = models.TextField(null=True, blank=True)
    quantidade_cotas_emitidas = models.FloatField(null=True, blank=True)
    fundo_exclusivo = models.TextField(null=True, blank=True)
    cotistas_vinculo_familiar = models.TextField(null=True, blank=True)
    mandato = models.TextField(null=True, blank=True)
    segmento_atuacao = models.TextField(null=True, blank=True)
    tipo_gestao = models.TextField(null=True, blank=True)
    prazo_duracao = models.TextField(null=True, blank=True)
    data_prazo_duracao = models.TextField(null=True, blank=True)
    encerramento_exercicio_social = models.TextField(null=True, blank=True)
    mercado_negociacao_bolsa = models.TextField(null=True, blank=True)
    mercado_negociacao_mbo = models.TextField(null=True, blank=True)
    mercado_negociacao_mb = models.TextField(null=True, blank=True)
    entidade_administradora_bvmf = models.TextField(null=True, blank=True)
    entidade_administradora_cetip = models.TextField(null=True, blank=True)
    nome_administrador = models.TextField(null=True, blank=True)
    cnpj_administrador = models.TextField(null=True, blank=True)
    logradouro = models.TextField(null=True, blank=True)
    numero = models.TextField(null=True, blank=True)
    complemento = models.TextField(null=True, blank=True)
    bairro = models.TextField(null=True, blank=True)
    cidade = models.TextField(null=True, blank=True)
    estado = models.TextField(null=True, blank=True)
    cep = models.TextField(null=True, blank=True)
    telefone1 = models.TextField(null=True, blank=True)
    telefone2 = models.TextField(null=True, blank=True)
    telefone3 = models.TextField(null=True, blank=True)
    site = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_inf_anual_fii_geral'
        verbose_name = 'Informação Anual FII - Geral'
        verbose_name_plural = 'Informações Anuais FII - Geral'

    def __str__(self):
        return f"{self.nome_fundo_classe} - {self.cnpj_fundo_classe}"


class InfAnualFiiAtivoValorContabil(models.Model):
    """Tabela de ativos e valores contábeis anuais de FII"""
    cnpj_fundo_classe = models.TextField(null=True, blank=True)
    data_referencia = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    nome_ativo = models.TextField(null=True, blank=True)
    valor = models.FloatField(null=True, blank=True)
    valor_justo = models.TextField(null=True, blank=True)
    percentual_valorizacao_desvalorizacao = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_inf_anual_fii_ativo_valor_contabil'
        verbose_name = 'Informação Anual FII - Ativo Valor Contábil'
        verbose_name_plural = 'Informações Anuais FII - Ativos Valores Contábeis'

    def __str__(self):
        return f"{self.cnpj_fundo_classe} - {self.nome_ativo}"


class InfMensalFiiGeral(models.Model):
    """Tabela de informações mensais gerais de FII"""
    cnpj_fundo_classe = models.TextField(null=True, blank=True)
    data_referencia = models.DateTimeField(null=True, blank=True)
    tipo_fundo_classe = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    data_entrega = models.TextField(null=True, blank=True)
    nome_fundo_classe = models.TextField(null=True, blank=True)
    data_funcionamento = models.TextField(null=True, blank=True)
    publico_alvo = models.TextField(null=True, blank=True)
    codigo_isin = models.TextField(null=True, blank=True)
    quantidade_cotas_emitidas = models.FloatField(null=True, blank=True)
    fundo_exclusivo = models.TextField(null=True, blank=True)
    cotistas_vinculo_familiar = models.TextField(null=True, blank=True)
    mandato = models.TextField(null=True, blank=True)
    segmento_atuacao = models.TextField(null=True, blank=True)
    tipo_gestao = models.TextField(null=True, blank=True)
    prazo_duracao = models.TextField(null=True, blank=True)
    data_prazo_duracao = models.TextField(null=True, blank=True)
    encerramento_exercicio_social = models.TextField(null=True, blank=True)
    mercado_negociacao_bolsa = models.TextField(null=True, blank=True)
    mercado_negociacao_mbo = models.TextField(null=True, blank=True)
    mercado_negociacao_mb = models.TextField(null=True, blank=True)
    entidade_administradora_bvmf = models.TextField(null=True, blank=True)
    entidade_administradora_cetip = models.TextField(null=True, blank=True)
    nome_administrador = models.TextField(null=True, blank=True)
    cnpj_administrador = models.FloatField(null=True, blank=True)
    logradouro = models.TextField(null=True, blank=True)
    numero = models.TextField(null=True, blank=True)
    complemento = models.TextField(null=True, blank=True)
    bairro = models.TextField(null=True, blank=True)
    cidade = models.TextField(null=True, blank=True)
    estado = models.TextField(null=True, blank=True)
    cep = models.TextField(null=True, blank=True)
    telefone1 = models.TextField(null=True, blank=True)
    telefone2 = models.TextField(null=True, blank=True)
    telefone3 = models.TextField(null=True, blank=True)
    site = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_inf_mensal_fii_geral'
        verbose_name = 'Informação Mensal FII - Geral'
        verbose_name_plural = 'Informações Mensais FII - Geral'

    def __str__(self):
        return f"{self.nome_fundo_classe} - {self.data_referencia}"


class InfMensalFiiAtivoPassivo(models.Model):
    """Tabela de ativo e passivo mensais de FII"""
    cnpj_fundo_classe = models.TextField(null=True, blank=True)
    data_referencia = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    total_necessidades_liquidez = models.FloatField(null=True, blank=True)
    disponibilidades = models.FloatField(null=True, blank=True)
    titulos_publicos = models.FloatField(null=True, blank=True)
    titulos_privados = models.FloatField(null=True, blank=True)
    fundos_renda_fixa = models.FloatField(null=True, blank=True)
    total_investido = models.FloatField(null=True, blank=True)
    direitos_bens_imoveis = models.FloatField(null=True, blank=True)
    terrenos = models.FloatField(null=True, blank=True)
    imoveis_renda_acabados = models.FloatField(null=True, blank=True)
    imoveis_renda_construcao = models.FloatField(null=True, blank=True)
    imoveis_venda_acabados = models.FloatField(null=True, blank=True)
    imoveis_venda_construcao = models.FloatField(null=True, blank=True)
    outros_direitos_reais = models.FloatField(null=True, blank=True)
    acoes = models.FloatField(null=True, blank=True)
    debentures = models.FloatField(null=True, blank=True)
    bonus_subscricao = models.FloatField(null=True, blank=True)
    certificados_deposito_valores_mobiliarios = models.FloatField(null=True, blank=True)
    cedulas_debentures = models.FloatField(null=True, blank=True)
    fundo_acoes = models.FloatField(null=True, blank=True)
    fip = models.FloatField(null=True, blank=True)
    fii = models.FloatField(null=True, blank=True)
    fdic = models.FloatField(null=True, blank=True)
    outras_cotas_fi = models.FloatField(null=True, blank=True)
    notas_promissorias = models.FloatField(null=True, blank=True)
    acoes_sociedades_atividades_fii = models.FloatField(null=True, blank=True)
    cotas_sociedades_atividades_fii = models.FloatField(null=True, blank=True)
    cepac = models.FloatField(null=True, blank=True)
    cri = models.FloatField(null=True, blank=True)
    cri_cra = models.FloatField(null=True, blank=True)
    letras_hipotecarias = models.FloatField(null=True, blank=True)
    lci = models.FloatField(null=True, blank=True)
    lci_lca = models.FloatField(null=True, blank=True)
    lig = models.FloatField(null=True, blank=True)
    outros_valores_mobliarios = models.FloatField(null=True, blank=True)
    valores_receber = models.FloatField(null=True, blank=True)
    contas_receber_aluguel = models.FloatField(null=True, blank=True)
    contas_receber_venda_imoveis = models.FloatField(null=True, blank=True)
    outros_valores_receber = models.FloatField(null=True, blank=True)
    rendimentos_distribuir = models.FloatField(null=True, blank=True)
    taxa_administracao_pagar = models.FloatField(null=True, blank=True)
    taxa_performance_pagar = models.FloatField(null=True, blank=True)
    obrigacoes_aquisicao_imoveis = models.FloatField(null=True, blank=True)
    adiantamento_venda_imoveis = models.FloatField(null=True, blank=True)
    adiantamento_alugueis = models.FloatField(null=True, blank=True)
    obrigacoes_securitizacao_recebiveis = models.FloatField(null=True, blank=True)
    instrumentos_financeiros_derivativos = models.FloatField(null=True, blank=True)
    provisoes_contigencias = models.FloatField(null=True, blank=True)
    outros_valores_pagar = models.FloatField(null=True, blank=True)
    total_passivo = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_inf_mensal_fii_ativo_passivo'
        verbose_name = 'Informação Mensal FII - Ativo/Passivo'
        verbose_name_plural = 'Informações Mensais FII - Ativo/Passivo'

    def __str__(self):
        return f"{self.cnpj_fundo_classe} - {self.data_referencia}"


class InfMensalFiiComplemento(models.Model):
    """Tabela de informações complementares mensais de FII"""
    cnpj_fundo_classe = models.TextField(null=True, blank=True)
    data_referencia = models.TextField(null=True, blank=True)
    versao = models.BigIntegerField(null=True, blank=True)
    data_informacao_numero_cotistas = models.TextField(null=True, blank=True)
    total_numero_cotistas = models.FloatField(null=True, blank=True)
    numero_cotistas_pessoa_fisica = models.FloatField(null=True, blank=True)
    numero_cotistas_pessoa_juridica_nao_financeira = models.FloatField(null=True, blank=True)
    numero_cotistas_banco_comercial = models.FloatField(null=True, blank=True)
    numero_cotistas_corretora_distribuidora = models.FloatField(null=True, blank=True)
    numero_cotistas_outras_pessoas_juridicas_financeira = models.FloatField(null=True, blank=True)
    numero_cotistas_investidores_nao_residentes = models.FloatField(null=True, blank=True)
    numero_cotistas_entidade_aberta_previdencia_complementar = models.FloatField(null=True, blank=True)
    numero_cotistas_entidade_fechada_previdencia_complementar = models.FloatField(null=True, blank=True)
    numero_cotistas_regime_proprio_previdencia_servidores_publicos = models.FloatField(null=True, blank=True)
    numero_cotistas_sociedade_seguradora_resseguradora = models.FloatField(null=True, blank=True)
    numero_cotistas_sociedade_capitalizacao_arrendamento_mercantil = models.FloatField(null=True, blank=True)
    numero_cotistas_fii = models.FloatField(null=True, blank=True)
    numero_cotistas_outros_fundos = models.FloatField(null=True, blank=True)
    numero_cotistas_distribuidores_fundo = models.FloatField(null=True, blank=True)
    numero_cotistas_outros_tipos = models.FloatField(null=True, blank=True)
    valor_ativo = models.FloatField(null=True, blank=True)
    patrimonio_liquido = models.FloatField(null=True, blank=True)
    cotas_emitidas = models.FloatField(null=True, blank=True)
    valor_patrimonial_cotas = models.FloatField(null=True, blank=True)
    percentual_despesas_taxa_administracao = models.FloatField(null=True, blank=True)
    percentual_despesas_agente_custodiante = models.FloatField(null=True, blank=True)
    percentual_rentabilidade_efetiva_mes = models.FloatField(null=True, blank=True)
    percentual_rentabilidade_patrimonial_mes = models.FloatField(null=True, blank=True)
    percentual_dividend_yield_mes = models.FloatField(null=True, blank=True)
    percentual_amortizacao_cotas_mes = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'rotinas_automaticas_inf_mensal_fii_complemento'
        verbose_name = 'Informação Mensal FII - Complemento'
        verbose_name_plural = 'Informações Mensais FII - Complemento'

    def __str__(self):
        return f"{self.cnpj_fundo_classe} - {self.data_referencia}"


# ================== TABELAS DE CONTROLE E METADADOS ==================

class EtlMetadata(models.Model):
    """Tabela de metadados dos processos ETL"""
    arquivo = models.CharField(max_length=255, null=True, blank=True)
    tipo_processamento = models.CharField(max_length=50, null=True, blank=True)
    registros_processados = models.IntegerField(null=True, blank=True)
    data_processamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'etl_metadata'
        verbose_name = 'Metadados ETL'
        verbose_name_plural = 'Metadados ETL'

    def __str__(self):
        return f"{self.arquivo} - {self.status}"


class ProcessingMetadata(models.Model):
    """Tabela de metadados de processamento"""
    arquivo_origem = models.CharField(max_length=255)
    arquivo_destino = models.CharField(max_length=255, null=True, blank=True)
    tabela_destino = models.CharField(max_length=255, null=True, blank=True)
    total_linhas = models.IntegerField(null=True, blank=True)
    total_colunas = models.IntegerField(null=True, blank=True)
    tamanho_arquivo_mb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_processamento = models.DateTimeField(auto_now_add=True)
    status_processamento = models.CharField(max_length=50, null=True, blank=True)
    tempo_processamento_segundos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    colunas_identificadas = models.JSONField(null=True, blank=True)
    sample_data = models.JSONField(null=True, blank=True)
    chaves_primarias = models.JSONField(null=True, blank=True)
    registros_validos = models.IntegerField(null=True, blank=True)
    registros_invalidos = models.IntegerField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'organizesee_processing_metadata'
        verbose_name = 'Metadados de Processamento'
        verbose_name_plural = 'Metadados de Processamento'

    def __str__(self):
        return f"{self.arquivo_origem} - {self.status_processamento}"


# ================== TABELAS ORGANIZESEE ==================

class DadosPessoais(models.Model):
    """Tabela de dados pessoais dos usuários"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11)
    email = models.EmailField()
    endereco = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=20, null=True, blank=True)
    profissao = models.CharField(max_length=100, null=True, blank=True)
    renda_mensal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    objetivos_financeiros = models.TextField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizesee_dadospessoais'
        verbose_name = 'Dados Pessoais'
        verbose_name_plural = 'Dados Pessoais'

    def __str__(self):
        return f"{self.nome_completo} - {self.cpf}"


class AtivosPrecos(models.Model):
    """Tabela de preços de ativos"""
    tipo = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10)
    close = models.DecimalField(max_digits=15, decimal_places=2)
    open = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    high = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    low = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    volume = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    data = models.DateField()
    fonte = models.CharField(max_length=10)

    class Meta:
        db_table = 'organizesee_ativosprecos'
        verbose_name = 'Preços de Ativos'
        verbose_name_plural = 'Preços de Ativos'

    def __str__(self):
        return f"{self.ticker} - {self.data} - {self.close}"


class AtivosPessoais(models.Model):
    """Tabela de ativos pessoais dos usuários"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=20)
    tipo = models.CharField(max_length=100)
    quantidade = models.DecimalField(max_digits=15, decimal_places=8)
    preco_medio = models.DecimalField(max_digits=15, decimal_places=2)
    data_compra = models.DateField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizesee_ativospessoais'
        verbose_name = 'Ativos Pessoais'
        verbose_name_plural = 'Ativos Pessoais'

    def __str__(self):
        return f"{self.user.username} - {self.ticker} - {self.quantidade}"


# ================== TABELAS PREÇOS DE ATIVOS ==================

class AtivosPrecosBruto(models.Model):
    """Tabela de preços de ativos (versão bruta)"""
    codigo_ativo = models.CharField(max_length=50, null=True, blank=True)
    data_referencia = models.DateField(null=True, blank=True)
    preco_abertura = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preco_maximo = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preco_minimo = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preco_medio = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preco_ultimo = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preco_oferta_compra = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preco_oferta_venda = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    volume_total = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    quantidade_total = models.BigIntegerField(null=True, blank=True)
    numero_negocios = models.IntegerField(null=True, blank=True)
    fonte = models.CharField(max_length=20, default='B3')
    data_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ativosprecos'
        verbose_name = 'Preços de Ativos (Bruto)'
        verbose_name_plural = 'Preços de Ativos (Bruto)'

    def __str__(self):
        return f"{self.codigo_ativo} - {self.data_referencia}"


# ================== TABELAS ORÇAMENTO DOMÉSTICO ==================

class OrcamentoDomesticoDividas(models.Model):
    """Tabela de dívidas do orçamento doméstico"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=20)
    descricao = models.CharField(max_length=255)
    valor_mensal = models.DecimalField(max_digits=15, decimal_places=2)
    quantidade_parcelas = models.IntegerField()
    taxa_juros = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    valor_hoje = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    divida_total = models.DecimalField(max_digits=15, decimal_places=2)
    juros_mensais = models.DecimalField(max_digits=15, decimal_places=2)
    flag = models.BooleanField()
    data_cadastro = models.DateTimeField()
    mes = models.IntegerField()
    ano = models.IntegerField()

    class Meta:
        db_table = 'orcamentoDomestico_Dividas'
        verbose_name = 'Dívida - Orçamento Doméstico'
        verbose_name_plural = 'Dívidas - Orçamento Doméstico'

    def __str__(self):
        return f"{self.user.username} - {self.descricao} - {self.valor_mensal}"


class OrcamentoDomesticoEntradas(models.Model):
    """Tabela de entradas do orçamento doméstico"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=20)
    descricao = models.CharField(max_length=255)
    valor_mensal = models.DecimalField(max_digits=15, decimal_places=2)
    flag = models.BooleanField()
    data_cadastro = models.DateTimeField()
    mes = models.IntegerField()
    ano = models.IntegerField()

    class Meta:
        db_table = 'orcamentoDomestico_Entradas'
        verbose_name = 'Entrada - Orçamento Doméstico'
        verbose_name_plural = 'Entradas - Orçamento Doméstico'

    def __str__(self):
        return f"{self.user.username} - {self.descricao} - {self.valor_mensal}"


class OrcamentoDomesticoGastos(models.Model):
    """Tabela de gastos do orçamento doméstico"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=20)
    descricao = models.CharField(max_length=255)
    valor_mensal = models.DecimalField(max_digits=15, decimal_places=2)
    flag = models.BooleanField()
    data_cadastro = models.DateTimeField()
    mes = models.IntegerField()
    ano = models.IntegerField()

    class Meta:
        db_table = 'orcamentoDomestico_Gastos'
        verbose_name = 'Gasto - Orçamento Doméstico'
        verbose_name_plural = 'Gastos - Orçamento Doméstico'

    def __str__(self):
        return f"{self.user.username} - {self.descricao} - {self.valor_mensal}"


class OrcamentoDomesticoMetasPersonalizadas(models.Model):
    """Tabela de metas personalizadas do orçamento doméstico"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo_da_meta = models.CharField(max_length=255)
    descricao = models.TextField(null=True, blank=True)
    valor_hoje = models.DecimalField(max_digits=15, decimal_places=2)
    valor_alvo = models.DecimalField(max_digits=15, decimal_places=2)
    data_limite = models.DateField()
    categoria = models.CharField(max_length=100)
    data_cadastro = models.DateTimeField()

    class Meta:
        db_table = 'orcamentoDomestico_MetasPersonalizadas'
        verbose_name = 'Meta Personalizada - Orçamento Doméstico'
        verbose_name_plural = 'Metas Personalizadas - Orçamento Doméstico'

    def __str__(self):
        return f"{self.user.username} - {self.titulo_da_meta}"


class OrcamentoDomestico(models.Model):
    """Tabela principal do orçamento doméstico"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    custos_fixos = models.DecimalField(max_digits=15, decimal_places=2)
    prazer = models.DecimalField(max_digits=15, decimal_places=2)
    conforto = models.DecimalField(max_digits=15, decimal_places=2)
    metas = models.DecimalField(max_digits=15, decimal_places=2)
    liberdade_financeira = models.DecimalField(max_digits=15, decimal_places=2)
    conhecimento = models.DecimalField(max_digits=15, decimal_places=2)
    data = models.DateTimeField()

    class Meta:
        db_table = 'organizesee_orcamentodomestico'
        verbose_name = 'Orçamento Doméstico'
        verbose_name_plural = 'Orçamentos Domésticos'

    def __str__(self):
        return f"{self.user.username} - {self.data}"


# ================== TABELAS DE USUÁRIO ==================

class UserProfile(models.Model):
    """Tabela de perfil dos usuários"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_paid_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    google_email = models.EmailField(null=True, blank=True)
    google_first_login = models.DateTimeField(null=True, blank=True)
    google_id = models.CharField(max_length=255, null=True, blank=True)
    google_last_login = models.DateTimeField(null=True, blank=True)
    google_name = models.CharField(max_length=255, null=True, blank=True)
    google_picture = models.CharField(max_length=200, null=True, blank=True)
    google_verified_email = models.BooleanField(default=False)
    is_google_account = models.BooleanField(default=False)

    class Meta:
        db_table = 'organizesee_userprofile'
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f"{self.user.username} - {'Pago' if self.is_paid_user else 'Gratuito'}"


class PasswordResetToken(models.Model):
    """Tabela de tokens para redefinição de senha"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=8)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'organizesee_passwordresettoken'
        verbose_name = 'Token de Redefinição de Senha'
        verbose_name_plural = 'Tokens de Redefinição de Senha'

    def __str__(self):
        return f"{self.email} - {self.code} - {'Usado' if self.is_used else 'Válido'}"


# ================== TABELAS ESPECÍFICAS DE CVM E B3 ==================

class CompanhiaAberta(models.Model):
    """Tabela de companhias abertas"""
    cnpj = models.CharField(max_length=20)
    denominacao_social = models.CharField(max_length=200)
    denominacao_comercial = models.CharField(max_length=200)
    setor_atividade = models.CharField(max_length=100)
    classificacao_setor = models.CharField(max_length=100)
    situacao = models.CharField(max_length=50)
    data_registro = models.DateField(null=True, blank=True)
    data_referencia = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_companhiaaberta'
        verbose_name = 'Companhia Aberta'
        verbose_name_plural = 'Companhias Abertas'

    def __str__(self):
        return f"{self.denominacao_social} - {self.cnpj}"


class CanalDivulgacaoCompanhia(models.Model):
    """Tabela de canais de divulgação das companhias"""
    cnpj_companhia = models.CharField(max_length=20)
    denominacao_social = models.CharField(max_length=200)
    endereco_canal = models.CharField(max_length=500)
    tipo_canal = models.CharField(max_length=100)
    data_referencia = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_canaldivulgacaocompanhia'
        verbose_name = 'Canal de Divulgação'
        verbose_name_plural = 'Canais de Divulgação'

    def __str__(self):
        return f"{self.denominacao_social} - {self.tipo_canal}"


class ValorMobiliarioCompanhia(models.Model):
    """Tabela de valores mobiliários das companhias"""
    cnpj_companhia = models.CharField(max_length=20)
    denominacao_social = models.CharField(max_length=200)
    cod_cvm = models.CharField(max_length=20)
    tipo_valor_mobiliario = models.CharField(max_length=100)
    mercado = models.CharField(max_length=50)
    segmento = models.CharField(max_length=100)
    data_referencia = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_valormobiliariocompanhia'
        verbose_name = 'Valor Mobiliário da Companhia'
        verbose_name_plural = 'Valores Mobiliários das Companhias'

    def __str__(self):
        return f"{self.denominacao_social} - {self.tipo_valor_mobiliario}"


class CvmGeralFii(models.Model):
    """Tabela geral de FII da CVM"""
    cnpj_fundo = models.CharField(max_length=20)
    denominacao_social = models.CharField(max_length=200)
    tipo_fundo = models.CharField(max_length=100)
    segmento_atuacao = models.CharField(max_length=100)
    administrador = models.CharField(max_length=200)
    gestor = models.CharField(max_length=200)
    situacao = models.CharField(max_length=50)
    data_registro = models.DateField(null=True, blank=True)
    data_referencia = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_cvmgeralfii'
        verbose_name = 'CVM Geral FII'
        verbose_name_plural = 'CVM Geral FII'

    def __str__(self):
        return f"{self.denominacao_social} - {self.cnpj_fundo}"


class FundoListadoB3(models.Model):
    """Tabela de fundos listados na B3"""
    codigo = models.CharField(max_length=20)
    razao_social = models.CharField(max_length=300)
    cnpj = models.CharField(max_length=14)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_fundolistadob3'
        verbose_name = 'Fundo Listado B3'
        verbose_name_plural = 'Fundos Listados B3'

    def __str__(self):
        return f"{self.codigo} - {self.razao_social}"


# ================== TABELAS DE CONTROLE DE ROTINAS ==================

class TipoRotina(models.Model):
    """Tabela de tipos de rotinas"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    icone = models.CharField(max_length=50)
    cor = models.CharField(max_length=7)  # Código hex da cor
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'rotinas_automaticas_tiporotina'
        verbose_name = 'Tipo de Rotina'
        verbose_name_plural = 'Tipos de Rotinas'

    def __str__(self):
        return self.nome


class StatusExecucao(models.Model):
    """Tabela de status de execução"""
    nome = models.CharField(max_length=20)
    descricao = models.CharField(max_length=255)
    icone = models.CharField(max_length=10)
    cor = models.CharField(max_length=7)  # Código hex da cor

    class Meta:
        db_table = 'rotinas_automaticas_statusexecucao'
        verbose_name = 'Status de Execução'
        verbose_name_plural = 'Status de Execuções'

    def __str__(self):
        return self.nome


class RotinaDefinicao(models.Model):
    """Tabela de definições de rotinas"""
    nome = models.CharField(max_length=100)
    nome_exibicao = models.CharField(max_length=150)
    descricao = models.TextField()
    comando_management = models.CharField(max_length=200)
    argumentos_padrao = models.CharField(max_length=500)
    periodo_cron = models.CharField(max_length=50)
    fuso_horario = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)
    executar_no_inicio = models.BooleanField(default=False)
    timeout_segundos = models.IntegerField(default=3600)
    max_tentativas = models.IntegerField(default=3)
    delay_entre_tentativas = models.IntegerField(default=60)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_rotina = models.ForeignKey(TipoRotina, on_delete=models.CASCADE)

    class Meta:
        db_table = 'rotinas_automaticas_rotinadefinicao'
        verbose_name = 'Definição de Rotina'
        verbose_name_plural = 'Definições de Rotinas'

    def __str__(self):
        return f"{self.nome_exibicao} - {'Ativo' if self.ativo else 'Inativo'}"


class ControleRotina(models.Model):
    """Tabela de controle de rotinas"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    ativo = models.BooleanField(default=True)
    hora_execucao = models.TimeField()
    periodo = models.CharField(max_length=50)
    executar_inicio = models.BooleanField(default=False)
    ultima_execucao = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_controlerotina'
        verbose_name = 'Controle de Rotina'
        verbose_name_plural = 'Controles de Rotinas'

    def __str__(self):
        return f"{self.nome} - {'Ativo' if self.ativo else 'Inativo'}"


class HistoricoExecucao(models.Model):
    """Tabela de histórico de execuções"""
    rotina = models.ForeignKey(ControleRotina, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    iniciado_em = models.DateTimeField()
    finalizado_em = models.DateTimeField(null=True, blank=True)
    duracao_segundos = models.IntegerField(null=True, blank=True)
    saida_stdout = models.TextField(default='')
    saida_stderr = models.TextField(default='')
    codigo_retorno = models.IntegerField(null=True, blank=True)
    argumentos_executados = models.CharField(max_length=500, default='')
    ambiente = models.CharField(max_length=50, default='')
    servidor = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'rotinas_automaticas_historicoexecucao'
        verbose_name = 'Histórico de Execução'
        verbose_name_plural = 'Históricos de Execuções'

    def __str__(self):
        return f"{self.rotina.nome} - {self.status} - {self.iniciado_em}"


class MonitorRotina(models.Model):
    """Tabela de monitoramento de rotinas"""
    rotina = models.OneToOneField(ControleRotina, on_delete=models.CASCADE)
    status_atual = models.CharField(max_length=20)
    ultima_execucao = models.DateTimeField(null=True, blank=True)
    proxima_execucao = models.DateTimeField(null=True, blank=True)
    total_execucoes = models.IntegerField(default=0)
    execucoes_sucesso = models.IntegerField(default=0)
    execucoes_erro = models.IntegerField(default=0)
    duracao_media = models.FloatField(null=True, blank=True)
    duracao_ultima = models.IntegerField(null=True, blank=True)
    alertas_ativo = models.BooleanField(default=False)
    max_duracao_alerta = models.IntegerField(null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_monitorrotina'
        verbose_name = 'Monitor de Rotina'
        verbose_name_plural = 'Monitores de Rotinas'

    def __str__(self):
        return f"{self.rotina.nome} - {self.status_atual}"


class RegistroExecucao(models.Model):
    """Tabela de registro de execução de rotinas"""
    
    STATUS_CHOICES = [
        ('AGUARDANDO', 'Aguardando execução'),
        ('AGENDADA', 'Agendada para executar'),
        ('EXECUTANDO', 'Executando'),
        ('CONCLUIDA', 'Concluída com sucesso'),
        ('ERRO', 'Erro'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    SISTEMA_CHOICES = [
        ('B3', 'B3'),
        ('CVM', 'CVM'),
        ('MANUAIS', 'Manuais'),
        ('IBGE', 'IBGE'),
    ]
    
    GRUPO_CHOICES = [
        ('DIARIO', 'Diário'),
        ('EVENTUAL', 'Eventual'),
        ('MENSAL', 'Mensal'),
        ('ANUAL', 'Anual'),
    ]

    # Identificação da rotina
    job_arquivo_processo = models.CharField(max_length=255, help_text="Nome do job/arquivo/processo")
    tabela_destino = models.CharField(max_length=255, help_text="Tabela destino dos dados carregados")
    
    # Contadores de registros
    registros_totais_novos = models.IntegerField(default=0, help_text="Quantidade de registros novos inseridos")
    quantidade_linhas_arquivo = models.IntegerField(default=0, help_text="Quantidade de linhas do arquivo processado")
    registros_totais_arquivo = models.IntegerField(default=0, help_text="Total de registros válidos no arquivo")
    registros_totais_atualizados = models.IntegerField(default=0, help_text="Quantidade de registros atualizados")
    registros_totais_ignorados = models.IntegerField(default=0, help_text="Quantidade de registros ignorados")
    
    # Controle de execução
    status_execucao = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGUARDANDO')
    dia_horario_execucao = models.DateTimeField(auto_now_add=True, help_text="Data e hora de início da execução")
    dia_horario_finalizacao = models.DateTimeField(null=True, blank=True, help_text="Data e hora de finalização")
    
    # Classificação
    sistema = models.CharField(max_length=20, choices=SISTEMA_CHOICES, help_text="Sistema origem dos dados")
    grupo = models.CharField(max_length=20, choices=GRUPO_CHOICES, help_text="Grupo de execução")
    
    # Agendamento
    proxima_execucao = models.DateTimeField(null=True, blank=True, help_text="Próxima execução agendada")
    
    # Log e observações
    arquivo_log = models.TextField(null=True, blank=True, help_text="Caminho do arquivo de log gerado")
    observacoes = models.TextField(null=True, blank=True, help_text="Observações sobre a execução")
    erro_detalhes = models.TextField(null=True, blank=True, help_text="Detalhes do erro (se houver)")
    
    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rotinas_automaticas_registro_execucao'
        verbose_name = 'Registro de Execução'
        verbose_name_plural = 'Registros de Execução'
        ordering = ['-dia_horario_execucao']

    def __str__(self):
        return f"{self.job_arquivo_processo} - {self.status_execucao} - {self.dia_horario_execucao}"
    
    @property
    def duracao_execucao(self):
        """Calcula a duração da execução em segundos"""
        if self.dia_horario_finalizacao and self.dia_horario_execucao:
            delta = self.dia_horario_finalizacao - self.dia_horario_execucao
            return delta.total_seconds()
        return None


# ================== TABELAS SCHEDULER AVANÇADO ==================

class GrupoDiasExecucao(models.Model):
    """Tabela de grupos de dias para execução"""
    
    GRUPOS_CHOICES = [
        ('DIARIO', 'Diário (Segunda a Domingo)'),
        ('DIAS_SEMANA', 'Dias de Semana (Segunda a Sexta)'),
        ('FINAL_SEMANA', 'Final de Semana (Sábado e Domingo)'),
        ('D_MAIS_1', 'D+1 (Terça a Sábado)'),
        ('PERSONALIZADO', 'Personalizado'),
    ]
    
    nome = models.CharField(max_length=50, choices=GRUPOS_CHOICES, unique=True)
    descricao = models.CharField(max_length=200)
    segunda = models.BooleanField(default=False)
    terca = models.BooleanField(default=False)
    quarta = models.BooleanField(default=False)
    quinta = models.BooleanField(default=False)
    sexta = models.BooleanField(default=False)
    sabado = models.BooleanField(default=False)
    domingo = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rotinas_automaticas_grupodiasexecucao'
        verbose_name = 'Grupo de Dias de Execução'
        verbose_name_plural = 'Grupos de Dias de Execução'
    
    def __str__(self):
        return f"{self.get_nome_display()}"
    
    def dias_da_semana_ativados(self):
        """Retorna lista de dias da semana ativados (0=Segunda, 6=Domingo)"""
        dias = []
        if self.segunda: dias.append(0)
        if self.terca: dias.append(1)
        if self.quarta: dias.append(2)
        if self.quinta: dias.append(3)
        if self.sexta: dias.append(4)
        if self.sabado: dias.append(5)
        if self.domingo: dias.append(6)
        return dias


class SchedulerRotina(models.Model):
    """Tabela principal do scheduler - extensão da RotinaDefinicao"""
    
    TIPO_EXECUCAO_CHOICES = [
        ('DIARIO', 'Diário'),
        ('MENSAL', 'Mensal'),
        ('EVENTUAL', 'Eventual'),
        ('CICLICO', 'Cíclico'),
    ]
    
    TIPO_ROTINA_CHOICES = [
        ('CARGA_ARQUIVO', 'Carga de Arquivo'),
        ('DOWNLOAD_ARQUIVO', 'Download de Arquivo'),
        ('EXECUCAO_SCRIPT', 'Execução de Script'),
        ('CHAMADA_API', 'Chamada API'),
        ('COMANDO_SISTEMA', 'Comando do Sistema'),
    ]
    
    # Relacionamento com a definição original
    rotina_definicao = models.OneToOneField(RotinaDefinicao, on_delete=models.CASCADE, related_name='scheduler')
    
    # Configurações de execução
    tipo_execucao = models.CharField(max_length=20, choices=TIPO_EXECUCAO_CHOICES, default='DIARIO')
    tipo_rotina = models.CharField(max_length=20, choices=TIPO_ROTINA_CHOICES, default='CARGA_ARQUIVO')
    grupo_dias = models.ForeignKey(GrupoDiasExecucao, on_delete=models.CASCADE, null=True, blank=True)
    
    # Configurações cíclicas
    ciclico = models.BooleanField(default=False, help_text="Executa a cada X horas")
    intervalo_horas = models.IntegerField(default=1, help_text="Intervalo em horas para execução cíclica")
    
    # Configurações de execução
    executar = models.BooleanField(default=True, help_text="Deve ser executada")
    horario_execucao = models.TimeField(help_text="Horário de execução (formato HH:MM)")
    
    # Configurações de API/Endpoint
    endpoint_url = models.CharField(max_length=500, null=True, blank=True, help_text="URL do endpoint para chamada")
    metodo_http = models.CharField(max_length=10, default='POST', choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT')])
    payload_json = models.TextField(null=True, blank=True, help_text="JSON do payload para envio")
    headers_json = models.TextField(null=True, blank=True, help_text="Headers HTTP em JSON")
    
    # Configurações de arquivo
    mascara_arquivo = models.CharField(max_length=200, null=True, blank=True, help_text="Máscara do arquivo (ex: TradeInfo*20250910*.csv)")
    pasta_origem = models.CharField(max_length=500, null=True, blank=True, help_text="Pasta de origem dos arquivos")
    
    # Controle de recovery e resilência
    permite_recovery = models.BooleanField(default=True, help_text="Permite recuperação em caso de falha")
    max_tentativas_recovery = models.IntegerField(default=3, help_text="Máximo de tentativas de recuperação")
    delay_recovery_minutos = models.IntegerField(default=5, help_text="Delay entre tentativas de recovery (minutos)")
    
    # Prioridade na fila
    prioridade = models.IntegerField(default=50, help_text="Prioridade na fila (menor número = maior prioridade)")
    
    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'rotinas_automaticas_schedulerrotina'
        verbose_name = 'Scheduler de Rotina'
        verbose_name_plural = 'Scheduler de Rotinas'
        ordering = ['prioridade', 'horario_execucao']
    
    def __str__(self):
        return f"{self.rotina_definicao.nome_exibicao} - {self.get_tipo_execucao_display()}"


class FilaExecucao(models.Model):
    """Tabela de fila de execução - controla o que deve ser executado"""
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EXECUTANDO', 'Executando'),
        ('CONCLUIDA', 'Concluída'),
        ('ERRO', 'Erro'),
        ('CANCELADA', 'Cancelada'),
        ('RECOVERY', 'Em Recovery'),
    ]
    
    # Identificação
    scheduler_rotina = models.ForeignKey(SchedulerRotina, on_delete=models.CASCADE)
    data_execucao = models.DateField(help_text="Data planejada para execução")
    horario_execucao = models.TimeField(help_text="Horário planejado para execução")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    prioridade = models.IntegerField(help_text="Prioridade na fila (copiado do scheduler)")
    
    # Execução
    iniciado_em = models.DateTimeField(null=True, blank=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    duracao_segundos = models.IntegerField(null=True, blank=True)
    
    # Recovery e tentativas
    tentativa_atual = models.IntegerField(default=1)
    max_tentativas = models.IntegerField(default=3)
    ultima_tentativa_em = models.DateTimeField(null=True, blank=True)
    
    # Resultado da execução
    codigo_retorno = models.IntegerField(null=True, blank=True)
    saida_stdout = models.TextField(null=True, blank=True)
    saida_stderr = models.TextField(null=True, blank=True)
    erro_detalhes = models.TextField(null=True, blank=True)
    
    # Dados específicos da execução
    arquivo_processado = models.CharField(max_length=500, null=True, blank=True)
    registros_processados = models.IntegerField(null=True, blank=True)
    
    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rotinas_automaticas_filaexecucao'
        verbose_name = 'Fila de Execução'
        verbose_name_plural = 'Fila de Execução'
        ordering = ['data_execucao', 'horario_execucao', 'prioridade']
        unique_together = ['scheduler_rotina', 'data_execucao', 'horario_execucao']
    
    def __str__(self):
        return f"{self.scheduler_rotina.rotina_definicao.nome_exibicao} - {self.data_execucao} {self.horario_execucao}"
    
    @property
    def duracao_formatada(self):
        """Retorna duração formatada"""
        if self.duracao_segundos:
            horas = self.duracao_segundos // 3600
            minutos = (self.duracao_segundos % 3600) // 60
            segundos = self.duracao_segundos % 60
            return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        return None


class CargaDiariaRotinas(models.Model):
    """Tabela de controle da carga diária de rotinas"""
    
    STATUS_CHOICES = [
        ('INICIADA', 'Iniciada'),
        ('CONCLUIDA', 'Concluída'),
        ('ERRO', 'Erro'),
        ('CANCELADA', 'Cancelada'),
        ('SUBSTITUIDA', 'Substituída'),
    ]
    
    data_carga = models.DateField(unique=True, help_text="Data da carga diária")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INICIADA')
    
    # Estatísticas
    total_rotinas_processadas = models.IntegerField(default=0)
    total_rotinas_adicionadas_fila = models.IntegerField(default=0)
    total_rotinas_ignoradas = models.IntegerField(default=0)
    
    # Execução
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    duracao_segundos = models.IntegerField(null=True, blank=True)
    
    # Log e observações
    arquivo_log = models.CharField(max_length=500, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    erro_detalhes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'rotinas_automaticas_cargadiariarotinas'
        verbose_name = 'Carga Diária de Rotinas'
        verbose_name_plural = 'Cargas Diárias de Rotinas'
        ordering = ['-data_carga']
    
    def __str__(self):
        return f"Carga {self.data_carga} - {self.get_status_display()}"


class LogScheduler(models.Model):
    """Tabela de logs do scheduler"""
    
    NIVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, default='INFO')
    componente = models.CharField(max_length=100, help_text="Componente que gerou o log")
    mensagem = models.TextField()
    
    # Relacionamentos opcionais
    fila_execucao = models.ForeignKey(FilaExecucao, on_delete=models.CASCADE, null=True, blank=True)
    carga_diaria = models.ForeignKey(CargaDiariaRotinas, on_delete=models.CASCADE, null=True, blank=True)
    
    # Dados contextuais
    dados_extra = models.JSONField(null=True, blank=True, help_text="Dados extras em JSON")
    stack_trace = models.TextField(null=True, blank=True)
    
    # Timestamp
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rotinas_automaticas_logscheduler'
        verbose_name = 'Log do Scheduler'
        verbose_name_plural = 'Logs do Scheduler'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"[{self.nivel}] {self.componente} - {self.mensagem[:100]}"
