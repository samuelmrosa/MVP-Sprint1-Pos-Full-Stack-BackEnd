from flask_openapi3 import OpenAPI, Tag, Info
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask import redirect
from model import Pedido, Session
from schemas import *

info = Info(title="Minha Primeira API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)


# tags
home_tag = Tag(name="Documentação", description="Escolha da documentação: Swagger, Redoc ou RapiDoc")
pedido_tag = Tag(name="Pedido", description="Cria, apresenta e remove pedidos do banco de dados")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi para escolha da documentação.
    """
    return redirect('/openapi')


@app.post('/pedido', tags=[pedido_tag],
          responses={"200": PedidoViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_pedido(form: PedidoSchema):
    """Adiciona um pedido
    """
    pedido = Pedido(
        id=form.id, 
        material=form.material,
        valor=form.valor,
        quantidade=form.quantidade,
        fornecedor=form.fornecedor,
)
    
    try:
        session = Session()
        session.add(pedido)
        session.commit()
        print("Pedido Inserido!")
        return apresenta_pedido(pedido), 200

    except IntegrityError as e:
        error_msg = "Erro ao adicionar pedido. O número de pedido já existe."
        print("erro: pedido já existente")
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Pedido não cadastrado."
        print("Erro!")
        return {"mesage": error_msg}, 400


@app.get('/pedidos', tags=[pedido_tag],
         responses={"200": ListagemPedidosSchema, "404": ErrorSchema})
def get_pedidos():
    """Retorna uma lista de pedidos
    """
    
    session = Session()
    pedidos = session.query(Pedido).all()

    if not pedidos:
        return {"pedidos": []}, 200
    print(pedidos)
    return apresenta_pedidos(pedidos), 200

@app.delete('/pedido', tags=[pedido_tag],
            responses={"200": PedidoDelSchema, "404": ErrorSchema})
def del_ped(query: PedidoBuscaSchema):
    """Deleta um pedido.
    """
    id = query.id
    session = Session()
    count = session.query(Pedido).filter(Pedido.id == id).delete()
    session.commit()

    if count:
        return {"mesage": "Pedido excluído", "pedido": id}
    error_msg = "Pedido não localizado"
    return {"mesage": error_msg}, 404
    