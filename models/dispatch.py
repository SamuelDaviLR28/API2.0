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
    CNPJ: Optional[str] = None
    ResponsavelRecebimento: Optional[str] = None
    SenhaVerificacao: Optional[str] = None
    TipoOperacao: Optional[str] = None
    TipoDevolucao: Optional[str] = None
    MotivoDevolucao: Optional[str] = None
    TipoPrioridade: Optional[str] = None
    ServicosAdicionais: Optional[str] = None
    PrevisaoDeEntrega: Optional[str] = None
    DataPrometida: Optional[str] = None
    PrazoDiasUteis: Optional[int] = None
    PrazoEntregaFinal: Optional[str] = None
    CodigoAutorizacao: Optional[str] = None

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
    Bairro: Optional[str] = None
    Cidade: str
    Estado: str
    Pais: Optional[str] = None
    CEP: str
    IE: Optional[str] = None
    Loja: Optional[str] = None
    NomeCentroDistribuicao: Optional[str] = None
    CodigoCentroDistribuicao: Optional[str] = None

class Frete(BaseModel):
    Transportadora: Transportadora
    Destinatario: Pessoa
    Remetente: Pessoa
    Tomador: Optional[Pessoa] = None

class NotaFiscal(BaseModel):
    DataEmissao: datetime
    Numero: int
    Serie: int
    Chave: Optional[str] = None
    ValorTotal: float
    ValorTotalProdutos: Optional[float] = None
    Cfop: Optional[str] = None
    StringXML: Optional[str] = None

class InfosAdicionais(BaseModel):
    EntregaAgendada: Optional[bool] = False
    Portabilidade: Optional[bool] = False
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
    NumeroPedido: str
    NumeroPedidoMarketplace: Optional[str] = None
    NumeroPedidoErp: Optional[str] = None
    NumeroPedidoAux: str
    CanalDeVenda: Optional[CanalDeVenda] = None
    Warehouse: Optional[Warehouse] = None
    NotaFiscal: Optional[NotaFiscal] = None
    InfosAdicionais: Optional[InfosAdicionais] = None
    Itens: List[Item]
