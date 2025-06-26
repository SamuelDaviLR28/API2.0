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
    Id: str
    Nome: str
    NomeServico: str
    IdServico: str
    CodigoRastreio: str
    ListaPostagem: str
    Reversa: bool
    Coleta: bool
    Dispatch: bool
    AlocacaoAutomatica: bool
    ValorAR: float
    ValorAverbadoPago: float
    ValorDeclarado: float
    ValorFrete: float
    Prioridade: bool


class Pessoa(BaseModel):
    Nome: str
    CPFCNPJ: Optional[str] = None
    Telefone: Optional[str] = None
    TelefoneFixo: Optional[str] = None
    TelefoneAdicional: Optional[str] = None
    Email: Optional[str] = None
    Empresa: Optional[str] = None
    Endereco: str
    Numero: str
    Complemento: Optional[str] = None
    Bairro: str
    Cidade: str
    Estado: str
    Pais: str
    CEP: str
    IE: Optional[str] = None
    Loja: Optional[str] = None
    NomeCentroDistribuicao: Optional[str] = None
    CodigoCentroDistribuicao: Optional[str] = None


class Frete(BaseModel):
    Transportadora: Transportadora
    Destinatario: Pessoa
    Remetente: Pessoa
    Tomador: Pessoa


class Item(BaseModel):
    IdUnico: str
    QuantidadeProdutos: int
    Volumes: int
    Largura: Optional[float]
    Peso: Optional[float]
    Altura: Optional[float]
    Comprimento: Optional[float]
    Produtos: List[Produto]
    Frete: Frete


class CanalDeVenda(BaseModel):
    Id: str
    Nome: str


class Warehouse(BaseModel):
    Id: str
    Nome: str


class NotaFiscal(BaseModel):
    DataEmissao: datetime
    Numero: int
    Serie: int
    Chave: Optional[str]
    ValorTotal: float
    ValorTotalProdutos: float
    Cfop: Optional[str] = None
    StringXML: Optional[str] = None


class InfosAdicionais(BaseModel):
    EntregaAgendada: bool
    Portabilidade: bool
    CartaoPostagem: Optional[str] = None
    CodigoAdmnistrativo: Optional[str] = None
    ContratoCorreios: Optional[str] = None
    DataAgendamento: Optional[str] = None
    PeriodoEntregaAgendamento: Optional[str] = None
    Cluster: Optional[str] = None
    TecnologiaDeAcesso: Optional[str] = None
    Acronimo: Optional[str] = None
    IdCliente: Optional[str] = None
    IdDestinatario: Optional[str] = None
    SegmentoCliente: Optional[str] = None


class DispatchRequest(BaseModel):
    CriacaoPedido: datetime
    NumeroPedido: str
    NumeroPedidoMarketplace: Optional[str]
    NumeroPedidoErp: Optional[str]
    NumeroPedidoAux: str
    CanalDeVenda: Optional[CanalDeVenda]
    Warehouse: Optional[Warehouse]
    Itens: List[Item]
    NotaFiscal: Optional[NotaFiscal]
    InfosAdicionais: Optional[InfosAdicionais]
