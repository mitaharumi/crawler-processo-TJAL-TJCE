from src.crawler.crawler_base import CrawlerBase
from src.crawler.models_pydantic import PrimeiroGrau, SegundoGrau, Parte, Movimentacao, ErroFactivel, ErroInesperado
from src.utils import *

import traceback
import asyncio
import re
from datetime import datetime


class ExtrairProcesso(CrawlerBase):
    def __init__(self, database):
        super().__init__()
        self.database = database

        self.primeiro_grau = None
        self.url_busca = None
        self.numero_processo = None
        self.codigo_tribunal = None

        self.dados_para_extrair_primeiro_grau = [
            'numero',
            'classe',
            'assunto',
            'area',
            'valor_da_acao',
            'data_de_distribuicao',
            'juiz',
            'foro',
            'vara',
            'partes_do_processo',
            'movimentacoes'
        ]
        self.dados_para_extrair_segundo_grau = [
            'numero',
            'classe',
            'assunto',
            'area',
            'valor_da_acao',
            'secao',
            'orgao_julgador',
            'relator',
            'partes_do_processo',
            'movimentacoes'
        ]

        self.passos_extracao_primeiro_grau = [
            self.buscar_por_processo,
            self.extrair_dados_processo_primeiro_grau
        ]
        self.passos = [
            self.buscar_por_processo,
            self.extrair_dados
        ]

    def set_numero_processo(self, numero_processo):
        self.numero_processo = numero_processo

    def set_codigo_tribunal(self):
        self.codigo_tribunal = self.numero_processo[-7:-4]

    def set_url_busca(self):
        match self.codigo_tribunal:
            case '802':  # tribunal de justiça de Alagoas (TJAL)
                self.url_busca = 'https://www2.tjal.jus.br/cpopg/open.do' \
                    if self.primeiro_grau else 'https://www2.tjal.jus.br/cposg5/open.do'
            case '806':  # tribunal de justiça de Ceará (TJCE)
                self.url_busca = 'https://esaj.tjce.jus.br/cpopg/open.do' \
                    if self.primeiro_grau else 'https://esaj.tjce.jus.br/cposg5/open.do'
            case _:
                print(f'tribunal invalido! {self.codigo_tribunal}')

    def set_primeiro_grau(self, status: bool):
        self.primeiro_grau = status

    async def executar_extracao(self, processo):
        """
            funcao seta o numero do processo/codigo do tribunal,

            chama a extracao do processo de primeiro grau,
            caso de certo chama a extracao de segundo grau caso

            se as duas extracoes derem certo,
            retorna true

            caso alguma extracao falhe,
            retorna false
        """

        self.set_numero_processo(processo.numero_processo)
        self.set_codigo_tribunal()

        if await self.extracao_processo(primeiro_grau=True, passos=self.passos):
            if await self.extracao_processo(primeiro_grau=False, passos=self.passos):
                return True

        return False

    async def buscar_por_processo(self):
        await self.page.goto(self.url_busca)

        try:
            await self.page.waitForSelector('#numeroDigitoAnoUnificado')
        except Exception as e:
            raise Exception(f'seletor nao apareceu (#numeroDigitoAnoUnificado) | {e}')

        await self.atribuir_valor('#numeroDigitoAnoUnificado', self.numero_processo[:13])
        await self.atribuir_valor('#foroNumeroUnificado', self.numero_processo[-4:])

        await self.page.click('[value="Consultar"]')

        if self.primeiro_grau:
            await self.verificar_se_processo_existe('#numeroProcesso')
        else:
            await self.verificar_se_processo_existe('#processoSelecionado')
            await self.selecionar_processo()
            await self.page.waitForSelector('#numeroProcesso')

        return True

    async def selecionar_processo(self):
        # todo: pegar caso que tem mais de um processo
        try:
            # verificando se apareceu o popup de selecionar processo
            await self.page.waitForSelector('#processoSelecionado')
        except Exception as e:
            # nao apareceu popup de selecionar processo
            raise Exception(f'selecionar processo, seletor do popup nao apareceu (#processoSelecionado) | {e}')
        else:
            # apareceu popup, selecionando o primeiro processo
            await self.page.click('#processoSelecionado')

            await self.esperar_botao_estar_habilitado('#botaoEnviarIncidente')
            await self.clicar_e_esperar_elemento_desaparecer('[value="Selecionar"]')

    async def verificar_se_processo_existe(self, seletor: str):
        try:
            await self.page.waitForSelector(f'{seletor}')
        except:
            mensagem = await self.extrair_texto('#mensagemRetorno')
            if 'Não existem informações disponíveis para os parâmetros informados' in mensagem:
                raise ErroFactivel('nao existe informacoes sobre processo')

            if not mensagem:
                raise Exception('erro desconhecido ao buscar por processo')

    async def extracao_processo(self, primeiro_grau: bool, passos: list):
        """
            funcao responsavel por executar os passos da extracao
            estrutura feita para ser adpatada facilmente se aumentar a quantidade de passos

            executa passo,
                caso retorne true: passa para o passo seguinte
                caso falhe: recomeca a extracao a partir do primeiro passo
            tenta executar os passos por ate 3 vezes

            retorna true caso todos os passos da extracao forem concluidas ou o processo nao existe
        """
        for tentativa in range(3):
            self.set_primeiro_grau(primeiro_grau)
            self.set_url_busca()

            print(f'\t> extraindo processo de {"primeiro" if self.primeiro_grau else "segundo"} grau')
            # execucao dos passos conforme grau do processo
            for passo in passos:
                print(f'\tentrou em {passo.__name__}')
                try:
                    await passo()
                except Exception as e:
                    # para a execucao caso seja um erro como, por exemplo, processo nao existe
                    if isinstance(e, ErroFactivel) or tentativa >= 2:
                        print(f'\tparou no passo {passo.__name__}')
                        print(f'\t{e}')
                        return True

                    print(f'\tparou em {passo.__name__}, tentando novamente realizar extracao')
                    print(e)
                    # para a execucao e tenta novamente a extracao (se tentativas menor que 3)
                    # caso seja um erro inesperado como, por exemplo, nao carregou a pagina
                    break
            else:
                print(f'\tconcluiu todos os passos')
                return True
        else:
            print('erro na extracao')
            return False

    async def extrair_dados(self):
        if self.primeiro_grau:
            await self.extrair_dados_processo_primeiro_grau()

        else:
            await self.extrair_dados_processo_segundo_grau()

        return True

    async def extrair_dados_processo_primeiro_grau(self):

        # extraindo dados
        dados_extraidos = await asyncio.gather(
            self.extrair_texto('#classeProcesso'),
            self.extrair_texto('#assuntoProcesso'),
            self.extrair_texto('#areaProcesso'),
            self.extrair_valor_da_acao(),
            self.extrair_data_distribuicao(),
            self.extrair_texto('#juizProcesso'),
            self.extrair_texto('#foroProcesso'),
            self.extrair_texto('#varaProcesso'),
            self.extrair_partes_do_processo(),
            self.extrair_movimentacoes()
        )

        # adicionando dado de numero_processo na lista de dados extraidos
        dados_extraidos.insert(0, self.numero_processo)

        # criando objeto processo primeiro grau
        processo = PrimeiroGrau(**dict(zip(self.dados_para_extrair_primeiro_grau, dados_extraidos)))

        # inserindo no banco de dados
        self.database.adicionar_dados_processo_primeiro_grau(processo)

        return True

    async def extrair_dados_processo_segundo_grau(self):
        # extraindo dados
        dados_extraidos = await asyncio.gather(
            self.extrair_texto('#classeProcesso'),
            self.extrair_texto('#assuntoProcesso'),
            self.extrair_texto('#areaProcesso'),
            self.extrair_valor_da_acao(),
            self.extrair_texto('#secaoProcesso'),
            self.extrair_texto('#orgaoJulgadorProcesso'),
            self.extrair_texto('#relatorProcesso'),
            self.extrair_partes_do_processo(),
            self.extrair_movimentacoes()
        )

        # adicionando dado de numero_processo na lista de dados extraidos
        dados_extraidos.insert(0, self.numero_processo)

        # criando objeto processo segundo grau
        processo = SegundoGrau(**dict(zip(self.dados_para_extrair_segundo_grau, dados_extraidos)))

        # inserindo no banco de dados
        self.database.adicionar_dados_processo(processo)

        return True

    async def extrair_valor_da_acao(self):
        valor = await self.extrair_texto('#valorAcaoProcesso')

        return float(substituir_caracteres(valor, ['R$', ' ', '.']).replace(',', '.')) if valor else None

    async def extrair_data_distribuicao(self):
        texto_distribuicao = await self.extrair_texto('#dataHoraDistribuicaoProcesso')
        data = re.search(r'\d+/\d+/\d+ às \d+:\d+', texto_distribuicao)
        if data:
            return datetime.strptime(data[0], '%d/%m/%Y às %H:%M').strftime('%d/%m/%Y %H:%M:%S')

    async def extrair_partes_do_processo(self):
        try:
            await self.page.waitForSelector('#tablePartesPrincipais')
        except Exception as e:
            raise Exception(f'seletor nao apareceu (#tablePartesPrincipais) | {e}')

        partes = []
        partes_extraidas = await self.page.evaluate(self.extrair_partes_do_processo_page_evaluate())

        for parte_extraida in partes_extraidas:
            partes.append(
                Parte(
                    **{
                        'parte': substituir_caracteres(parte_extraida["parte"], ['\xa0', '\t']),
                        'nomes': substituir_caracteres(parte_extraida["nomes"], ['\xa0', '\t']).split('\n')
                    }
                )
            )
        return partes

    @staticmethod
    def extrair_partes_do_processo_page_evaluate():
        return """ () => { 
            partes_tabela_linhas = document.querySelectorAll('#tablePartesPrincipais > tbody > tr');
            partes = [];
            for (let parte of partes_tabela_linhas){
                partes_tabela_colunas = parte.querySelectorAll('td');
                partes.push({
                    parte: partes_tabela_colunas[0].innerText, 
                    nomes: partes_tabela_colunas[1].innerText
                });
            }
            return partes
        }"""

    async def extrair_movimentacoes(self):
        try:
            await self.page.waitForSelector('#tabelaUltimasMovimentacoes')
        except Exception as e:
            raise Exception(f'seletor nao apareceu (#tabelaUltimasMovimentacoes) | {e}')

        movimentacoes = []
        movimentacoes_extraidas = await self.page.evaluate(self.extrair_movimentacoes_page_evaluate())

        for movimentacao_extraida in movimentacoes_extraidas:
            movimento = movimentacao_extraida['movimento']
            # removendo partes que comecam e terminam com \n e \t
            substrings = re.findall(r'^[\n+\t+]+', movimento)
            substrings += re.findall(r'[\n+\t+]+$', movimento)
            # removendo partes que comecam e terminam com \n e/ou espacos
            substrings += re.findall(r'^[\n+ +]+', movimento)
            substrings += re.findall(r'[\n+ +]+$', movimento)
            substrings += re.findall(r'^[ +]+', movimento)
            substrings += re.findall(r'[ +]+$', movimento)

            if substrings:
                movimento = substituir_caracteres(movimento, substrings)

            # removendo espacos duplicados, \n+\t, \n, \t e espacos no meio da string
            substrings = re.findall(r'^[\n+\t+]+', movimento)
            substrings += re.findall(r'^[\n+ +]+', movimento)
            substrings += re.findall(r'[\t]{2,}', movimento)
            substrings += re.findall(r'[ ]{2,}', movimento)

            if substrings:
                movimento = substituir_caracteres(movimento, substrings, ' ')
            
            movimentacoes.append(
                Movimentacao(
                    **{
                        'data_de_movimentacao':
                            datetime.strptime(
                                substituir_caracteres(movimentacao_extraida['data'], ['\t', '\n', ' ']),
                                '%d/%m/%Y'
                            ).strftime('%d/%m/%Y'),
                        'movimento': movimento
                    }
                )
            )

        return movimentacoes

    def extrair_movimentacoes_page_evaluate(self):
        seletor_data, seletor_descricao = (".dataMovimentacao", ".descricaoMovimentacao") \
            if self.primeiro_grau \
            else (".dataMovimentacaoProcesso", ".descricaoMovimentacaoProcesso")

        return f""" () => {{
            movimentacoes_tabela_linhas = document.querySelectorAll('#tabelaTodasMovimentacoes > tr');
            movimentacoes = [];
            for (let movimentacao of movimentacoes_tabela_linhas){{
                movimentacoes.push({{
                    data: movimentacao.querySelector('{seletor_data}').innerText,
                    movimento: movimentacao.querySelector('{seletor_descricao}').innerText
                }});
            }}
            return movimentacoes
        }}"""

