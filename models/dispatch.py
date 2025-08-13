from pydantic import BaseModel, Field
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


class Pessoa(BaseModel):
    Nome: Optional[str] = None
    CPFCNPJ: Optional[str] = None
    Telefone: Optional[str] = None
    TelefoneFixo: Optional[str] = None
    TelefoneAdicional: Optional[str] = None
    Email: Optional[str] = None
    Empresa: Optional[str] = None
    Endereco: Optional[str] = None
    Numero: Optional[str] = None
    Complemento: Optional[str] = None
    Bairro: Optional[str] = None
    Cidade: Optional[str] = None
    Estado: Optional[str] = None
    Pais: Optional[str] = None
    CEP: Optional[str] = None
    IE: Optional[str] = None
    Loja: Optional[str] = None
    NomeCentroDistribuicao: Optional[str] = None
    CodigoCentroDistribuicao: Optional[str] = None


class Frete(BaseModel):
    Transportadora: Optional[Transportadora] = None
    Destinatario: Pessoa
    Remetente: Pessoa
    Tomador: Optional[Pessoa] = None


class NotaFiscal(BaseModel):
    DataEmissao: Optional[datetime] = None
    Numero: Optional[int] = None
    Serie: Optional[int] = None
    Chave: Optional[str] = None
    ValorTotal: Optional[float] = None
    ValorTotalProdutos: Optional[float] = None
    Cfop: Optional[str] = None
    StringXML: Optional[str] = None


class Item(BaseModel):
    IdUnico: str
    QuantidadeProdutos: int
    Volumes: int
    Largura: Optional[float] = None
    Peso: Optional[float] = None
    Altura: Optional[float] = None
    Comprimento: Optional[float] = None
    Produtos: List[Produto]
    Frete: Frete


class CanalDeVenda(BaseModel):
    Id: Optional[str] = None
    Nome: Optional[str] = None
    Tipo: Optional[str] = None


class Warehouse(BaseModel):
    Id: Optional[str] = None
    Nome: Optional[str] = None


class DispatchRequest(BaseModel):
    CriacaoPedido: datetime
    DataPagamento: Optional[datetime] = None
    NumeroPedido: str
    NumeroPedidoMarketplace: Optional[str] = None
    NumeroPedidoErp: Optional[str] = None
    NumeroPedidoAux: Optional[str] = None
    CanalDeVenda: Optional[CanalDeVenda] = None
    Warehouse: Optional[Warehouse] = None
    Itens: List[Item]
    NotaFiscal: Optional[NotaFiscal] = None
    InfosAdicionais: Optional[dict] = None
    Marketplace: Optional[str] = None
    Marca: Optional[str] = None
    Seller: Optional[str] = None
    IdsAuxiliares: Optional[List[str]] = None
