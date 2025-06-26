from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class CanalDeVenda(BaseModel):
    Id: Optional[str]
    Nome: Optional[str]

class Warehouse(BaseModel):
    Id: Optional[str] = Field(default=None, alias="id")
    Nome: Optional[str] = Field(default=None, alias="nome")

class Produto(BaseModel):
    Descricao: Optional[str]
    Preco: Optional[float]
    Quantidade: Optional[int]
    SKU: Optional[str]
    NumeroDeSerie: Optional[str]

class Transportadora(BaseModel):
    Id: Optional[str]
    Nome: Optional[str]
    NomeServico: Optional[str]
    IdServico: Optional[str]
    CodigoRastreio: Optional[str]
    ListaPostagem: Optional[str]
    Reversa: Optional[bool]
    Coleta: Optional[bool] = None
    Dispatch: Optional[bool] = None
    AlocacaoAutomatica: Optional[bool] = None
    ValorAR: Optional[float] = 0.0
    ValorAverbadoPago: Optional[float] = 0.0
    ValorDeclarado: Optional[float] = 0.0
    ValorFrete: Optional[float] = 0.0

class Pessoa(BaseModel):
    Nome: Optional[str]
    CPFCNPJ: Optional[str]
    Telefone: Optional[str]
    TelefoneFixo: Optional[str] = None
    TelefoneAdicional: Optional[str] = None
    Email: Optional[str]
    Empresa: Optional[str]
    Endereco: Optional[str]
    Numero: Optional[str]
    Complemento: Optional[str]
    Bairro: Optional[str]
    Cidade: Optional[str]
    Estado: Optional[str]
    Pais: Optional[str]
    CEP: Optional[str]
    IE: Optional[str]

class Remetente(Pessoa):
    NomeCentroDistribuicao: Optional[str]
    CodigoCentroDistribuicao: Optional[str]
    CPFCNPJ: Optional[str]

class Frete(BaseModel):
    Transportadora: Optional[Transportadora]
    Destinatario: Optional[Pessoa]
    Remetente: Optional[Remetente]
    Tomador: Optional[Pessoa]

class Item(BaseModel):
    IdUnico: Optional[str]
    QuantidadeProdutos: Optional[int] = None
    Volumes: Optional[int]
    Largura: Optional[float]
    Peso: Optional[float]
    Altura: Optional[float]
    Comprimento: Optional[float]
    Formato: Optional[str] = None
    Produtos: Optional[List[Produto]]
    Frete: Optional[Frete]

class NotaFiscal(BaseModel):
    DataEmissao: Optional[datetime]
    Numero: Optional[int]
    Serie: Optional[int]
    Chave: Optional[str]
    ValorTotal: Optional[float]
    ValorTotalProdutos: Optional[float]

class InfosAdicionais(BaseModel):
    EntregaAgendada: Optional[bool] = None
    Portabilidade: Optional[bool] = None

class DispatchRequest(BaseModel):
    CriacaoPedido: datetime
    DataPagamento: Optional[datetime] = None
    NumeroPedido: str
    NumeroPedidoMarketplace: Optional[str]
    NumeroPedidoErp: Optional[str]
    NumeroPedidoAux: Optional[str]
    CanalDeVenda: Optional[CanalDeVenda]
    Warehouse: Optional[Warehouse] = Field(default=None, alias="warehouse")
    UnidadeDeNegocio: Optional[str] = None
    Rede: Optional[str] = None
    Marca: Optional[str] = None
    Seller: Optional[str] = None
    Campanha: Optional[str] = None
    Itens: List[Item]
    NotaFiscal: Optional[NotaFiscal]
    InfosAdicionais: Optional[InfosAdicionais]

    class Config:
        populate_by_name = True
        extra = "allow"
