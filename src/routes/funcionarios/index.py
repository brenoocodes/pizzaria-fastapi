from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from src.configure import app, router, db_dependency
from src.models import models
from src.config.senhas import *
from src.schemas.funcionarios.index import Funcionarios, FuncionarioPut
from src.config.login import logado



@router.get("/funcionarios", status_code=status.HTTP_200_OK)
async def buscar_funcionarios(db: db_dependency, user: logado):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    try:
        funcionarios = db.query(models.Funcionarios).all()
        lista_de_funcionarios = []
        for funcionario in funcionarios:
            funcionario_atual = {}
            funcionario_atual['matricula'] = funcionario.matricula
            funcionario_atual['nome'] = funcionario.nome
            funcionario_atual['email'] = funcionario.email
            funcionario_atual['admin'] = funcionario.administrador
            lista_de_funcionarios.append(funcionario_atual)
        return lista_de_funcionarios
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

@router.get("/funcionarios/{matricula}", status_code=status.HTTP_200_OK)
async def buscar_funcionario_por_id(db: db_dependency, user: logado, matricula: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        funcionario = db.query(models.Funcionarios).filter(models.Funcionarios.matricula == matricula).first()
        if not funcionario:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esse funcionário não existe")
        funcionario_atual = {}
        funcionario_atual['matricula'] = funcionario.matricula
        funcionario_atual['nome'] = funcionario.nome
        funcionario_atual['email'] = funcionario.email
        funcionario_atual['admin'] = funcionario.administrador
        
        return JSONResponse(funcionario_atual)

    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")
         


@router.post("/funcionarios", status_code=status.HTTP_201_CREATED)
async def criar_funcionarios(funcionario: Funcionarios, db: db_dependency):
    try:
        funcionario_existente = db.query(models.Funcionarios).filter(models.Funcionarios.email == funcionario.email).first()
        if funcionario_existente:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Funcionário já existe")

        # Se o funcionário não existir, cria um novo
        senha = gerar_senha_criptografada(funcionario.senha)
        novo_funcionario = models.Funcionarios(nome=funcionario.nome, email=funcionario.email, senha=senha, administrador=funcionario.administrador)
        db.add(novo_funcionario)
        db.commit()
        return {'message': 'Novo funcionário criado com sucesso', 'data': funcionario}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")


@router.put("/funcionarios/{matricula}", status_code=status.HTTP_200_OK)
async def modificar_funcionario(db: db_dependency, user: logado, funcionario: FuncionarioPut, matricula: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        funcionario_existente = db.query(models.Funcionarios).filter(models.Funcionarios.matricula == matricula).first()
        if not funcionario_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
        if funcionario.email != funcionario_existente.email:
            email_existente = db.query(models.Funcionarios).filter(models.Funcionarios.email == funcionario.email).first()
            if email_existente:
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
        if funcionario.nome is not None:
            funcionario_existente.nome = funcionario.nome
        if funcionario.email is not None:
            funcionario_existente.email = funcionario.email
        if funcionario.senha is not None:
            senha = gerar_senha_criptografada(funcionario.senha)
            funcionario_existente.senha = senha
        if funcionario.administrador is not None:
            funcionario_existente.admin = funcionario.administrador
        db.commit()
        db.refresh(funcionario_existente)

        funcionario_atualizado = {
            "matricula": funcionario_existente.matricula,
            "nome": funcionario_existente.nome,
            "email": funcionario_existente.email,
            "administrador": funcionario_existente.administrador
        }
        return {"message": "Funcionário atualizado com sucesso", "funcionario": funcionario_atualizado}
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um error: {e}")

@router.delete("/funcionarios/{matricula}", status_code=status.HTTP_200_OK)
async def excluir_funcionario(db: db_dependency, user: logado, matricula: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Você não está logado')
    if not user.get('is_admin', False):
        raise HTTPException(status_code=403, detail='Você não tem permissão para acessar esta funcionalidade')
    try:
        funcionario_existente = db.query(models.Funcionarios).filter(models.Funcionarios.matricula == matricula).first()
        if not funcionario_existente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")
        
        if user.get('user_id') == matricula:
            print(user.get('user_id'))
            print(matricula)
            raise HTTPException(status_code=403, detail='Você não pode excluir a si mesmo')

        db.delete(funcionario_existente)
        db.commit()
        return {"message": "Funcionário excluído com sucesso", "funcionario": funcionario_existente}

    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro: {e}")


app.include_router(router)