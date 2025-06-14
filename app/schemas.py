from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    nome_completo: str
    cpf: str
    email: str
    user_type: str

class UserCreate(BaseModel):
    nome_completo: str
    cpf: str
    email: str
    user_type: str
    senha: str  # senha adicionada aqui também

class UserRead(UserBase):
    id_user: int
    class Config:
        from_atributes = True

class VotacaoCreate(BaseModel):
    titulo: str
    descricao: Optional[str]
    status: Optional[str] = "aberta"
    permite_candidatura: bool
    data_inicio: datetime
    data_fim: datetime

class CandidaturaCreate(BaseModel):
    id_user: int
    id_votacao: int
    detalhes: Optional[str]
    status: Optional[str] = "pendente"

class OpcaoCreate(BaseModel):
    id_votacao: int
    titulo: str
    detalhes: Optional[str]

class LoginUpdate(BaseModel):
    email: Optional[EmailStr]
    senha: Optional[str]

class CandidaturaUpdate(BaseModel):
    detalhes: Optional[str]
    status: Optional[str]

class VotacaoUpdate(BaseModel):
    status: Optional[str]
    titulo: Optional[str]
    descricao: Optional[str]
    data_fim: Optional[datetime]

class OpcaoUpdate(BaseModel):
    titulo: Optional[str]
    detalhes: Optional[str]

class VotoCreate(BaseModel):
    id_user: int
    id_votacao: int
    id_opcao: int
    data_voto: datetime





















class LoginRequest(BaseModel):
    email: str
    senha: str

class UserResponse(BaseModel):
    id_user: int
    nome_completo: str
    email: str

    class Config:
        model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserBase


class CandidaturaInfo(BaseModel):
    id_candidatura: int
    id_votacao: int
    id_user: int
    detalhes: Optional[str]
    titulo: str
    nome_completo: str 
