from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from database.database import  db, ma
from config.swagger import template, swagger_config
from routes.conta_route import contas
from routes.cliente_route import clientes
from routes.porquinho_route import porquinhos

app = Flask(__name__)
port = 5001
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Cofre.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SWAGGER'] = {
    'title': 'Meu cofre - API',
    'uiversion': 3
            }

swagger = Swagger(app, template=template, config=swagger_config)

db.app=app
db.init_app(app)
ma.init_app(app)

# Registrando endpoints
app.register_blueprint(contas)
app.register_blueprint(clientes)
app.register_blueprint(porquinhos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host="0.0.0.0", port=port)

