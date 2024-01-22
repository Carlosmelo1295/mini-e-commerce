from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha_chave'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # configuração do banco
login_manager = LoginManager()

db = SQLAlchemy(app)  # instancia do banco
CORS(app)

login_manager.init_app(app)
login_manager.login_view = 'login'  # Login manager faz o gerenciamento dos usuários para sabermos quem está logado


# apos criar a classe, rodar o comando "flask shell" e criar a tabela com o comando "db.create_all()" e "db.session.commit()" para finalizar o commit
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


# ao criar outra tabela, rodar
# >>> db.drop_all()
# >>> db.create_all()
# >>> db.session.commit()
# >>> exit()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)

#usado para recuperar o usuário sempre que tentar acessar uma rota protegida
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))#user id recuperado dos cokies

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()

    if user and data.get("password") == user.password:
        login_user(user)
        return jsonify({"message": "Login Successfully"})

    return jsonify({"message": "Access denied"}), 401


@app.route('/api/products/add', methods=["POST"])
@login_required # diz para a rota que só pode ser acessada por usuários
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Successfully"})
    return jsonify({"message": "Invalid product data"}), 400


@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted Successfully"})
    return jsonify({"message": "Product not found"}), 404


@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
        })
    return jsonify({"message": "Product not found"}), 404


@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required

def update_products(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    if 'name' in data or 'price' in data or 'description' in data:
        product.name = data['name']
        product.price = data['price']
        product.description = data['description']
        db.session.commit()
    return jsonify({"message": "Product updated Successfully"})


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()

    if not products:
        return jsonify({'message': 'No product found'}), 404

    list_of_products = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
        }
        list_of_products.append(product_data)

    return list_of_products


@app.route('/')
def hello_word():
    return 'Hello World'


if __name__ == "__main__":
    app.run(debug=True)
