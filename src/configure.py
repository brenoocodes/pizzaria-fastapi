from fastapi import FastAPI, APIRouter
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from typing import Annotated


SECRET_KEY = "ne34943rh3rnr3h2ri4bf3#2232@3nf3ior2inrb23i32@9392i12n323jjei23i932urneh0120919090rr)(jwwehr9021902@)"
ALGORITHM = 'HS256'
# Instanciando o aplicativo FastAPI
app = FastAPI()

# Configuração do CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


router = APIRouter()



SQL = "postgresql://postgres.agaivybqwvdvzwdjctyj:9hFX86yG8jX0Dj2I@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
engine = create_engine(SQL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Corrigindo para chamar a função close()

db_dependency = Annotated[Session, Depends(get_db)]



@router.get("/")
def home():
    return {'Olá': 'Mundo'}


# Registrar o roteador de funcionários
app.include_router(router)
