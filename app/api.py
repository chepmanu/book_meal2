import jwt
from datetime import datetime, timedelta
from . models import User,meal_schema, users_schema, Meal, Menu, Order, OrderSchema,order_schema, user_schema,orders_schema, meals_schema, meal_schema,menu_schema
# local import
from instance.config import app_config
from flask import Flask, request, jsonify, make_response, abort, Blueprint, current_app
from werkzeug.security  import generate_password_hash, check_password_hash
# from .auth import generate_token, token_required
import os

from . import db

from .auth import token_required
from . validation import usernameValidate
## from flask_jwt_extended import (
#     JWTManager, jwt_required, create_access_token,
#     get_jwt_identity
# ) 

#BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# app.config['SECRET_KEY'] = 'ER9U9U9N9EUR'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(BASE_DIR, 'bookmeal3.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
# db = SQLAlchemy(app)
# ma = Marshmallow(app)


api = Blueprint('api', __name__)

# app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
# jwt = JWTManager(app)




### To add new user during signup
@api.route('/api/v2/auth/signup', methods=['POST'])
def signup():
	if not request.is_json:
		return jsoinfy({"message":"format not json"})
	username = request.get_json().get('username')
	password = request.get_json().get('password')
	email = request.get_json().get('email', None)
	is_admin = request.get_json().get('is_admin', None)
	err = usernameValidate(username)
	if err:
		return jsonify({"message":"invalid","errors":err}), 400
	encrypted_password =generate_password_hash(password, method='sha256')
	if not is_admin:
		is_admin = False
		
	user = User(username=username, password_hash=encrypted_password, email=email,is_admin=is_admin)
	db.session.add(user)
	db.session.commit()
	
	return jsonify({"message":"successful sign up"}), 201
##### During log in

# Get username and password from request then login user if successfull
@api.route('/api/v2/auth/signin', methods=['POST'])
def login():
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    if not username:
        return jsonify({"message":"Username required"}) 
    if not password:
        return jsonify({"message":"Password required"}) 
    user = User.query.filter_by(username=username).first()
    print(user.username) 
    if not user:
        return jsonify({"message":"User not found"})
     
    if check_password_hash(user.password_hash, password):
        print(current_app.config['SECRET'])
        token = jwt.encode({'email': user.email, 
                            'exp' : datetime.utcnow() + timedelta(minutes=30)}, 
                            current_app.config['SECRET'])
        print(token)
        return jsonify({"token":token.decode('UTF-8')})
        # access_token = create_access_token(identity=user.email)
        # return jsonify(access_token=access_token), 200

    
   
    return jsonify({"message":"wrong credentials"}) , 401
    
      
####### TO add a meal for a given user
@api.route('/api/v2/meals', methods=['POST'])
@token_required
def add_meal(current_user):
    if not current_user.is_admin:
        return jsonify({"message":"Unauthorized"}), 401
    food = request.get_json().get('food')
    price = request.get_json().get('price')
    #Create an instance of Meal
    meal = Meal(food=food, price=price, user_id=current_user.user_id)
    meal_in_sytem = Meal.query.filter_by(food=food).first()
    
    db.session.add(meal)
    db.session.commit()
    #user.add_meal(meal)
    return jsonify({'message':'meal added'}), 201

#To get meal option by admin
@api.route('/api/v2/meals', methods=['GET'])
@token_required
def getmeals_endpoint(current_user):
    if not current_user.is_admin:
        return jsonify({'message':'you must an admin'}), 401
         
    meals = Meal.query.all()
    results = meals_schema.dump(meals).data
    return jsonify({"meals":results})

#Select meal from menu
@api.route('/api/v2/menu/<int:id>', methods=['GET'])
@token_required
def get_meal(current_user, id):
    meal = Menu.query.get(id)
    print(id)
    if not meal:
        return jsonify({"message":"meal not found"}), 404
    print(meal.meals)
    meal_data = Meal.query.get(meal.meals)
    print(meal_data.food)
    #result = meals_schema.dump(meal_data).data 
    return jsonify({"Meal":[meal_data.food, meal_data.price]}) , 200
    
    


