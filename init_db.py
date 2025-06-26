from database import Base, engine
from models.pedido import Pedido  # Garante que o modelo seja carregado

print("📦 Criando tabelas...")
Base.metadata.drop_all(bind=engine)  # ⚠️ Opcional: limpa tudo antes
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas!")
