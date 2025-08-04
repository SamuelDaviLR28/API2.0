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
    NotaFiscal: NotaFiscal  # ✅ Agora obrigatório
    InfosAdicionais: InfosAdicionais  # ✅ Agora obrigatório


class CanalDeVenda(BaseModel):
    Id: str
    Nome: str
    Tipo: Optional[str] = None


class Warehouse(BaseModel):
    Id: str
    Nome: str


class DispatchRequest(BaseModel):
    CriacaoPedido: datetime
    DataPagamento: Optional[datetime] = None
    NumeroPedido: str
    NumeroPedidoMarketplace: Optional[str] = None
    NumeroPedidoErp: Optional[str] = None
    IdsAuxiliares: Optional[str] = None
    NumeroPedidoAux: Optional[str] = None
    Marketplace: Optional[str] = None
    Marca: Optional[str] = None
    Seller: Optional[str] = None
    CanalDeVenda: Optional[CanalDeVenda]  # ✅ Aceita objeto, sem = None
    Warehouse: Optional[Warehouse]        # ✅ Aceita objeto, sem = None
    UnidadeDeNegocio: Optional[str] = None
    Rede: Optional[str] = None
    Campanha: Optional[str] = None
    Itens: List[Item]
