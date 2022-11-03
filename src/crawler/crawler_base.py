import time
from pyppeteer import launch


class CrawlerBase:
    def __init__(self):
        self.browser = None
        self.page = None

    async def iniciar_navegador(self):
        self.browser = await launch(headless=False, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
        # self.browser = await launch(
        #     headless=True,
        #     args=['--no-sandbox'],
        #     handleSIGINT=False,
        #     handleSIGTERM=False,
        #     handleSIGHUP=False
        # )
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(5000)

    async def fechar_navegador(self):
        await self.browser.close()

    async def atribuir_valor(self, seletor: str, value: str) -> None:
        await self.page.evaluate(
            f"""document.querySelector('{seletor}').value = '{value}'""")

    async def extrair_texto(self, seletor, tempo_maximo_de_espera: int = 2000) -> [str, None]:
        try:
            await self.page.waitForSelector(seletor, timeout=tempo_maximo_de_espera)
        except:
            print(f'nao achou o seletor {seletor}')
            # seletor nao encontrado
            return None
        else:
            texto = await self.page.evaluate('(elemento) => elemento.innerText', await self.page.querySelector(seletor))
            return texto

    async def pegar_conteudo_texto(self, seletor: str) -> str:
        return await self.page.evaluate('(elemento) => elemento.innerText', await self.page.querySelector(seletor))

    async def esperar_por_botao_radio_estar_selecionado(self, seletor: str, tempo_maximo_de_espera: float = 5) -> None:
        tempo_inicial = time.time()
        while float(time.time() - tempo_inicial) <= tempo_maximo_de_espera:
            if await self.checar_status_botao_radio(seletor):
                break
            time.sleep(0.5)
        else:
            raise Exception(f'botao {seletor} nao foi selecionado')

    async def checar_status_botao_radio(self, seletor: str) -> bool:
        return await self.page.evaluate(f'(elemento) => elemento.checked', await self.page.querySelector(seletor))

    async def esperar_botao_estar_habilitado(self, seletor: str, tempo_maximo_de_espera: float = 5) -> None:
        tempo_inicial = time.time()
        while float(time.time() - tempo_inicial) <= tempo_maximo_de_espera:
            if await self.checar_se_botao_esta_habilitado(seletor):
                break
            time.sleep(0.5)
        else:
            raise Exception(f'botao {seletor} ainda esta desabilitado')

    async def checar_se_botao_esta_habilitado(self, seletor: str) -> bool:
        botao = await self.page.querySelector(seletor)
        desabilitado = await self.page.evaluate(f'(botao) => botao.getAttribute("disabled")', botao)
        return True if desabilitado != 'disabled' else False

    async def clicar_e_esperar_elemento_desaparecer(self, seletor: str, tempo_maximo_de_espera: float = 10) -> bool:
        tempo_inicial = time.time()
        while float(time.time() - tempo_inicial) <= tempo_maximo_de_espera:
            await self.page.click(seletor)

            try:
                await self.page.waitForSelector(seletor, {'timeout': 2000})
            except:
                return True
        else:
            raise Exception(f'ao clicar e esperar por elemento desaparecer ({seletor})')
