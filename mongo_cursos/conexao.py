import os
from functools import lru_cache
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

@lru_cache(maxsize=1)
def obter_banco():
    uri = os.getenv("MONGO_URI")
    nome_banco = os.getenv("MONGO_DB")

    if not uri or not nome_banco:
        raise ValueError("Configure MONGO_URI e MONGO_DB no arquivo .env.")

    cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)

    return cliente[nome_banco]

if __name__ == "__main__":
    try:
        banco = obter_banco()
        banco.command("ping")

        print("Conexão realizada com sucesso!")
        print("Banco:", banco.name)

    except Exception as erro:
        raise SystemExit(f"Erro na conexão: {erro}") from None
