# busca-processo-TJAL-TJCE
API que busca dados de um processo em todos os graus dos Tribunais de Justiça de Alagoas (TJAL) e do Ceará (TJCE).


Dados a serem coletados:

    classe
    área
    assunto
    data de distribuição
    juiz
    valor da ação
    partes do processo
    lista das movimentações (data e movimento)



## instalacao

```
pyppeteer install
```

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
