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
        self.meal2 = {"food":"veal", "price":400}
        self.meal4 = {"food":"mutton", "price":500}

        response = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user),content_type='application/json')
        response = self.client.post('/api/v2/auth/signin', data=json.dumps(self.user_login),content_type='application/json')
        self.token = json.loads(response.data).get('token')

    def test_setmenu_endpoint(self):
        """ Test API endpoint can add meal to menu"""
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 201)
        
        with self.app.app_context():
            meal = Meal.query.filter_by(food="githeri").first()
        meal_id = meal.meal_id
        req = {
            "id":meal_id
        }
        res = self.client.post('/api/v2/menu', data=json.dumps(req), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        req = self.client.get('/api/v2/menu', headers={'Authorization':self.token})
        self.assertEqual(req.status_code, 200)
        data = json.loads(req.data)
        with self.app.app_context():
            meal = Meal.query.filter_by(meal_id=meal_id).first() 
        self.assertIn('githeri', meal.food)
        



    def test_selectfrom_menu_endpoint(self):
        """Test API endpoint can select from  menu  """
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 201)
        
        with self.app.app_context():
            meal = Meal.query.filter_by(food="githeri").first()
        meal_id = meal.meal_id
        req = {
            "id":meal_id
        }
        res = self.client.post('/api/v2/menu', data=json.dumps(req), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        req = self.client.get('/api/v2/menu', headers={'Authorization':self.token})
        self.assertEqual(req.status_code, 200)
        data = json.loads(req.data)
        meal_id = data['menu'][0]['meals']
        with self.app.app_context():
            meal = Meal.query.filter_by(meal_id=meal_id).first() 
        self.assertIn('githeri', meal.food)
        
    def test_getmenu_endpoint(self):
        """Test API endpoint can get menu  """
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal1), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 201)
        
        with self.app.app_context():
            meal = Meal.query.filter_by(food="githeri").first()
            meal2 = Meal.query.filter_by(food="spagheti").first()
        meal_id = meal.meal_id
        meal_id2 = meal2.meal_id 
        req = {
            "id":meal_id
        }
        req2 = {
            "id":meal_id2
        }
        res = self.client.post('/api/v2/menu', data=json.dumps(req), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        res = self.client.post('/api/v2/menu', data=json.dumps(req2), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        req = self.client.get('/api/v2/menu', headers={'Authorization':self.token})
        self.assertEqual(req.status_code, 200)
        data = json.loads(req.data)
        meal_id = data['menu'][0]['meals']
        meal_id2 = data['menu'][1]['meals']
        with self.app.app_context():
            meal = Meal.query.filter_by(meal_id=meal_id).first()
            meal1 = Meal.query.filter_by(meal_id=meal_id2).first() 
        self.assertIn('githeri', meal.food)
        self.assertIn('spagheti', meal1.food)
    

        


   



    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.reflect()
            db.drop_all() 

if __name__ == "__main__":
    unittest.main()