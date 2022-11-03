from typing import List


def substituir_caracteres(texto: str, caracteres: List, trocar_por: str = '') -> str:
    if texto:
        for caracter in caracteres:
            try:
                texto = texto.replace(caracter, trocar_por)
            except:
                print(f'indo se substituir {caracteres}')
                print(texto)

    return texto


