import jwt
from datetime import datetime, timedelta
from . models import User,meal_schema, users_schema, Meal, Menu, Order, OrderSchema,order_schema, user_schema,orders_schema, meals_schema, meal_schema,menu_schema
from instance.config import app_config
from flask import Flask, request, jsonify, make_response, abort, Blueprint, current_app
from werkzeug.security  import generate_password_hash, check_password_hash
import os
from  werkzeug.debug import get_current_traceback
from . import db
from .auth import token_required
from . validation import usernameValidate, emailValidate, passwordValidate, foodValidate, priceValidate


api = Blueprint('api', __name__)


@api.errorhandler(400)
def bad(err):
    return jsonify({"message":"Bad error, check data format"}),400
    #return jsonify({"message":str(err)}), 400

@api.errorhandler(500)
def internal_error(error):
    return jsonify({"message":"Internal server error"})

@api.errorhandler(404)
def internal_error(error):
    return jsonify({"message":"Page cannot be found, check you url"})


### To add new user during signup
@api.route('/api/v2/auth/signup', methods=['POST'])
def signup():
    if request.json is None:
        return jsonify({"message":"format not json"}), 400
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    email = request.get_json().get('email', None)
    print(email)
    is_admin = request.get_json().get('is_admin', None)
    err = usernameValidate(username)
    err1 = passwordValidate(password)
    err2 = emailValidate(email)
    if err:
        return jsonify({"message":"invalid", "errors":err}), 400
    if err1:
        return jsonify({"message":"invalid", "errors":err1}), 400
    if err2:
        return jsonify({"message":"invalid","errors":err2}), 400
    encrypted_password =generate_password_hash(password, method='sha256')
    if not is_admin:
        is_admin = False
    user = User.query.filter_by(username=username).first()
    check_user_email = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message":"please pick a different username"}), 409
    if check_user_email:
        return jsonify({"message":"email exists, please pick a different email"}), 404	
    user = User(username=username, password_hash=encrypted_password, email=email,is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"successful sign up"}), 201
##### During log in

# Get username and password from request then login user if successfull
@api.route('/api/v2/auth/signin', methods=['POST'])
def login():
    if request.json is None:
        return jsonify({"message":"json required"}), 400
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    err = usernameValidate(username)
    if err:
        return message({"message":"invalid", "invalid":err}), 400 
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message":"User not found"})
    if check_password_hash(user.password_hash, password):
        print(current_app.config['SECRET'])
        token = jwt.encode({'email': user.email, 
                            'exp' : datetime.utcnow() + timedelta(minutes=30)}, 
                            current_app.config['SECRET'])
        return jsonify({"username":username,"email":user.email,"token":token.decode('UTF-8')})
    return jsonify({"message":"wrong credentials"}) , 401

      
####### TO add a meal for a given user
@api.route('/api/v2/meals', methods=['POST'])
@token_required
def add_meal(current_user):
    if request.json is None:
        return jsonify({"message":"json format required"}), 400
    if not current_user.is_admin:
        return jsonify({"message":"Unauthorized"}), 401
    food = request.get_json().get('food')
    price = request.get_json().get('price')
    err = foodValidate(food)
    err1 = priceValidate(price)
    if err:
        return jsonify({"message":"invalid", "errors":err}), 400
    if err1:
        return jsonify({"message":"invalid", "error":err1}), 400
    #Create an instance of Meal
    food1 = Meal.query.filter_by(food=food).first()
    if food1:
        return jsonify({"message":"meal already exists"}), 409
    meal = Meal(food=food, price=price, user_id=current_user.user_id)
    db.session.add(meal)
    db.session.commit()
    return jsonify({'food':[food,price],'message':'meal added'}), 201

#To get meal option by admin
@api.route('/api/v2/meals', methods=['GET'])
@token_required
def getmeals_endpoint(current_user):
    if not current_user.is_admin:
        return jsonify({'message':'you must an admin'}), 401
         
    meals = Meal.query.all()
    results = meals_schema.dump(meals).data
    return jsonify({"meals":results}), 200

#Select meal from menu
@api.route('/api/v2/menu/<int:id>', methods=['GET'])
@token_required
def get_meal(current_user, id):
    meal = Menu.query.get(id)
    print(id)
    if not meal:
        return jsonify({"message":"meal not found"}), 404
    meal_data = Meal.query.get(meal.meals) 
    return jsonify({"Meal":[meal_data.food, meal_data.price]}) , 200


#update a meal option by admin
@api.route('/api/v2/meals/<int:id>', methods=['PUT'])
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
@api.route('/api/v2/meals/<int:id>', methods=['DELETE'])
@token_required
def delete(current_user, id):
    if not current_user.is_admin:
        return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    meal = Meal.query.filter_by(meal_id=id, user_id=current_user.user_id).first()
    if not meal:
        return({"message":"Meal not found"}), 404
    
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message":"Meal deleted"}), 200

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
    meal_in_menu = Menu.query.filter_by(meals=id).first()
    if not meal_in_menu:
        menu_item = Menu(meals=meal.meal_id, user_id=current_user.user_id)
        db.session.add(menu_item)
        db.session.commit()
    if meal_in_menu:
        return jsonify({"message":"meal already in menu"}), 409

    
     
    return jsonify({"message":"Menu item set"})

#Get the menu for the day
@api.route('/api/v2/menu', methods=['GET'])
@token_required
def getmenu_endpoint(current_user):
    menu = Menu.query.all()
    results = menu_schema.dump(menu).data
    return jsonify({"menu":results}), 200


#Make an order 
@api.route('/api/v2/orders', methods=['POST'])
@token_required
def meal(current_user):
    id = request.get_json().get('id')
    meal = Menu.query.filter_by(menu_id=id).first()
    if not meal:
        return jsonify({"message":"Meal not found in menu"}), 404
    meal1 = Meal.query.get(meal.meals)
    order = Order(menu_id=id, user_id=current_user.user_id)
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
        if orders.completed == True:
            return jsonify({"message":"The order cannot be mordified"}) 
        orders.menu_id = menu_id
        db.session.add(orders)

        db.session.commit() 
        return jsonify({"message":"The order has been mordified"})
    return jsonify({"message":"The menu item cannot be found"})
    

    
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
        print(current_user.username)
        return jsonify({"message":"unauthorisations"}), 401
    users = User.query.all()
    result = users_schema.dump(users).data 
    return jsonify({"users":result})


@api.route('/api/v2/meals/<int:id>', methods=['GET'])
@api.errorhandler(404)
@token_required 
def get_one_meal(current_user, id):
	meal =Meal.query.filter_by(meal_id=id).first()
	if not meal:
		return jsonify({"message":"meal not found"})
	result = meal_schema.dump(meal).data 
	return jsonify({"meal":result})