from app.database import Base, engine
from app.models import models  # Importa todos os modelos para registrar as tabelas

print("Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso!")