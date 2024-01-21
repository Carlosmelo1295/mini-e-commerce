from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # configuração do banco

db = SQLAlchemy(app)  # instancia do banco

# apos criar a classe, rodar o comando "flask shell" e criar a tabela com o comando "db.create_all()" e "db.session.commit()" para finalizar o commit
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


@app.route('/api/products/add', methods=["POST"])
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Successfully"})
    return jsonify({"message": "Invalid product data"}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
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
