from src.database.conexao_mongodb import Database
from src.crawler.crawler_extracao_processos import ExtrairProcesso

import asyncio
import random
import time


async def main():
    database = Database()

    while True:
        aux_tempo = time.time()
        extracao = ExtrairProcesso(database)
        await extracao.iniciar_navegador()

        # verifica a requisicoes as pendentes por aproximadamente 5 minutos apos isso fecha o navegador
        # (para diminuir as chances de estouro de memoria por parte do chromium)
        while int(time.time() - aux_tempo) < 60 * 5:
            print('verificando se existem requisicoes pendentes ...')

            id_requisicao_mais_antiga = database.pegar_id_requisicao_mais_antiga_nao_inicializada()
            if id_requisicao_mais_antiga:
                print(f'\n\nrequisicao {id_requisicao_mais_antiga} pendente!')
                while True:
                    processo = database.pegar_processo_nao_inicializado(id_requisicao_mais_antiga)

                    if not processo:
                        print(f'nao existem mais extracoes nao inicializadas na requisicao {id_requisicao_mais_antiga}\n\n')
                        break

                    print(f'\niniciando extracao do processo: {processo.numero_processo}')

                    database.atualizar_status_extracao(processo, 1)
                    database.atualizar_data_inicial(processo)

                    if await extracao.executar_extracao(processo):
                        # extracao foi um sucesso,
                        # atualizando status processo para 2 no controle de extracao
                        database.atualizar_status_extracao(processo, 2)
                    else:
                        # extracao falhou,
                        # atualizando status processo para -1 no controle de extracao
                        database.atualizar_status_extracao(processo, -1)

                    print(f'extracao finalizado do processo: {processo.numero_processo}\n')

                    # delay aleatorio para reduzir as chances de mais de 1 robo pegar o mesmo processo
                    time.sleep(random.randint(0, 5))

            # todo: tirar essa trap
            break

        await extracao.fechar_navegador()
        break

if __name__ == '__main__':
    asyncio.run(main())
