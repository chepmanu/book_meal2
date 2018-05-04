from flask import Flask, request, jsonify, make_response, abort, Blueprint, current_app
import jwt
from functools import wraps

from .models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message':'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET'])
            print(data)
            current_user = User.query.filter_by(email=data['email']).first()
            print(current_user.is_admin)
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

