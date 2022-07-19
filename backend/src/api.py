import os
from flask import Flask, request, jsonify, abort, redirect, url_for
from sqlalchemy import exc
import json
from flask_cors import CORS

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

db_drop_and_create_all()


# ROUTES
@app.route('/')
def index():
    return redirect(url_for('get_all_drinks'))

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    get_drink = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in get_drink],
        'total': len(get_drink)
    }), 200



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(auth):
    drinks_detail = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [detail.long() for detail in drinks_detail]
    }), 200

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
def create_drink(auth):

    req = request.get_json()

    if 'title' and 'recipe' not in req:
        abort(422)

    my_recipe = req['recipe']
    if isinstance(my_recipe, dict):
        my_recipe = [my_recipe]

    try:
        drink_title = req['title']

        # convert object to a string
        drink_recipe = json.dumps(my_recipe)

        # instantiate the drink object
        new_drink = Drink(title=drink_title, recipe=drink_recipe)

        # Persist into the database
        new_drink.insert()

    except:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    }), 201

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
def update_drink(auth, id):
    req = request.get_json()

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        req_title = req.get('title')
        req_recipe = req.get('recipe')
        if req_title:
            drink.title = req_title

        if req_recipe:
            drink.recipe = json.dumps(req['recipe'])

        drink.update()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200


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
def delete_drink(auth, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none

    if drink is None:
        return({
            'success': False,
            'drinks': 'Drink with ID {} no longer exist'.format(id)
        }), 404

    try:
        drink.delete()
    except:
        abort(400)

    return({
        'success': True,
        'drinks': 'Drink with ID {} has been deleted'.format(id)
    }), 200



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
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
def not_found(error):
    jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found'
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return({
        'success': False,
        'error': error.status_code,
        'message': 'Unathorised'
    }), 401


@app.errorhandler(400)
def bad_request(error):
    return({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400


@app.errorhandler(403)
def forbidden(error):
    return({
        'success': False,
        'error': 403,
        'message': 'Forbidden'
    }), 403


@app.errorhandler(405)
def method_not_allowed(error):
    return({
        'success': False,
        'error': 405,
        'message': 'Method Not All  wed'
    }), 405

@app.errorhandler(500)
def internal_server_error(error):
    return({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500