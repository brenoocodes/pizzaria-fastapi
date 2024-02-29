from fastapi import status, HTTPException
from src.configure import app, router, db_dependency
from fastapi.responses import JSONResponse
from src.models import models
from src.schemas.categorias.index import Categoria
from src.config.login import logado
from sqlalchemy.orm import joinedload


@router.get("/categorias", status_code=status.HTTP_200_OK)
async def buscar_categorias(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    
    try:
        categorias = db.query(models.Categorias).all()
        lista_de_categorias = []
        for categoria in categorias:
            categoria_atual = {}
            categoria_atual['id'] = categoria.id
            categoria_atual['nome'] = categoria.nome
            lista_de_produtos = []
            for produto in categoria.produtos:
                produto_atual = {}
                produto_atual['id'] = produto.id
                produto_atual['nome'] = produto.nome
                produto_atual['banner'] = produto.banner
                lista_de_produtos.append(produto_atual)
            if len(lista_de_produtos) == 0:
                categoria_atual['produtos'] = 'Ainda não foi associado nenhum produto a essa categoria'
            else:
                categoria_atual['produtos'] = lista_de_produtos
            lista_de_categorias.append(categoria_atual)
        if len(lista_de_categorias) == 0:
            return JSONResponse({'mensagem': 'Você ainda não cadastrou nenhuma categoria'})
        return lista_de_categorias


    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Ocorreu um erro: {e}')





@router.post("/categorias", status_code=status.HTTP_201_CREATED)
async def criar_categorias(categoria: Categoria, db: db_dependency, user: logado):
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        categoria_existente = db.query(models.Categorias).filter(models.Categorias.nome == categoria.nome).first()
        if categoria_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria já cadastrada")
        nova_categoria = models.Categorias(nome=categoria.nome)
        db.add(nova_categoria)
        db.commit()
        return {'mensagem': f"A categoria {categoria.nome} foi adicionada com sucesso"}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Ocorreu um erro: {e}')




app.include_router(router)