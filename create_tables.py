from database import engine, Base
from models.pedido import Pedido  # Adicione outros modelos se houver

Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas com sucesso!")
