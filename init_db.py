from database import Base, engine
from models.pedido import Pedido

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso!")