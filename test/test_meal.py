import unittest 
import os 
from app import create_app, db 
from app.models import Meal 
import json
class EndPointsTestCase(unittest.TestCase):
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
        self.meal = {"food":"githeri", "price":450}
        self.meal1 = {"food":"spagheti", "price":250}
        self.meal2 = {"price":400}
        self.meal4 = {"food":"mutton", "price":500}
        self.orders = [{"food":"githeri", "price":450, "id":1},{"food":"spagheti", "price":250, "id":2}]
        self.user1 = [{"username":"manu", "password":"manu0", "id":1}]
        self.menu = [{"food":"githeri", "price":450, "id":1},{"food":"spagheti", "price":250, "id":2}]

        response = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user),content_type='application/json')
        response = self.client.post('/api/v2/auth/signin', data=json.dumps(self.user_login),content_type='application/json')
        self.token = json.loads(response.data).get('token')

    def test_addmeal_endpoint(self):
        """ Test API endpoint can add meal"""
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'x-access-token':self.token})
        self.assertEqual(response.status_code, 201)
        with self.app.app_context():
            meal = Meal.query.filter_by(food="githeri").first()
            
        meal_id = meal.meal_id
        res = self.client.get('/api/v2/meal/{}'.format(meal_id), headers={'x-access-token':self.token})
        self.assertEqual(res.status_code, 200)
        



    def test_deletemeal_endpoint(self):
        """Test API endpoint can delete meal"""
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'x-access-token':self.token})
        self.assertEqual(response.status_code, 201)
        with self.app.app_context():
            meal = Meal.query.filter_by(food="githeri").first()
        meal_id = meal.meal_id
        print(meal_id)
        res = self.client.delete('/api/v2/meal/{}'.format(meal_id), headers={'x-access-token':self.token})
        self.assertEqual(res.status_code, 204)

        
    def test_modifymeal_endpoint(self):
        """Test API endpoint can modify meal option """
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'x-access-token':self.token})
        self.assertEqual(response.status_code, 201)
        with self.app.app_context():
            meal = Meal.query.filter_by(food="githeri").first() 
        meal_id = meal.meal_id
        response = self.client.put('/api/v2/meal/{}'.format(meal_id), data=json.dumps(self.meal2), content_type='application/json', headers={'x-access-token':self.token})

        self.assertEqual(response.status_code, 200)
        req = self.client.get('/api/v2/meal/{}'.format(meal_id), headers={'x-access-token':self.token})
        self.assertEqual(req.status_code, 200)
        data = json.loads(req.data).get('price')
        print(data)
        self.assertEqual(data, 400)
        


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
    #     self.assertEqual(req.status_code, 200)
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.reflect()
            db.drop_all() 

if __name__ == "__main__":
    unittest.main()