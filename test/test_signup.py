import unittest
import os
import jwt
import json
from app import create_app, db
from app.models import User, Meal


class EndPointsTestCase(unittest.TestCase):
    """ Tests for all the api endpoints """
    def setUp(self):
        """ Initialize app and define test variables"""
        self.app = create_app('testing')
        self.app.testing=True
        self.client = self.app.test_client()
        with self.app.app_context():
            # create all tables
            db.session.commit()
            db.drop_all()
            db.create_all()

        self.user = {"username":"userfirst", "password":"firstcome", "email":"userfirst@email.com", "is_admin":True}
        self.user_normal = {"username":"usersecond", "password":"222second", "email":"usersecond@email.com"}
        
        self.user_login = {'username':'userfirst','password':'firstcome'}
        self.user_normal_login = {'username':'usersecond', "password":'222second', 'token':'oeoiee'}
   

        response = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user),content_type='application/json')
        res = self.client.post('/api/v2/auth/signin', data=json.dumps(self.user_login),content_type='application/json')
        self.token = json.loads(res.data)['token']
        claim = jwt.decode(self.token, 'thisismanuchepsecretkey15')
        print(claim)
        
        

    def test_signup(self):
        """ Test API endpoint can register a new user"""
        res = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user_normal),content_type='application/json')
        self.assertEqual(res.status_code, 201)
        print(res.data)
        res = self.client.get('/api/v2/users', headers={'Authorization':self.token})
        print(res.data)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('usersecond', str(data))


    def test_signin(self):
        """Test API endpoint can sign in user""" 
        response = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user_normal),content_type='application/json')
        response = self.client.post('/api/v2/auth/signin', data=json.dumps(self.user_normal_login), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('token' in data)    


    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.reflect()
            db.drop_all() 

if __name__ == "__main__":
    unittest.main()