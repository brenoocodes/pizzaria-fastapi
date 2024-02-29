from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models import models
from src.schemas.pedidos.index import AlterarPedidos
from src.config.login import logado

router.put("/pedidos/{id_pedido}", status_code=status.HTTP_200_OK)
async def alterar_pedido(db: db_dependency, user: logado, id:int, alterar:AlterarPedidos):
    if user is None:
            raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        pedido_existente = db.query(models.Pedidos).filter(models.Pedidos.pedido_id == id).first()
        if not pedido_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não existe este pedido")
        
        if alterar.mesa is not None:
             pedido_existente.mesa = alterar.mesa
        if alterar.status is not None:
             pedido_existente.status = alterar.status
        if alterar.finalizado is not None:
             pedido_existente.finalizado = True
        
        db.commit()
        db.refresh(pedido_existente)

        if pedido_existente.finalizado == True:
             
             return JSONResponse()

        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")