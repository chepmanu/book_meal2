import datetime
from werkzeug import generate_password_hash, check_password_hash


from . import ma, db

orders = db.Table('orders',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('order_id', db.Integer, db.ForeignKey('order.order_id'), primary_key=True)
)



class User(db.Model):
    __tablename__ ='users'

    user_id = db.Column(db.Integer , primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128) , unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean)
    orders = db.relationship('Order', secondary=orders,
        backref=db.backref('users_order', lazy=True)) 



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash , password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    # def authenticate(username, password):
    #     user = User.query.filter(User.username == username).first()
    #     if user and user.check_password(password):
    #         return user

    def identity(payload):
        user_id = payload['identity']
        return User.query.filter(User.id == payload['identity']).scalar()


class Meal(db.Model):
    __tablename__ = 'meals'
    meal_id = db.Column(db.Integer, primary_key=True)
    food = db.Column(db.String(128), unique=True)
    price = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    photo = db.Column(db.String(128), nullable=True)
    #user = db.relationship('User')
    

class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.menu_id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    completed = db.Column(db.Boolean, default=True)



    
    def save(self):
        db.session.add(self)
        db.session.commit()
class Menu(db.Model):
    menu_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    meals = db.Column(db.Integer, db.ForeignKey('meals.meal_id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ( 'username', 'password_hash', 'user_id', 'is_admin', 'orders')

class MealSchema(ma.Schema):
    class Meta:
        fields = ('food', 'price', 'user_id', 'timestamp', 'photo', 'meal_id')

class MenuSchema(ma.Schema):
    class Meta:
        fields = ('menu_id', 'user_id', 'meals', 'timestamp') 
class OrderSchema(ma.Schema):
    class Meta:
        fields = ('order_id', 'menu_id', 'timestamp')

users_schema = UserSchema(many=True)
user_schema = UserSchema()
meals_schema = MealSchema(many=True)
meal_schema = MealSchema()
menu_schema = MenuSchema(many=True)
orders_schema= OrderSchema(many=True)
order_schema = OrderSchema()
