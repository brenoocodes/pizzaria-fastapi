from passlib.context import CryptContext

password_criptografado = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_senha_criptografada(senha):
    return password_criptografado.hash(senha)

def verificar_senha(senha, senha_criptografado):
    return password_criptografado.verify(senha, senha_criptografado)