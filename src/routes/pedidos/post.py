from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models import models
from src.schemas.pedidos.index import Pedidos, ProdutosPedidos
from src.config.login import logado


@router.post("/pedidos", status_code=status.HTTP_201_CREATED)
async def criar_pedidos(pedido: Pedidos, db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        novo_pedido = models.Pedidos(mesa=pedido.mesa, status="Iniciado para a cozinha", finalizado=False, funcionarios_matricula=user.get('id'))  # Corrigido aqui
        db.add(novo_pedido)
        db.commit()
        db.refresh(novo_pedido)

        return {'mensagem': "Novo pedido repassado a cozinha com sucesso", "pedido": novo_pedido}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


@router.post("/pedidos/{id}/produtos", status_code=status.HTTP_201_CREATED)
async def adicionar_produtos_ao_pedido(db: db_dependency, user: logado, id:int, produtos:ProdutosPedidos):
    if user is None:
            raise HTTPException(status_code=401, detail='Você não está logado')
    try:
      produto_existente = db.query(models.Produtos).filter(models.Produtos.id == produtos.produto_id).first()
      if not produto_existente:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não existe este produto")
      pedido_existente = db.query(models.Pedidos).filter(models.Pedidos.id == id).first()
      if not pedido_existente:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não existe este pedido")
      
      novo_produto = models.PedidosProdutos(
          pedido_id = pedido_existente.id,
          produto_id = produtos.produto_id,
          preco_unitario = produto_existente.preco,
          quantidade = produtos.quantidade
      )
      db.add(novo_produto)
      db.commit()

      return f"Novo produto cadastrado com sucesso ao pedido de id {pedido_existente.id}"
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")



app.include_router(router)
