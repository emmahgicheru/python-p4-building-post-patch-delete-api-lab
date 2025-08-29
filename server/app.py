#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)

    if request.method == 'GET':
        return make_response(bakery.to_dict(), 200)
    
    # PATCH
    name = request.form.get('name')
    if name:
        bakery.name = name.strip()
    try:
        db.session.commit()
        return make_response(bakery.to_dict(), 200)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    if not most_expensive:
        return make_response({'error': 'No baked goods found'}, 404)
    return make_response(most_expensive.to_dict(), 200)

# -------- POST --------

# Create a baked good from FORM data: name, price, bakery_id
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    price_raw = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    if not name or price_raw is None or not bakery_id:
        return make_response({'error': 'name, price, and bakery_id are required'}, 400)

    try:
        # Cast price from form string; works whether your column is Float or Integer
        price = float(price_raw)
        bg = BakedGood(
            name=name.strip(),
            price=price,
            bakery_id=int(bakery_id),
        )
        db.session.add(bg)
        db.session.commit()
        return make_response(bg.to_dict(), 201)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

# -------- DELETE --------

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    bg = BakedGood.query.filter_by(id=id).first()
    if not bg:
        return make_response({'error': 'BakedGood not found'}, 404)

    try:
        db.session.delete(bg)
        db.session.commit()
        return make_response({'message': f'BakedGood {id} deleted'}, 200)
    except Exception as e:
        db.session.rollback()
        return make_response({'error': str(e)}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)