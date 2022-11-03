# busca-processo-TJAL-TJCE
Crawler realizado em pyppeteer que busca dados de um processo de primeiro e segundo grau dos Tribunais de Justiça de Alagoas (TJAL) e do Ceará (TJCE) com uma API Flask pra solicitação e retorno dos dados.

----
#### todo
- [ ] arquivos teste para rodar localmente
- [ ] pretty retorno api
- [ ] atualizacao do readme
  - [ ] outros SO
- [ ] documentacao de funcao
- [ ] aws
  - [ ] criar infra para acessar via loadbalancer
  - [ ] pm2 rodando o crawler e o destravador de extracao
  - [ ] gunicorn pra rodar a api
- [ ] docker *
----

### Informaçoes gerais

#### Dados a serem coletados:

**primeiro grau**

    classe
    área
    assunto
    data de distribuição
    juiz
    valor da ação
    partes do processo
    lista das movimentações (data e movimento)

**segundo grau**

    classe
    área
    assunto
    valor da ação
    partes do processo
    lista das movimentações (data e movimento)
	secao
	orgao julgador
	relator

#### Funcionamento geral do projeto
* api.py, reponsavel por:
  * receber os numeros de processos para extracao do usuario
  * inserir no banco os numeros (em ModelControleProcesso) do processo 
  * devolver os dados das extracoes que estao no banco (em ModelDadosProcessoPrimeiroGrau e ModelDadosProcessoSegundoGrau) para cliente
* gerenciador_extracoes.py, responsavel por:
  * verificar no banco se existem extracoes pendentes para ser extraidas
  * chamar crawler de extracao 
  * atualizar status da extracao (em ModelControleProcesso)
* destravador_de_extracoes.py, responsavel por:
  * destravar posiveis extracoes que possam estar travadas
    * extracoes com status 1 com mais de 3 minutos desde o status inicial

## Requisitos e instalação local

* python 3.10
* env
* pyppeteer
* mongodb

> instalação a seguir para sistemas linux
### python 3.10
```
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.10
```
### ambiente virtual e instalação de requirements

#### instalação
```
sudo apt install python3-venv
```

#### criação
```
python3.10 -m venv name-venv
```

#### ativação
```
source name-venv/bin/activate
```

#### instalação requirements 
```
pip install -r requirements.txt
```

#### para sair da venv, caso necessite
```
deactivate
```

### pyppeteer (instalação chromium)
```
pyppeteer install
```

### mongodb
- Para a instalação mongodb siga o [tutorial](https://www.mongodb.com/docs/manual/installation/) do seu sistema operacional.
- Para macos recomendo esse [tutorial](https://armstar.medium.com/mongodb-with-python-on-mac-for-absolute-beginners-d9f9d791d03c) simples.

## Executar projeto
Apos todos os requisitos instalados e o banco configurado, execute os 3 arquivos no root: 
- api.py
- destravador_extracoes.py
- gerenciador_extracoes.py

Ou execute o comando
```
 python3 api.py && python3 destravador_extracoes.py && python3 gerenciador_extracoes.py
```

### Enviar numero de processos e receber dados da extração
- consulte se a api esta healthy pelo link:
  - [localhost:5000/](localhost:5000/)
- envie numero de processos pelo link:
  - [localhost:5000/nova-requisicao](localhost:5000/nova-requisicao)
    - recebera um id_requisicao no retorno que deve ser utilizado para consultar os dados da extração
- consulte dados da extração pelo link, passando o id_requisicao no final:
  - localhost:5000/consultar-requisicao?id_requisicao=<id_requicao>

{
	"numeros_processos" : [
		"0729650-85.2021.8.02.0001", 
		"0733864-85.2022.8.02.0001", 
		"0734578-79.2021.8.02.0001", 
		"0729237-72.2021.8.02.0001", 
		"0728504-43.2020.8.02.0001",
		"0070337-91.2008.8.06.0001",
		"0710802-55.2018.8.02.0001"
	]
}


numeros = []

for (a of document.querySelectorAll('.DocumentFooter-item > a')){
  numero = a.innerText.replace('Andamento do Processo n.', '')
  numeros.push(numero.slice(0, 26))
}

console.log(numeros)


