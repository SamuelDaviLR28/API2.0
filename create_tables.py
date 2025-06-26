# create_tables.py

from database import engine, Base
from models.pedido import Pedido  # Adicione outros modelos aqui se tiver

def criar_tabelas():
    print("🔧 Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso.")

if __name__ == "__main__":
    criar_tabelas()
