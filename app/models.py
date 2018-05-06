import datetime
from werkzeug import generate_password_hash, check_password_hash


from . import ma, db




class User(db.Model):
    __tablename__ ='users'

    user_id = db.Column(db.Integer , primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128) , unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean)
    orders = db.relationship('Order', backref='users', lazy=True) 



    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash , password)

    def save(self):
        db.session.add(self)
        db.session.commit()

   

    def identity(payload):
        user_id = payload['identity']
        return User.query.filter(User.id == payload['identity']).scalar()


class Meal(db.Model):
    __tablename__ = 'meals'
    meal_id = db.Column(db.Integer, primary_key=True)
    food = db.Column(db.String(128), unique=True, nullable=False)
    price = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    photo = db.Column(db.String(128), nullable=True)
    caterer = db.relationship('User')
    

class Order(db.Model):
    __tablename__ = 'order'
    order_id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.menu_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    completed = db.Column(db.Boolean, default=False)



    
    def save(self):
        db.session.add(self)
        db.session.commit()
class Menu(db.Model):
    menu_id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    meals = db.Column(db.Integer, db.ForeignKey('meals.meal_id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    caterer = db.relationship('User')

class OrderSchema(ma.Schema):
    class Meta:
        fields = ('order_id', 'menu_id','user_id', 'timestamp')

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ( 'username', 'user_id', 'is_admin', 'orders')

    orders = ma.List(ma.Nested(OrderSchema))

class MealSchema(ma.Schema):
    class Meta:
        fields = ('food', 'price', 'caterer', 'timestamp', 'photo', 'meal_id')
    caterer  =  ma.Nested(UserSchema)

class MenuSchema(ma.Schema):
    class Meta:
        fields = ('menu_id', 'user_id', 'meals', 'timestamp', 'caterer')
    caterer = ma.Nested(UserSchema)

users_schema = UserSchema(many=True)
user_schema = UserSchema()
meals_schema = MealSchema(many=True)
meal_schema = MealSchema()
menu_schema = MenuSchema(many=True)
orders_schema= OrderSchema(many=True)
order_schema = OrderSchema()
