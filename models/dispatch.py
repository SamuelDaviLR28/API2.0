from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class Produto(BaseModel):
    Descricao: Optional[str]
    Altura: Optional[float]
    Comprimento: Optional[float]
    Largura: Optional[float]
    Peso: Optional[float]
    Preco: Optional[float]
    Quantidade: Optional[int]
    SKU: Optional[str]
    CodigoProduto: Optional[str]
    NumeroDeSerie: Optional[str]
    TipoProduto: Optional[str]
    Fabricante: Optional[str]

class Transportadora(BaseModel):
    PrevisaoDeEntrega: Optional[datetime]
    DataPrometida: Optional[datetime]
    Id: Optional[str]
    Nome: Optional[str]
    NomeServico: Optional[str]
    IdServico: Optional[str]
    CodigoRastreio: Optional[str]
    ListaPostagem: Optional[str]
    Reversa: Optional[bool]
    Coleta: Optional[bool]
    Dispatch: Optional[bool]
    AlocacaoAutomatica: Optional[bool]
    CodigoAutorizacao: Optional[str]
    PrazoDiasUteis: Optional[int]
    PrazoEntregaFinal: Optional[datetime]
    ValorAR: Optional[float]
    ValorAverbadoPago: Optional[float]
    ValorDeclarado: Optional[float]
    ValorFrete: Optional[float]
    CNPJ: Optional[str]
    ResponsavelRecebimento: Optional[str]
    SenhaVerificacao: Optional[str]
    TipoOperacao: Optional[str]
    TipoDevolucao: Optional[str]
    MotivoDevolucao: Optional[str]
    Prioridade: Optional[bool]
    TipoPrioridade: Optional[str]
    ServicosAdicionais: Optional[str]

class DestinatarioRemetenteTomador(BaseModel):
    Nome: Optional[str]
    CPFCNPJ: Optional[str]
    Telefone: Optional[str] = None
    TelefoneFixo: Optional[str] = None
    TelefoneAdicional: Optional[str] = None
    Email: Optional[str] = None
    Empresa: Optional[str] = None
    Endereco: Optional[str]
    Numero: Optional[str]
    Complemento: Optional[str]
    Bairro: Optional[str]
    Cidade: Optional[str]
    Estado: Optional[str]
    Pais: Optional[str]
    CEP: Optional[str]
    IE: Optional[str]
    Lat: Optional[float] = None
    Long: Optional[float] = None
    Referencia: Optional[str] = None
    Loja: Optional[str] = None
    NomeCentroDistribuicao: Optional[str] = None
    CodigoCentroDistribuicao: Optional[str] = None

class Frete(BaseModel):
    Transportadora: Optional[Transportadora]
    Destinatario: Optional[DestinatarioRemetenteTomador]
    Remetente: Optional[DestinatarioRemetenteTomador]
    Tomador: Optional[DestinatarioRemetenteTomador]

class Item(BaseModel):
    IdUnico: Optional[str]
    QuantidadeProdutos: Optional[int]
    Volumes: Optional[int]
    Largura: Optional[float]
    Peso: Optional[float]
    Altura: Optional[float]
    Comprimento: Optional[float]
    Formato: Optional[str]
    Produtos: Optional[List[Produto]]
    Frete: Optional[Frete]

class NotaFiscal(BaseModel):
    DataEmissao: Optional[datetime]
    Numero: Optional[int]
    Serie: Optional[int]
    Cfop: Optional[str]
    Chave: Optional[str]
    ValorTotal: Optional[float]
    ValorTotalProdutos: Optional[float]
    StringXML: Optional[str]

class InfosAdicionais(BaseModel):
    CartaoPostagem: Optional[str]
    CodigoAdmnistrativo: Optional[str]
    ContratoCorreios: Optional[str]
    EntregaAgendada: Optional[bool]
    DataAgendamento: Optional[datetime]
    PeriodoEntregaAgendamento: Optional[str]
    Cluster: Optional[str]
    TecnologiaDeAcesso: Optional[str]
    Acronimo: Optional[str]
    IdCliente: Optional[str]
    IdDestinatario: Optional[str]
    Portabilidade: Optional[bool]
    SegmentoCliente: Optional[str]

class Pedido(BaseModel):
    CriacaoPedido: datetime
    DataPagamento: Optional[datetime]
    NumeroPedido: str
    NumeroPedidoMarketplace: Optional[str]
    NumeroPedidoErp: Optional[str]
    IdsAuxiliares: Optional[str]
    NumeroPedidoAux: Optional[str]
    Marketplace: Optional[str]
    Marca: Optional[str]
    Seller: Optional[str]
    CanalDeVenda: Optional[str]
    Warehouse: Optional[str]
    UnidadeDeNegocio: Optional[str]
    Rede: Optional[str]
    Campanha: Optional[str]
    Itens: List[Item]
    NotaFiscal: Optional[NotaFiscal]
    InfosAdicionais: Optional[InfosAdicionais]
