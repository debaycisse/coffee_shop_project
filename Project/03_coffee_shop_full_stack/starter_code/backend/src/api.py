import os
from flask import Flask, request, abort, jsonify
from sqlalchemy import exc
import json
from flask_cors import CORS
import ast

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
@requires_auth('get:drinks')
def get_drinks(payload):
    drinks = []
    try:
        for drink in Drink.query.all():
            drinks.append(drink.short()) 
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except Exception:
        abort(404)



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks_detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = []
    try:
        for drink in Drink.query.all():
            drinks.append(drink.long())
        return json.dumps({
            "success": True,
            "drinks": drinks
        })
    except Exception:
        abort(404)



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    new_drink_data = request.get_json()
    # new_drink_title = new_drink_data['title']
    # new_drink_recipe = new_drink_data['recipe']
    # new_drink_recipe_formatted = json.dumps(new_drink_recipe)

    new_drink_title = new_drink_data.get('title', None)
    new_drink_recipe = new_drink_data.get('recipe', None)

    
    new_drink = Drink(
        title = new_drink_title, 
        recipe = new_drink_recipe
        )
    try:
        new_drink.insert()
    except Exception:
        abort(422)
    get_new_drink = Drink.query.filter(Drink.title==new_drink_title).all()
    # new_drink_info = []
    # for drink in get_new_drink:
    #     new_drink_info.append(drink.long())
    return jsonify({
        "success": True,
        "drinks": [get_new_drink.long()]
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload,id):
    new_data = request.get_json()
    selected_drink = Drink.query.filter(Drink.id==id).first()
    if not selected_drink:
        abort(404)
    try:
        recipe = new_data['recipe']
        recipe_formatted = json.dumps(recipe)
        selected_drink.title = new_data['title']
        selected_drink.recipe = recipe_formatted
        selected_drink.update()
    except Exception:
        abort(422)
    # Build the data to return
    updated_drink = selected_drink.long()

    return jsonify({
        "success": True,
        "drinks": [updated_drink]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload,id):
    # new_data = request.get_json()
    print(id)
    selected_drink = Drink.query.filter(Drink.id==id).first()
    if not selected_drink:
        abort(404)
    try:
        selected_drink.delete()
    except Exception:
        abort(422)

    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error_format(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
