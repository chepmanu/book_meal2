# Book A Meal
https://travis-ci.org/chepmanu/book_meal2.svg?branch=master
<img src='/homepage.png',  alt='bookmeal_homepage'>
1.This is an app that allows for people to make orders and caterers to set up and complete orders.

## How to run.
1. Create a virtual env and activate it.
1. Install all the requirements as seen in the requirements.txt
1. Set up the database for both the testing and development configurations.
1. Run the test on your terminal using nose.
1. Run the application by typing *flask run* on your terminal.
1. Use postman to check all the endpoints. 

## Endpoints functionality
### Signup endpoint
This endpoint allows a user or caterer to sign up by providing the required credentials in the correct format.

### Signin endpoint 
This endpoint allows a user of caterer to sign in by providing the correct credentials and they are assigned a token upon successfull sign in.

### Add Meal endpoint 
This endpoint allows a caterer only to add a meal item into the system by providing the meal name and the price.

### Mordify Meal endpoint 
This endpoint allows a caterer only to mordify a meal that was set to the system by providing the new meal information to update with. 

### Remove a Meal endpoint 
This endpoint allows a caterer only to remove a meal that was set to the system by providing the meal id for the meal to be deleted. 

### Set menu endpoint 
This endpoint allows a caterer only to set a menu by selecting meals from the system. 

### Select menu item 
This endpoint allows a caterer only to select one menu item.

### Make an order
This endpoint allows an authenticated user to make an order by picking a meal in the menu.

### Mordify an order 
This endpoint allows an authenticated user to mordify an order by providing the new meal item to replace the one in the order with

### Get all orders 
This endpoint allows an authenticated caterer to view all the orders that have been placed.  

### Get one order 
This endpoint allows an authenticated caterer to view one order item. 

### Get users 
This endpoint allows an aunthenticated caterer to view all users.