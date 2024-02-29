from pydantic import BaseModel
from typing import Optional

class Pedidos(BaseModel):
    mesa: int

class ProdutosPedidos(BaseModel):
    produto_id: int
    quantidade: int


class AlterarPedidos(BaseModel):
    mesa: Optional[int] = None
    status: Optional[str] = None
    finalizado: Optional[bool] = None