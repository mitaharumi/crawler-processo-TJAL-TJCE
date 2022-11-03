from pydantic import BaseModel
from typing import Optional


class Movimentacao(BaseModel):
    data_de_movimentacao: str
    movimento: str


class Parte(BaseModel):
    parte: str
    nomes: list[str]


class Processo(BaseModel):
    numero: str
    classe: str
    assunto: str
    area: Optional[str]
    valor_da_acao: Optional[float]
    partes_do_processo: Optional[list[Parte]]
    movimentacoes: Optional[list[Movimentacao]]


class PrimeiroGrau(Processo):
    data_de_distribuicao: Optional[str]
    juiz: Optional[str]
    foro: Optional[str]
    vara: Optional[str]


class SegundoGrau(Processo):
    secao: Optional[str]
    orgao_julgador: Optional[str]
    relator: Optional[str]


class ErroFactivel(Exception):
    def __init__(self, erro):
        super().__init__(erro)


class ErroInesperado(Exception):
    def __init__(self, erro):
        super().__init__(erro)