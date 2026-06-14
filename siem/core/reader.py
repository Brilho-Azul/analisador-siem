import time
import os


def tail_log(caminho_arquivo):
    while not os.path.exists(caminho_arquivo):
        print(f"Aguardando o arquivo {caminho_arquivo} ser criado...")
        time.sleep(2)

    with open(caminho_arquivo, 'r') as f:
        f.seek(0, 2)

        while True:
            linha = f.readline()
            if not linha:
                time.sleep(0.5)
                continue

            yield linha