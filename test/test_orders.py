import unittest 
import os 
from app import create_app, db 
from app.models import Meal, Menu 
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
        self.user_normal = {"username":"usersecond", "password":"222normal", "email":"usersecond@email.com"}
        
        self.user_login = {'username':'userfirst','password':'first'}
        self.user_normal_login = {'username':'usersecond', "password":'222normal', 'token':'oeoiee'}
        self.meal = {"food":"githeri", "price":450}
        self.meal1 = {"food":"spagheti", "price":250}
        self.meal2 = {"food":"veal", "price":400}
        self.meal4 = {"food":"mutton", "price":500}

        response = self.client.post('/api/v2/auth/signup', data=json.dumps(self.user),content_type='application/json')
        response = self.client.post('/api/v2/auth/signin', data=json.dumps(self.user_login),content_type='application/json')
        self.token = json.loads(response.data).get('token')

    def test_makeorder_endpoint(self):
        """ Test API endpoint can make an order"""
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
        req = {
            "id":1
        }
        res = self.client.post('/api/v2/orders', data=json.dumps(req), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        response = self.client.get('/api/v2/orders', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        meal = data['orders'][0]['menu_id']
        with self.app.app_context():
            meal2 = Menu.query.filter_by(menu_id=meal).first()
            meal1 = Meal.query.filter_by(meal_id=meal2.meals).first()
        self.assertIn('githeri', meal1.food)        



    def test_mordifyorder_endpoint(self):
        """ Test API endpoint can modify order"""
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/v2/meals', data=json.dumps(self.meal1), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 201)
        
        with self.app.app_context():
            meal = Meal.query.filter_by(food="githeri").first()
            meal2 = Meal.query.filter_by(food='spagheti').first()
        meal_id = meal.meal_id
        meal_id1 = meal2.meal_id
        req = {
            "id":meal_id
        }
        req1 = {
            "id":meal_id1
        }
        res = self.client.post('/api/v2/menu', data=json.dumps(req), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        res = self.client.post('/api/v2/menu', data=json.dumps(req1), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        req = self.client.get('/api/v2/menu', headers={'Authorization':self.token})
        self.assertEqual(req.status_code, 200)
        data = json.loads(req.data)
        with self.app.app_context():
            meal = Meal.query.filter_by(meal_id=meal_id).first() 
        self.assertIn('githeri', meal.food)
        req2 = {
            "id":1
        }
        req3 = {
            "id":2
        }
        res = self.client.post('/api/v2/orders', data=json.dumps(req2), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        res = self.client.post('/api/v2/orders', data=json.dumps(req3), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        response = self.client.get('/api/v2/orders', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        print(data)
        menu_id1 = data['orders'][0]['menu_id']
        menu_id2 = data['orders'][1]['menu_id']
        order_id = data['orders'][0]['order_id']
        with self.app.app_context():
            meal1 = Menu.query.filter_by(menu_id=menu_id1).first()
            meal2 = Menu.query.filter_by(menu_id=menu_id2).first()
            meal_item1 = Meal.query.filter_by(meal_id=meal1.meals).first()
            meal_item2 = Meal.query.filter_by(meal_id=meal2.meals).first()
            print(meal_item2.food)
        self.assertIn('githeri', meal_item1.food)
        self.assertIn('spagheti', meal_item2.food)
        req1 = {
            "order_id":order_id
        }
        menu_id ={
            "menu_id":menu_id2
        }
        res = self.client.put('/api/v2/orders/{}'.format(order_id), data=json.dumps(menu_id),content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        response = self.client.get('/api/v2/orders/{}'.format(order_id), headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 200)


        
        
    def test_getorders_endpoint(self):
        """ Test API endpoint can get all orders"""
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
        req = {
            "id":1
        }
        res = self.client.post('/api/v2/orders', data=json.dumps(req), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        response = self.client.get('/api/v2/orders', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        meal = data['orders'][0]['menu_id']
        with self.app.app_context():
            meal2 = Menu.query.filter_by(menu_id=meal).first()
            meal1 = Meal.query.filter_by(meal_id=meal2.meals).first()
        self.assertIn('githeri', meal1.food)        

    def test_get_one_orders_endpoint(self):
        """ Test API endpoint can get one order"""
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
        req = {
            "id":1
        }
        res = self.client.post('/api/v2/orders', data=json.dumps(req), content_type='application/json', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        response = self.client.get('/api/v2/orders', headers={'Authorization':self.token})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        meal = data['orders'][0]['menu_id']
        order = data['orders'][0]['order_id']
        with self.app.app_context():
            meal2 = Menu.query.filter_by(menu_id=meal).first()
            meal1 = Meal.query.filter_by(meal_id=meal2.meals).first()
        self.assertIn('githeri', meal1.food)
        res = self.client.get('/api/v2/orders/{}'.format(order), headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200) 


    def test_getusers_endpoint(self):
        """Test API endpoint can get all users"""
        res = self.client.get('/api/v2/users', headers={'Authorization':self.token})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('userfirst', str(data))



   


    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.reflect()
            db.drop_all() 

if __name__ == "__main__":
    unittest.main()