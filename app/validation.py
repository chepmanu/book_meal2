import re 


def usernameValidate(username):
    errors =[]
    if username is None:
        errors.append('Username required')
    
    return errors 