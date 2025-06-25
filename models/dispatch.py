from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Produto(BaseModel):
    Descricao: str
    Altura: Optional[float]
    Comprimento: Optional[float]
    Largura: Optional[float]
    Peso: Optional[float]
    Preco: float
    Quantidade: int
    SKU: str
    CodigoProduto: Optional[str]
    NumeroDeSerie: str
    TipoProduto: Optional[str]
    Fabricante: Optional[str]


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


class Destinatario(BaseModel):
    Nome: str
    CPFCNPJ: str
    Telefone: str
    Email: str
    Empresa: str
    Endereco: str
    Numero: str
    Complemento: str
    Bairro: str
    Cidade: str
    Estado: str
    Pais: str
    CEP: str
    IE: str


class Remetente(BaseModel):
    Nome: str
    NomeCentroDistribuicao: str
    CodigoCentroDistribuicao: str
    Endereco: str
    Numero: str
    Bairro: str
    Cidade: str
    Estado: str
    Pais: str
    CEP: str
    IE: str
    CPFCNPJ: str


class Tomador(BaseModel):
    Nome: str
    Endereco: str
    Numero: str
    Bairro: str
    Cidade: str
    Estado: str
    Pais: str
    CEP: str
    CPFCNPJ: str


class Frete(BaseModel):
    Transportadora: Transportadora
    Destinatario: Destinatario
    Remetente: Remetente
    Tomador: Tomador


class Item(BaseModel):
    IdUnico: str
    QuantidadeProdutos: int
    Volumes: int
    Produtos: List[Produto]
    Frete: Frete


class NotaFiscal(BaseModel):
    DataEmissao: str
    Numero: int
    Serie: int
    ValorTotal: float
    ValorTotalProdutos: float


class InfosAdicionais(BaseModel):
    EntregaAgendada: bool
    Portabilidade: bool


class DispatchRequest(BaseModel):
    CriacaoPedido: datetime
    DataPagamento: Optional[str]
    NumeroPedido: str
    NumeroPedidoAux: str
    Itens: List[Item]
    NotaFiscal: NotaFiscal
    InfosAdicionais: InfosAdicionais
