from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.configure import db_dependency, router, SECRET_KEY, ALGORITHM, app
from src.models.models import Funcionarios
from sqlalchemy.orm import Session
from typing import Annotated
from src.config.senhas import verificar_senha

ouauth2_bearer = OAuth2PasswordBearer(tokenUrl='/login')



class FuncionarioSemSenha(BaseModel):
    matricula: int
    nome: str
    email: str
    administrador: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    funcionario: FuncionarioSemSenha


def criar_token_acesso(email: str, user_id: int,adm: bool, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id, 'administrador': adm}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM) 

class Login(BaseModel):
    username: str
    password: str


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(login: Login, db: db_dependency):
    try:
        funcionario_logar = login.username
        print(funcionario_logar)
        if "@" in funcionario_logar:
            funcionario_existente = db.query(Funcionarios).filter(Funcionarios.email == funcionario_logar).first()
        else:
            funcionario_existente = db.query(Funcionarios).filter(Funcionarios.matricula == funcionario_logar).first()
        if not funcionario_existente:
            return {'mensagem': 'Funcionário não cadastrado'}
        senha = login.password
        print(senha)
        if senha is None:
            return{'mensagem': 'Preencha sua senha'}
        if verificar_senha(senha, funcionario_existente.senha) == True:
            token = criar_token_acesso(funcionario_existente.email, funcionario_existente.matricula, funcionario_existente.administrador, timedelta(days=30))
            reponse = {
                'token': token,
                'funcionario_matricula': funcionario_existente.matricula,
                'funcionario_nome': funcionario_existente.nome,
                'funcionario_email': funcionario_existente.email,
                'funcionario_administrador': funcionario_existente.administrador
            }
            return reponse
        else:
            return {'senha incorreta'}
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro ao logar {e}')

async def verificar_login(token: Annotated[str, Depends(ouauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: bool = payload.get('administrador')
        
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Usuário inválido')
        return {'username': username, 'id': user_id, 'is_admin': is_admin}  

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token não é mais válido')


logado = Annotated[dict, Depends(verificar_login)]
    
app.include_router(router)
