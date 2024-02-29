from fastapi import FastAPI, File, UploadFile, Form, status, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from pydantic import BaseModel
from src.configure import app, router, db_dependency
from src.models import models
from src.config.login import logado
from PIL import Image
import os
import uuid

IMAGEDIR = "src/static/images"

@router.get("/produtos", status_code=status.HTTP_200_OK)
async def buscar_produtos(db: db_dependency):
    # if user is None:
    #     raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        def buscar_imagem(nome_arquivo):
            path = f"{IMAGEDIR}/{nome_arquivo}"
            return FileResponse(path)
          
        produtos = db.query(models.Produtos).all()
        lista_de_produtos = []
        for produto in produtos:
            produto_atual = {}
            produto_atual['id'] = produto.id
            produto_atual['nome'] = produto.nome
            produto_atual['preco'] = produto.preco
            produto_atual['banner'] = f"/static/images/{produto.banner}"
            lista_de_produtos.append(produto_atual)
        if len(lista_de_produtos) == 0:
            return JSONResponse({'mensagem': 'Você ainda não cadastrou nenhuma categoria'})
        return lista_de_produtos
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


@router.get("/produtos/{id}", status_code=status.HTTP_200_OK)
async def buscar_produto_por_id(db:db_dependency, user:logado, id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        produto = db.query(models.Produtos).filter(models.Produtos.id == id).first()
        if not produto:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esse produto não existe")
        produto_atual = {}
        produto_atual = {}
        produto_atual['id'] = produto.id
        produto_atual['nome'] = produto.nome
        produto_atual['preco'] = produto.preco
        produto_atual['banner'] = f"/static/images/{produto.banner}"
        return produto_atual
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")



@router.post("/produtos", status_code=status.HTTP_201_CREATED)
async def criar_produto(db: db_dependency, user: logado, nome: str = Form(...), preco: str = Form(...), categoria_id: str = Form(...), file: UploadFile = File(None)):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')

    try:
        produto_existente = db.query(models.Produtos).filter(models.Produtos.nome == nome).first()
        if produto_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto já cadastrado")

        categoria_existente = db.query(models.Categorias).filter(models.Categorias.id == categoria_id).first()
        if not categoria_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não existe essa categoria")

        banner_filename = 'banner.png'  # Valor padrão para o banner
        if file is not None:
            file.filename = f"{uuid.uuid4()}.png"
            contents = await file.read()
            with open(f"{IMAGEDIR}/{file.filename}", "wb") as f:
                f.write(contents)
            banner_filename = file.filename

            # Redimensionar a imagem para 350x350 pixels
            img_path = os.path.join(IMAGEDIR, banner_filename)
            img = Image.open(img_path)
            img.thumbnail((350, 350))
            img.save(img_path)

        novo_produto = models.Produtos(
            nome=nome,
            preco=preco,
            banner=banner_filename,
            categoria_id=categoria_id
        )
        db.add(novo_produto)
        db.commit()
        return {'mensagem': 'Novo produto cadastrado com sucesso'}

    except Exception as e:
        print("Erro:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


def delete_old_image_if_exists(produto_existente):
    old_banner_filename = produto_existente.banner
    if old_banner_filename:
        old_img_path = os.path.join(IMAGEDIR, old_banner_filename)
        if os.path.exists(old_img_path):
            os.remove(old_img_path)

@router.put("/produtos/{id}", status_code=status.HTTP_200_OK)
async def alterar_produto(
    db: db_dependency, 
    user: logado, 
    id: int, 
    nome: Optional[str] = Form(None),
    preco: Optional[float] = Form(None),
    categoria_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if not user.get('is_admin', False):
            raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        
        produto_existente = db.query(models.Produtos).filter(models.Produtos.id == id).first()
        if not produto_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
        
        if nome is not None:
            produto_existente.nome = nome
        
        if preco is not None:
            produto_existente.preco = preco
        
        if categoria_id is not None:
            categoria_existente = db.query(models.Categorias).filter(models.Categorias.id == categoria_id).first()
            if not categoria_existente:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Não existe essa categoria")
            produto_existente.categoria_id = categoria_id

        if file is not None:
            # Excluir a imagem antiga, se existir
            delete_old_image_if_exists(produto_existente)

            file.filename = f"{uuid.uuid4()}.png"
            contents = await file.read()
            with open(f"{IMAGEDIR}/{file.filename}", "wb") as f:
                f.write(contents)
            banner_filename = file.filename

            # Redimensionar a imagem para 350x350 pixels
            img_path = os.path.join(IMAGEDIR, banner_filename)
            img = Image.open(img_path)
            img.thumbnail((350, 350))
            img.save(img_path)

            produto_existente.banner = banner_filename

        db.commit()
        return {"message": "Produto alterado com sucesso"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")



app.include_router(router)