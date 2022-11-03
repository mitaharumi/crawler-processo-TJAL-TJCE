class ErroFactivel(Exception):
    def __init__(self, erro):
        super().__init__(erro)


class ErroInesperado(Exception):
    def __init__(self, erro):
        super().__init__(erro)




class Evento:
    def evento(self, nome: str):
        match nome:
            case 'nao_encontrou_processo':
                # para execucao
                print('parou')