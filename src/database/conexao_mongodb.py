from src.database.models_mongoengine import ModelControleExtracao, ModelDadosProcessoPrimeiroGrau, ModelDadosProcessoSegundoGrau
from src.crawler.models_pydantic import PrimeiroGrau, SegundoGrau

from mongoengine import connect, disconnect, Q
from contextlib import contextmanager

from datetime import datetime
import json
import random


class Database:

    @contextmanager
    def __conexao(self):
        conexao = connect(db="processos", host="localhost", port=27017)
        try:
            yield conexao
        finally:
            disconnect()

    def inserir_processos_em_controle_extracao(self, id_requisicao: int, numeros_processos: list[str]):
        lista_para_insercao = []

        for numero_processo in numeros_processos:
            lista_para_insercao.append(
                ModelControleExtracao(numero_processo=numero_processo, id_requisicao=id_requisicao)
            )

        with self.__conexao():
            ModelControleExtracao.objects.insert(lista_para_insercao)

    def consultar_quantidade_processos_restantes(self, id_requisicao: int):
        with self.__conexao():
            return ModelControleExtracao.objects(Q(id_requisicao=id_requisicao) & (Q(status=0)) | (Q(status=-1) & Q(tentativas__lte=2))).count()

    def pegar_processo_nao_inicializado(self, id_requisicao_mais_antiga: int):
        with self.__conexao():
            # pegando os processos da requisicao mais antiga nao finalizada
            processos_requisao_mais_antiga = ModelControleExtracao.objects(
                Q(id_requisicao=id_requisicao_mais_antiga) & Q(status=0)).order_by('id_requisicao')

            if processos_requisao_mais_antiga:
                # processo aleatorio da requisicao mais antiga
                # para reduzir a chances de mais de um robo pegar o mesmo processo
                processo = processos_requisao_mais_antiga[random.randint(0, len(processos_requisao_mais_antiga) - 1)]
                return processo
            else:
                # nao ha processos que ainda nao foram inicializados nessa requisicao
                return None

    def pegar_id_requisicao_mais_antiga_nao_inicializada(self):
        with self.__conexao():
            processos_requisao_mais_antiga = ModelControleExtracao.objects(Q(status=0)).order_by('id_requisicao')
            if processos_requisao_mais_antiga:
                id_requisicao = processos_requisao_mais_antiga[0].id_requisicao
                return id_requisicao
            else:
                # todas requisicoes foram finalizadas
                return None

    def atualizar_status_extracao(self, processo: ModelControleExtracao, status: int):
        """
            atualiza status do processo em controle extracao

            caso status for atualizado para -1,
            primeiro verifica se tentativas é igual a 2,
                se for igual a 2: atualiza o status para 1
                senao for: incrementa as tentativas e muda status para 0
                    assim "reseta" a extracao para mais uma tentativa
        """
        with self.__conexao():
            if status == -1:
                if processo.tentativas == 2:
                    processo.update(status=-1)
                else:
                    processo.update(tentativas=processo.tentativas + 1)
                    processo.update(status=0)

            processo.update(status=status)

    def atualizar_data_inicial(self, processo: ModelControleExtracao):
        with self.__conexao():
            processo.update(data_inicio=datetime.today().strftime('%d/%m/%Y %H:%M:%S'))

    def consultar_colletion(self, model):
        with self.__conexao():
            for controle in model.objects:
                print(controle.to_json())

    def limpar_collection(self, model):
        with self.__conexao():
            collection = model.objects()
            collection.delete()

    def adicionar_dados_processo_primeiro_grau(self, processo_primeiro_grau: [PrimeiroGrau, SegundoGrau]):
        with self.__conexao():
            ModelDadosProcessoPrimeiroGrau(**processo_primeiro_grau.dict()).save()

    def adicionar_dados_processo(self, processo: [PrimeiroGrau, SegundoGrau]):
        with self.__conexao():
            if isinstance(processo, PrimeiroGrau):
                # adicionando no bando dados um processo de primeiro grau
                ModelDadosProcessoPrimeiroGrau(**processo.dict()).save()
            else:
                # adicionando no bando dados um processo de segundo grau
                ModelDadosProcessoSegundoGrau(**processo.dict()).save()

    def pegar_dados_processo(self, numero_processo, processo_primeiro_grau, processo_segundo_grau):
        with self.__conexao():
            ModelControleExtracao(numero_processo, processo_primeiro_grau, processo_segundo_grau).save()

    def destravar_emissoes(self):
        with self.__conexao():
            processos = ModelControleExtracao.objects(Q(status=1))
            for processo in processos:
                data_inicio = datetime.strptime(processo.data_inicio, '%d/%m/%Y %H:%M:%S')
                data_agora = datetime.now()

                # se a extracao tiver com status 1 a mais de 5 minutos, ela é resetada
                if (data_agora-data_inicio).total_seconds() > 60 * 5:
                    print(f'destravando: processo {processo.numero_processo} (requisicao {processo.id_requisicao})')
                    processo.update(status=0, data_inicio=None)

    def pegar_dados_requisicao(self, id_requisicao):
        with self.__conexao():
            processos = ModelControleExtracao.objects(id_requisicao=id_requisicao)
            numeros_processos = [processo.numero_processo for processo in processos]

            processos_primeiro_grau = ModelDadosProcessoPrimeiroGrau.objects(Q(numero__in=numeros_processos))
            processos_segundo_grau = ModelDadosProcessoSegundoGrau.objects(Q(numero__in=numeros_processos))

            dados_processo = []

            for primeiro_grau, segundo_grau in zip(processos_primeiro_grau, processos_segundo_grau):
                primeiro_grau = json.loads(primeiro_grau.to_json())
                del primeiro_grau['_id']
                segundo_grau = json.loads(segundo_grau.to_json())
                del segundo_grau['_id']

                dados_processo.extend([primeiro_grau, segundo_grau])

            return sorted(dados_processo, key=lambda processo: processo['numero'])


def teste():
    db = Database()
    # db.inserir_processos_em_controle_extracao(['13', '24'], '900')
    # db.consultar(ModelControleExtracao)
    # db.consultar_quantidade_processos_restantes(id_requisicao=1667244264)
    # db.pegar_processo_nao_inicializado()

    # id_requisicao = db.pegar_id_requisicao_mais_antiga_nao_inicializada()
    # processo = db.pegar_processo_nao_inicializado(id_requisicao)
    # db.atualizar_status_extracao(processo, -1)
    # db.atualizar_data_inicial(processo)
    # db.consultar_colletion(ModelControleExtracao)
    # db.pegar_dados_requisicao('1667346967')
    # db.consultar_colletion(ModelControleExtracao)
    # db.limpar_collection(ModelControleExtracao)
    # db.limpar_collection(ModelDadosProcessoPrimeiroGrau)
    # db.limpar_collection(ModelDadosProcessoSegundoGrau)

    db.consultar_colletion(ModelDadosProcessoPrimeiroGrau)
    db.consultar_colletion(ModelDadosProcessoSegundoGrau)
    # db.destravar_emissoes()

# asyncio.run(teste())
teste()

