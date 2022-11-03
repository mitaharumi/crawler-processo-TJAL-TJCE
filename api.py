from src.database.conexao_mongodb import Database
from src.utils import substituir_caracteres
from flask.json import JSONEncoder

from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
def _():
    return "true"


@app.route('/nova-requisicao', methods=['POST'])
def nova_requisicao():
    json = request.get_json()

    numeros_processos_json = json['numeros_processos']

    # tratamento dos numeros de processo recebidos
    numeros_processos = [substituir_caracteres(processo, ['-', '.']) for processo in numeros_processos_json]
    numeros_processos_invalidos = [processo for processo in numeros_processos if len(processo) != 20]
    numeros_processos = [processo for processo in numeros_processos if processo not in numeros_processos_invalidos]

    id_requisicao = int(time.time())

    db = Database()
    db.inserir_processos_em_controle_extracao(id_requisicao=id_requisicao, numeros_processos=numeros_processos)

    retorno = f'Requisicao {id_requisicao}\n'
    retorno += f'Foram enviados {len(numeros_processos)} processos ' if len(numeros_processos) != 1 else 'foi enviado 1 processo '
    retorno += f'para extracao, consulte os dados em http://localhost:5000/consultar-requisicao?id_requisicao={id_requisicao}'
    if numeros_processos_invalidos:
        retorno += f'\n\nNumero de processos com dados invalidos: {numeros_processos_invalidos}'

    print(retorno)
    return retorno


@app.route('/consultar-requisicao', methods=['GET'])
def consultar_requisicao():
    id_requisicao = int(request.args['id_requisicao'])

    db = Database()
    quantidade_processos_restantes = db.consultar_quantidade_processos_restantes(id_requisicao=id_requisicao)

    # caso extracao ainda nao foi finalizada
    if quantidade_processos_restantes != 0:
        retorno = f'Faltam {quantidade_processos_restantes} processos para serem extraidos ' \
            if quantidade_processos_restantes > 1 else f'Falta 1 processo para ser extraido '
        retorno += f'na requisicao {id_requisicao}'
        return retorno

    dados_processo = db.pegar_dados_requisicao(id_requisicao)
    print(dados_processo)
    return jsonify(dados_processo)


if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.run(debug=True)
