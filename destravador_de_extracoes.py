from src.database.conexao_mongodb import Database
import time

# a cada 3 minutos checa e destrava extracoes paradas no status 1 por mais de 5 minutos
if __name__ == '__main__':
    db = Database()
    while True:
        db.destravar_emissoes()

        time.sleep(3 * 60)