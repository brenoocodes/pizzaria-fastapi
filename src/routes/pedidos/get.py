from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models import models
from src.schemas.pedidos.index import AlterarPedidos
from src.config.login import logado

@router.get("/pedidos", status_code=status.HTTP_200_OK)
def todos_os_pedidos(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        pedidos = db.query(models.Pedidos).all()
        lista_de_pedidos = []
        for pedido in pedidos:
            pedido_atual = {}
            pedido_atual['id'] = pedido.id
            pedido_atual['mesa'] = pedido.mesa
            pedido_atual['status'] = pedido.status
            pedido_atual['finalizado'] = pedido.finalizado
            pedido_atual['funcionario'] = pedido.funcionario.nome
            produtos_do_pedido = []
            valor_atual = 0
            for pedido_produto in pedido.pedidos_produto:
                produto_atual = {}
                produto_atual['id'] = pedido_produto.produto.id
                produto_atual['nome'] = pedido_produto.produto.nome
                produto_atual['preco'] = pedido_produto.preco_unitario
                produto_atual['quantidade'] = pedido_produto.quantidade
                if produto_atual['preco'] is not None:  # Verifica se o preço não é None
                    valor_atual += produto_atual['preco'] * produto_atual['quantidade']
                produtos_do_pedido.append(produto_atual)
            pedido_atual['produtos'] = produtos_do_pedido
            pedido_atual['valor_total'] = valor_atual
            lista_de_pedidos.append(pedido_atual)
        return lista_de_pedidos

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


app.include_router(router)
