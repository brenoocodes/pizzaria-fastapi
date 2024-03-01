import uvicorn
from src.routes.funcionarios.index import *
from src.routes.categorias.index import *
from src.routes.produtos.index import *
from src.routes.pedidos.post import *
from src.routes.pedidos.get import *
from src.routes.pedidos.delete import *
from src.config.login import *

# if __name__ == "__main__":
#     uvicorn.run("src.configure:app", port=5000, reload=True)
