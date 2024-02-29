from pydantic import BaseModel, EmailStr
from typing import Optional

class Funcionarios(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    administrador: bool

class FuncionarioPut(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    administrador: Optional[bool] = None
    