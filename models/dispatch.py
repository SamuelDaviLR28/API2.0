from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Produto(BaseModel):
    Descricao: str
    Altura: Optional[float] = None
    Comprimento: Optional[float] = None
    Largura: Optional[float] = None
    Peso: Optional[float] = None
    Preco: float
    Quantidade: int
    SKU: str
    CodigoProduto: Optional[str] = None
    NumeroDeSerie: Optional[str] = None
    TipoProduto: Optional[str] = None
    Fabricante: Optional[str] = None

class Transportadora(BaseModel):
    PrevisaoDeEntrega: Optional[datetime] = None
    DataPrometida: Optional[datetime] = None
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
    CodigoAutorizacao: Optional[str] = None
    PrazoDiasUteis: Optional[int] = None
    PrazoEntregaFinal: Optional[datetime] = None
    ValorAR: float
    ValorAverbadoPago: float
    ValorDeclarado: float
    ValorFrete: float
    CNPJ: Optional[str] = None
    ResponsavelRecebimento: Optional[str] = None
    SenhaVerificacao: Optional[str] = None
    TipoOperacao: Optional[str] = None
    TipoDevolucao: Optional[str] = None
    MotivoDevolucao: Optional[str] = None
    Prioridade: bool
    TipoPrioridade: Optional[str] = None
    ServicosAdicionais: Optional[str] = None

class Destinatario(BaseModel):
    Nome: str
    CPFCNPJ: str
    Telefone: str
    TelefoneFixo: Optional[str] = None
    TelefoneAdicional: Optional[str] = None
    Email: str
    Empresa: str
    Endereco: str
    Numero: str
    Complemento: Optional[str] = None
    Bairro: str
    Cidade: str
    Estado: str
    Pais: str
    CEP: str
    IE: str
    Lat: Optional[float] = None
    Long: Optional[float] = None
    Referencia: Optional[str] = None

class Remetente(BaseModel):
    Nome: str
    Loja: Optional[str] = None
    NomeCentroDistribuicao: str
    CodigoCentroDistribuicao: str
    Endereco: str
    Numero: str
    Complemento: Optional[str] = None
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
    Complemento: Optional[str] = None
    Bairro: str
    Cidade: str
    Estado: str
    Pais: str
    CEP: str
    IE: Optional[str] = None
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
    Largura: Optional[float] = None
    Peso: Optional[float] = None
    Altura: Optional[float] = None
    Comprimento: Optional[float] = None
    Formato: Optional[str] = None
    Produtos: List[Produto]
    Frete: Frete

class NotaFiscal(BaseModel):
    DataEmissao: datetime
    Numero: int
    Serie: int
    Cfop: Optional[str] = None
    Chave: Optional[str] = None
    ValorTotal: float
    ValorTotalProdutos: float
    StringXML: Optional[str] = None

class InfosAdicionais(BaseModel):
    CartaoPostagem: Optional[str] = None
    CodigoAdmnistrativo: Optional[str] = None
    ContratoCorreios: Optional[str] = None
    EntregaAgendada: bool
    DataAgendamento: Optional[datetime] = None
    PeriodoEntregaAgendamento: Optional[str] = None
    Cluster: Optional[str] = None
    TecnologiaDeAcesso: Optional[str] = None
    Acronimo: Optional[str] = None
    IdCliente: Optional[str] = None
    IdDestinatario: Optional[str] = None
    Portabilidade: bool
    SegmentoCliente: Optional[str] = None

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
    CanalDeVenda: Optional[str] = None
    Warehouse: Optional[str] = None
    UnidadeDeNegocio: Optional[str] = None
    Rede: Optional[str] = None
    Campanha: Optional[str] = None
    Itens: List[Item]
    NotaFiscal: NotaFiscal
    InfosAdicionais: InfosAdicionais
