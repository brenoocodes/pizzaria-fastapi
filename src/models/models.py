import sys
from pathlib import Path
# Obtém o diretório do arquivo atual e seu diretório pai
file = Path(__file__).resolve()
parent = file.parent.parent.parent
# Adiciona o diretório pai ao sys.path
sys.path.append(str(parent))

from sqlalchemy import Boolean, Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.configure import Base, engine
from datetime import datetime

class Funcionarios(Base):
    __tablename__ = 'funcionarios'
    # Atributos da tabela funcionarios
    matricula = Column(Integer, unique=True, nullable=False, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    senha = Column(String(100), nullable=False)
    administrador = Column(Boolean, default=False)
    data_criacao = Column(DateTime, nullable=False, default=datetime.utcnow)


    pedidos = relationship('Pedidos', backref='funcionario')


class Categorias(Base):
    __tablename__ = 'categorias'
    # Atributos da tabela categorias
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nome = Column(String(120), unique=True, nullable=False)
    data_criacao = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relacionamento com os produtos
    produtos = relationship('Produtos', backref='categoria')

class Produtos(Base):
    __tablename__= 'produtos'
    # Atributos da tabela produtos
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    nome = Column(String(120), unique=True, nullable=False)
    preco = Column(Float, nullable=False, default=0.0)
    banner = Column(String(256), default='banner.png')
    data_criacao = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Chave estrangeira para a categoria
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False)


class Pedidos(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    mesa = Column(Integer, nullable=False)
    status = Column(String(120))
    finalizado = Column(Boolean, default=False)
    data_criacao = Column(DateTime, nullable=False, default=datetime.utcnow)

    #relacionamento com funcionario
    funcionarios_matricula = Column(Integer, ForeignKey('funcionarios.matricula'), nullable=False)
    
    pedidos_produto = relationship('PedidosProdutos', backref='pedido_produto')

class PedidosProdutos(Base):
    __tablename__ = 'pedidos_produtos'

    id = Column(Integer, unique=True, nullable=False, primary_key=True) 

    pedido_id = Column(Integer, ForeignKey('pedidos.id'))  # Corrigido para 'pedidos.id'
    produto_id = Column(Integer, ForeignKey('produtos.id'))

    preco_unitario = Column(Float)

    quantidade = Column(Integer, nullable=False, default=1)
    
    # Define a relação com a tabela de produtos
    produto = relationship('Produtos', backref='pedidos')

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)



# #Base.metadata.create_all(bind=engine, tables=[Categorias.__table__, Produtos.__table__])

# Base.metadata.drop_all(bind=engine, tables=[Pedidos.__table__, PedidosProdutos.__table__])
# Base.metadata.create_all(bind=engine, tables=[Pedidos.__table__, PedidosProdutos.__table__])
