from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField, ReferenceField, StringField, IntField, FloatField, ListField


class ModelControleExtracao(Document):
    id_requisicao = IntField(required=True, max_length=10)
    numero_processo = StringField(required=True, max_length=20)
    status = IntField(required=True, default=0, max_length=1)
    tentativas = IntField(required=True, default=0, max_length=1)
    data_inicio = StringField(max_length=20, null=True)


class ModelsDadosProcessoPartes(EmbeddedDocument):
    parte = StringField(required=True)
    nomes = ListField(StringField(required=True))


class ModelsDadosProcessoMovimentacoes(EmbeddedDocument):
    data_de_movimentacao = StringField(required=True)
    movimento = StringField(required=True)


class ModelDadosProcessoPrimeiroGrau(Document):
    numero = StringField(required=True)
    classe = StringField(required=True)
    assunto = StringField(required=True)
    area = StringField()
    valor_da_acao = FloatField()
    partes_do_processo = ListField(EmbeddedDocumentField(ModelsDadosProcessoPartes))
    movimentacoes = ListField(EmbeddedDocumentField(ModelsDadosProcessoMovimentacoes))

    data_de_distribuicao = StringField(required=True)
    juiz = StringField()
    foro = StringField()
    vara = StringField()


class ModelDadosProcessoSegundoGrau(Document):
    numero = StringField(required=True)
    classe = StringField(required=True)
    assunto = StringField(required=True)
    area = StringField()
    valor_da_acao = FloatField()
    partes_do_processo = ListField(EmbeddedDocumentField(ModelsDadosProcessoPartes))
    movimentacoes = ListField(EmbeddedDocumentField(ModelsDadosProcessoMovimentacoes))

    secao = StringField()
    orgao_julgador = StringField()
    relator = StringField()
