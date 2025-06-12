from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id_user = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome_completo = Column(Text)
    cpf = Column(Text)
    email = Column(Text)
    user_type = Column(Text)

    logins = relationship("Login", back_populates="user")
    votos = relationship("Voto", back_populates="user")
    candidaturas = relationship("Candidatura", back_populates="user")

class Login(Base):
    __tablename__ = "login"
    id_login = Column(Integer, primary_key=True, autoincrement=True)
    senha = Column(Text)
    id_user = Column(Integer, ForeignKey("user.id_user"))

    user = relationship("User", back_populates="logins")

class Votacao(Base):
    __tablename__ = "votacao"
    id_votacao = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(Text)
    descricao = Column(Text)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    status = Column(Text)
    permite_candidatura = Column(Boolean)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"))

    categoria = relationship("Categoria", back_populates="votacoes")
    opcoes = relationship("Opcoes", back_populates="votacao")
    votos = relationship("Voto", back_populates="votacao")
    candidaturas = relationship("Candidatura", back_populates="votacao")

class Categoria(Base):
    __tablename__ = "categorias"
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nome_categoria = Column(Text)

    votacoes = relationship("Votacao", back_populates="categoria")

class Opcoes(Base):
    __tablename__ = "opcoes"
    id_opcao = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(Text)
    detalhes = Column(Text)
    id_votacao = Column(Integer, ForeignKey("votacao.id_votacao"))

    votacao = relationship("Votacao", back_populates="opcoes")
    votos = relationship("Voto", back_populates="opcao")

class Voto(Base):
    __tablename__ = "voto"
    id_voto = Column(Integer, primary_key=True, autoincrement=True)
    data_voto = Column(DateTime,default=datetime.utcnow)
    voto_publico = Column(Boolean)
    id_user = Column(Integer, ForeignKey("user.id_user"))
    id_votacao = Column(Integer, ForeignKey("votacao.id_votacao"))
    id_opcao = Column(Integer, ForeignKey("opcoes.id_opcao"))

    user = relationship("User", back_populates="votos")
    votacao = relationship("Votacao", back_populates="votos")
    opcao = relationship("Opcoes", back_populates="votos")

class Candidatura(Base):
    __tablename__ = "candidatura"
    id_candidatura = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Text)
    id_user = Column(Integer, ForeignKey("user.id_user"))
    id_votacao = Column(Integer, ForeignKey("votacao.id_votacao"))
    detalhes = Column(Text)

    user = relationship("User", back_populates="candidaturas")
    votacao = relationship("Votacao", back_populates="candidaturas")
