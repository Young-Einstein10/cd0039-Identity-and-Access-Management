from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)


"""
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
"""
CORS(app)

"""
    @TODO: Use the after_request decorator to set Access-Control-Allow
"""


@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response


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


@app.route("/drinks")
def fetch_short_drinks():
    drinks = Drink.query.order_by(Drink.id).all()

    short_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': short_drinks,
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def fetch_long_drinks(params):
    drinks = Drink.query.order_by(Drink.id).all()

    long_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': long_drinks,
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def create_drink(params):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = json.dumps(body.get("recipe", None))

    drink = Drink(title=new_title, recipe=new_recipe)

    drink.insert()

    return jsonify(
        {
            'success': True,
            'drinks': [drink.long()]
        }
    )


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


@app.route("/drinks/<id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(params, id):
    drink = Drink.query.filter(
        Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()

    incoming_title = body.get("title", None)
    incoming_recipe = json.dumps(body.get("recipe", None))

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    drink.title = incoming_title
    drink.recipe = incoming_recipe

    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
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


@app.route("/drinks/<id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(params, id):
    drink = Drink.query.filter(
        Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify(
        {
            "success": True,
            "delete": id,
        }
    )


# Error Handling
'''
Example error handling for unprocessable entity
'''


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422)


@app.errorhandler(400)
def bad_request(error):
    return (jsonify({"success": False, "error": 400, "message": "bad request"}), 400)


@app.errorhandler(403)
def bad_request(error):
    return (jsonify({"success": False, "error": 403, "message": "Forbidden"}), 403)


@app.errorhandler(500)
def internal_server(error):
    return (jsonify({"success": False, "error": 500, "message": "internal server error"}), 500)


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404,
                 "message": "resource not found"}),
        404,
    )


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(401)
def not_found(error):
    return (
        jsonify({"success": False, "error": 401,
                 "message": "not authorized"}),
        401,
    )


@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response
