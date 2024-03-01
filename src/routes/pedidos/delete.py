from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models import models
from src.schemas.pedidos.index import Pedidos, ProdutosPedidos
from src.config.login import logado


@router.delete("/pedidos/{id}", status_code=status.HTTP_200_OK)
def excluir_mesa(db: db_dependency, user: logado, id: int):
    if user is None:
            raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        pedido_existente = db.query(models.Pedidos).filter(models.Pedidos.id==id).first()
        if not pedido_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não existe este pedido")
        db.delete(pedido_existente)
        db.commit()
        return {'mensagem': 'Pedido excluido com sucesso', 'pedido': pedido_existente}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")
 

app.include_router(router)