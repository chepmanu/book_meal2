import unittest
import os
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

        self.user = {"username":"userfirst", "password":"first", "email":"userfirst@email.com", "is_admin":True}
        self.user_normal = {"username":"usersecond", "password":"222", "email":"usersecond@email.com"}
        
        self.user_login = {'username':'userfirst','password':'first'}
        self.user_normal_login = {'username':'usersecond', "password":'222', 'token':'oeoiee'}
        # self.meal = {"food":"gith
    # def test_deletemeal_endpoint(self):
    #     """Test API endpoint can delete meal"""
    #     meal = {"food":"chapo", "price":50}
    #     response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'x-access-token':self.token})
    #     self.assertEqual(response.status_code, 201)
    #     meal_id =  json.loads(response.data).get("id")
    #     res = self.client.delete('/api/v2/meal/{}'.format(meal_id), headers={'x-access-token':self.token})
    #     self.assertEqual(res.status_code, 200)

    #     #Test to see if it exists, should return a 404
    #     result = self.client.get('/api/v2/meal/10', headers={'x-access-token':self.token})
    #     self.assertEqual(result.status_code, 404)
            

    # def test_modifymeal_endpoint(self):
    #     """Test API endpoint can modify meal option """
    #     response = self.client.post('/api/v2/meals', data=json.dumps(self.meal1), content_type='application/json', headers={'x-access-token':self.token})
    #     meal_id =  json.loads(response.data).get("id")
    #     response = self.client.put('/api/v2/meal/{}'.format(meal_id), data=json.dumps(self.meal2), content_type='application/json', headers={'x-access-token':self.token})

    #     self.assertEqual(response.status_code, 200)
    #     req = self.client.get('/api/v2/meal/{}'.format(meal_id), headers={'x-access-token':self.token})
    #     data = json.loads(req.get_data()).get('price')
    #     self.assertEqual(data, 400)
        


    # def test_getonemeal_endpoint(self):
    #     """ Test API endpoint can get one meal given the meal id"""
    #     response = self.client.post('/api/v2/meals', data=json.dumps(self.meal4), content_type='application/json', headers={'x-access-token':self.token})
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.get_data())
    #     result = self.client.get('/api/v2/meal/{}'.format(data.get('id')), headers={'x-access-token':self.token})
    #     self.assertEqual(result.status_code, 200)
        
        

    # def test_getmeals_endpoint(self):
    #     """Test API endpoint can get all meals"""
    #     req = self.client.get('/api/v2/meals',
    #                         headers={'x-access-token':self.token})
    #     self.assertEqual(req.status_code, 200)eri", "price":450, "id":1}
        # self.meal1 = {"food":"spagheti", "price":250, "id":2}
        # self.meal2 = {"price":400}
        # self.meal4 = {"food":"mutton", "price":500, "id":4}
        # self.orders = [{"food":"githeri", "price":450, "id":1},{"food":"spagheti", "price":250, "id":2}]
        # self.user1 = [{"username":"manu", "password":"manu0", "id":1}]
        # self.menu = [{"food":"githeri", "price":450, "id":1},{"food":"spagheti", "price":250, "id":2}]

        response = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user),content_type='application/json')
        response = self.client.post('/api/v2/auth/signin', data=json.dumps(self.user_login),content_type='application/json')
        self.token = json.loads(response.data).get('token')

        

    def test_signup(self):
        """ Test API endpoint can register a new user"""
        response = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user_normal),content_type='application/json')
        self.assertEqual(response.status_code, 201)
        res = self.client.get('/api/v2/users', headers={'x-access-token':self.token})
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