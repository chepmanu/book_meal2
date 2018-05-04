from flask import Flask, request, jsonify, make_response, abort
from werkzeug.security  import generate_password_hash, check_password_hash
# from .auth import generate_token, token_required
import os
## from flask_jwt_extended import (
#     JWTManager, jwt_required, create_access_token,
#     get_jwt_identity
# ) 
import jwt
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
#BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__) 


# app.config['SECRET_KEY'] = 'ER9U9U9N9EUR'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(BASE_DIR, 'bookmeal3.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
# db = SQLAlchemy(app)
# ma = Marshmallow(app)



# app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
# jwt = JWTManager(app)

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'message':'Token is missing!'}), 401

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			current_user = User.query.filter_by(email=data['email']).first()
		except:
			return jsonify({'message': 'Token is invalid!'}), 401
		return f(current_user, *args, **kwargs)

	return decorated 
### To add new user during signup
@app.route('/api/v2/auth/signup', methods=['POST'])
def signup():
    username = request.get_json().get('username', None)
    password = request.get_json().get('password')
    email = request.get_json().get('email', None)
    is_admin = request.get_json().get('is_admin', None)

    encrypted_password =generate_password_hash(password, method='sha256')

    if not is_admin:
         is_admin = False
    # if not verify_email(email):
    #      return jsonify({"messsage":"email is taken", "status":409}), 409
    user = User(username=username, password_hash=encrypted_password, email=email,is_admin=is_admin)
    db.session.add(user)
    db.session.commit()

    #return jsonify({'token': generate_token(user.email)})
    return jsonify({"message":"successful sign up"})
##### During log in

# Get username and password from request then login user if successfull
@app.route('/api/v2/auth/signin', methods=['POST'])
def login():
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    if not username:
        return jsonify({"message":"Username required"}) 
    if not password:
        return jsonify({"message":"Password required"}) 
    user = User.query.filter_by(username=username).first() 
    if not user:
        return jsonify({"message":"User not found"})
    print(password)
    print(user.password_hash) 
    if check_password_hash(user.password_hash, password):
        token = jwt.encode({'email': user.email, 'exp' : datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        print(token)
        return jsonify({"token":token.decode('UTF-8')})
        # access_token = create_access_token(identity=user.email)
        # return jsonify(access_token=access_token), 200

    
   
    return jsonify({"message":"wrong crediemnbtald"}) , 401
    
      
####### TO add a meal for a given user
@app.route('/api/v2/meals', methods=['POST'])
#@token_required
def add_meal():
    food = request.get_json().get('food')
    price = request.get_json().get('price')
    #Create an instance of Meal
    meal = Meal(food=food, price=price)
    meal_in_sytem = Meal.query.filter_by(food=food).first()
    
    db.session.add(meal)
    db.session.commit()
    #user.add_meal(meal)
    return jsonify({'message':'meal added'}), 201

#To get meal option by admin
@app.route('/api/v2/meals', methods=['GET'])
#@token_required
def getmeals_endpoint(current_user):
    # if not current_user.is_admin:
    #     return jsonify({'message':'you must an admin','status':401}), 401
    meals = Meal.query.all()
    results = meals_schema.dump(meals).data
    return jsonify({"meals":results})

#Select meal from menu
@app.route('/api/v2/meal/<int:id>', methods=['GET'])
#@token_required
def get_meal( id):
    meal = Menu.query.get(id)
    if not meal:
        return({"message":"meal not found"})
    print(meal.meals)
    meal_data = Meal.query.get(meal.meals)
    print(meal_data.food)
    #result = meals_schema.dump(meal_data).data 
    return jsonify({"Meal":[meal_data.food, meal_data.price]}) 
    
    


#update a meal option by admin
@app.route('/api/v2/meal/<int:id>', methods=['PUT'])
#@token_required
def mordify_meal(id):
    # if not current_user.is_admin:
    #     return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    new_food = request.get_json().get('food')
    new_price = request.get_json().get('price')
    
    meal = Meal.query.filter_by(meal_id=id).first()
    
    if new_food:
        meal.food = new_food 
    if new_price:
        meal.price = new_food 

    db.session.add(meal)
    db.session.commit()

    return jsonify({"message":"meal updated"})

#Remove  A meal option
@app.route('/api/v2/meal/<int:id>', methods=['DELETE'])
#@token_required
def delete( id):
    # if not current_user.is_admin:
    #     return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    meal = Meal.query.filter_by(meal_id=id).first()
    if not meal:
        return({"message":"Meal not found"}), 404
    
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message":"Meal deleted"}), 404

#Set menu for a day
@app.route('/api/v2/menu', methods=['POST'])
#@token_required
def setmenu():
    # if not current_user.is_admin:
    #     return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
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
@app.route('/api/v2/menu', methods=['GET'])
#@token_required
def getmenu_endpoint():
    menu = Menu.query.all()
    results = menu_schema.dump(menu).data
    return jsonify({"menu":results})


#Select meal from menu
@app.route('/api/v2/orders', methods=['POST'])
#@token_required
def meal():
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
@app.route('/api/v2/orders')
def allorders_endpoint():
    # if not current_user.is_admin:
    #     return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    orders = Order.query.all()
    result = orders_schema.dump(orders).data
    return jsonify({"orders":result})

#Modify an order
@app.route('/api/v2/order/<int:id>', methods=['PUT'])
#@token_required
def modifyorder_endpoint(id):
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
@app.route('/api/v2/order/<int:id>', methods=['GET'])
#@token_required
def getoneorder_endpoint(id):
    # if not current_user.is_admin:
    #     return jsonify({"message":"you must be an admin to perfom this operation", 'status':401}), 401
    order = Order.query.get(id)
    if not order:
        return jsonify({"message":"Order not found "}), 404 
    result = order_schema.dump(order).data 
    return jsonify({"message":result})
@app.route('/api/v2/users', methods=['GET'])
def users():
    users = User.query.all()
    result = users_schema.dump(users).data 
    return jsonify({"users":result})

