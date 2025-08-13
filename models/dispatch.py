from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Produto(BaseModel):
    Descricao: str
    Preco: float
    Quantidade: int
    SKU: str
    NumeroDeSerie: str
    CodigoProduto: Optional[str] = None
    TipoProduto: Optional[str] = None
    Fabricante: Optional[str] = None
    Altura: Optional[float] = None
    Comprimento: Optional[float] = None
    Largura: Optional[float] = None
    Peso: Optional[float] = None

class Transportadora(BaseModel):
    Id: Optional[str] = None
    Nome: Optional[str] = None
    NomeServico: Optional[str] = None
    IdServico: Optional[str] = None
    CodigoRastreio: Optional[str] = None
    ListaPostagem: Optional[str] = None
    Reversa: Optional[bool] = None
    Coleta: Optional[bool] = None
    Dispatch: Optional[bool] = None
    AlocacaoAutomatica: Optional[bool] = None
    ValorAR: Optional[float] = None
    ValorAverbadoPago: Optional[float] = None
    ValorDeclarado: Optional[float] = None
    ValorFrete: Optional[float] = None
    Prioridade: Optional[bool] = None

    model_config = {
        "extra": "allow"  # permite campos adicionais sem erro
    }

class Pessoa(BaseModel):
    Nome: Optional[str] = None
    Estado: Optional[str] = None
    Cidade: Optional[str] = None
    Endereco: Optional[str] = None
    Numero: Optional[str] = None
    CEP: Optional[str] = None
    Pais: Optional[str] = None

    model_config = {
        "extra": "allow"
    }

class Frete(BaseModel):
    Transportadora: Optional[Transportadora] = None
    Destinatario: Optional[Pessoa] = None
    Remetente: Optional[Pessoa] = None
    Tomador: Optional[Pessoa] = None

    model_config = {
        "extra": "allow"
    }

class NotaFiscal(BaseModel):
    DataEmissao: Optional[datetime] = None
    Numero: Optional[int] = None
    Serie: Optional[int] = None
    Chave: Optional[str] = None
    ValorTotal: Optional[float] = None

    model_config = {
        "extra": "allow"
    }

class Item(BaseModel):
    IdUnico: str
    QuantidadeProdutos: int
    Volumes: int
    Produtos: List[Produto]
    Frete: Optional[Frete] = None

class CanalDeVenda(BaseModel):
    Id: Optional[str] = None
    Nome: Optional[str] = None
    Tipo: Optional[str] = None

class Warehouse(BaseModel):
    Id: Optional[str] = None
    Nome: Optional[str] = None

class DispatchRequest(BaseModel):
    CriacaoPedido: datetime
    NumeroPedido: str
    Itens: List[Item]
    CanalDeVenda: Optional[CanalDeVenda] = None
    Warehouse: Optional[Warehouse] = None
    NotaFiscal: Optional[NotaFiscal] = None

    model_config = {
        "extra": "allow"
    }
