from  werkzeug.debug import get_current_traceback
import re 


def usernameValidate(username):
    errors =[]
    if username is None:
        errors.append('Username required')
    
    if len(username)< 2:
        errors.append('Username too short')

    if  not re.match("^[a-zA-Z0-9_]*$", username):
        errors.append('Username should not contain any special characters apart from an underscore')

    if re.match("^[0-9]*$", username):
        errors.append('Username cannot be only intergers')


    
    return errors 

def passwordValidate(password):
    errors = []
    if password is None:
        errors.append('Password required')
    if len(password)<5:
        errors.append('password too short')


    return errors 

def emailValidate(email):
    errors = []
    if email is None:
         errors.append('email is required')
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        errors.append('email is invalid')

    return errors 


def foodValidate(food):
    errors = []
    if food is None:
        errors.append('food is required')
    if  not re.match("^[a-zA-Z0-9_]*$", food):
        errors.append('food should not contain any special characters apart from an underscore')
    
    if re.match("^[0-9]*$", food):
        errors.append('food name cannot be only intergers') 

    return errors 
    
def priceValidate(price):
    errors = []
    if not isinstance(price, int):
        errors.append('price should be an interger')
    if price is None:
        errors.append('price is required')
    if not re.match("^[0-9]*$", str(price)):
        errors.append('price can only contain intergers')
    if price <= 0:
        errors.append('price cannot be a negative number')
    # if  not re.match("^[a-zA-Z0-9_]*$", str(price)):
    #     errors.append('price should not contain any special characters apart from an underscore')
    if price > 500000:
        errors.append('are you sure, price so big!')

    return errors 