#update a meal option by admin
@api.route('/api/v2/meal/<int:id>', methods=['PUT'])
@token_required
def mordify_meal(current_user, id):
    if not current_user.is_admin:
        return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    new_food = request.get_json().get('food')
    new_price = request.get_json().get('price')
    
    meal = Meal.query.filter_by(meal_id=id).first()
    
    if new_food:
        meal.food = new_food 
    if new_price:
        meal.price = new_price 

    db.session.add(meal)
    db.session.commit()

    return jsonify({"message":"meal updated"})

#Remove  A meal option
@api.route('/api/v2/meal/<int:id>', methods=['DELETE'])
@token_required
def delete(current_user, id):
    if not current_user.is_admin:
        return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    meal = Meal.query.filter_by(meal_id=id).first()
    if not meal:
        return({"message":"Meal not found"}), 404
    
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message":"Meal deleted"}), 204

#Set menu for a day
@api.route('/api/v2/menu', methods=['POST'])
@token_required
def setmenu(current_user):
    if not current_user.is_admin:
        return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    id = request.get_json().get('id')

    meal = Meal.query.get(id)
    if not meal:
        return jsonify({"message":"meal cannot be found"}), 404
    print(meal.food)
    meal_in_menu = Menu.query.filter_by(meals=id).first()
    if not meal_in_menu:
        menu_item = Menu(meals=meal.meal_id)
        db.session.add(menu_item)
        db.session.commit()
    if meal_in_menu:
        return jsonify({"message":"meal already in menu"})

    
     
    return jsonify({"message":"success"})

#Get the menu for the day
@api.route('/api/v2/menu', methods=['GET'])
@token_required
def getmenu_endpoint(current_user):
    menu = Menu.query.all()
    results = menu_schema.dump(menu).data
    return jsonify({"menu":results})


#Select meal from menu
@api.route('/api/v2/orders', methods=['POST'])
@token_required
def meal(current_app):
    id = request.get_json().get('id')
    meal = Menu.query.get(id)
    if not meal:
        return jsonify({"message":"Meal not found in menu"}), 404
    meal1 = Meal.query.get(meal.meals)
    order = Order(menu_id=meal.meals)
    db.session.add(order)
    db.session.commit()
    results = meal_schema.dump(meal1).data
    return jsonify({"meal":results})


#Get all orders
@api.route('/api/v2/orders')
@token_required
def allorders_endpoint(current_user):
    if not current_user.is_admin:
         return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    orders = Order.query.all()
    result = orders_schema.dump(orders).data
    return jsonify({"orders":result})

#Modify an order
@api.route('/api/v2/order/<int:id>', methods=['PUT'])
@token_required
def modifyorder_endpoint(current_user, id):
    #Confirm if the id in the url has an order
    orders = Order.query.get(id)
    if not orders:
        return jsonify({"message":"order cannot be found"}), 404 
    #Confirm that the menu id provided in the body is in the menu
    menu_id = request.get_json().get('menu_id')
    menu_items = Menu.query.get(menu_id)
    if menu_items:
        if orders.completed == False:
            return jsonify({"message":"The order cannot be mordified"}) 
        orders.menu_id = menu_id
        db.session.add(orders)

        db.session.commit() 
        return jsonify({"message":"The order has been mordified"})
    return jsonify({"message":"The menu item cannot be found"})
    #If both ids are fine
    #Check if order is completed 
    

    
#Select order from orders
@api.route('/api/v2/order/<int:id>', methods=['GET'])
@token_required
def getoneorder_endpoint(current_user,id):
    if not current_user.is_admin:
        return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    order = Order.query.get(id)
    if not order:
        return jsonify({"message":"Order not found "}), 404 
    result = order_schema.dump(order).data 
    return jsonify({"message":result})

@api.route('/api/v2/users', methods=['GET'])
@token_required
def users(current_user):
    if not current_user.is_admin:
        return jsonify({"message":"unauthorisations"}), 401
    users = User.query.all()
    result = users_schema.dump(users).data 
    return jsonify({"users":result})

@api.route('/api/v2/meal/<int:id>', methods=['GET'])
@token_required 
def get_one_meal(current_user, id):
	meal =Meal.query.filter_by(meal_id=id).first()
	if not meal:
		return jsonify({"message":"meal not found"})
	result = meal_schema.dump(meal).data 
	return jsonify({"meal":result})