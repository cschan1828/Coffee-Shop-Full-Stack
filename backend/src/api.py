import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)

# Set up CORS. Allow '*' for origins.
cors = CORS(app, resources={r"/": {"origins": "*"}})


@app.after_request
def after_request(response):
    '''
    Set Access-Control-Allow and CORS.
    '''
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Methods', 'GET,POST,DELETE,PATCH'
    )

    return response

# db_drop_and_create_all()


@app.route('/drinks', methods=['GET'])
def drinks():
    '''
    A public endpoint containing only brief drink recipe.
    '''
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": [d.short() for d in drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    '''
    An endpoint required the special permission,
    containing only brief drink recipe.
    '''
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    '''
    An endpoint required the special permission,
    creating a new drink, returning a full drink info.
    '''
    try:
        drink_input = request.get_json()
        title_new = drink_input.get('title', None)
        recipe_new = drink_input.get('recipe', None)
        if (title_new is not None) & (recipe_new is not None):
            drink_created = Drink(
                title=title_new,
                recipe=json.dumps(recipe_new)
            )
            drink_created.insert()
            return jsonify({
                "success": True,
                "drinks": drink_created.long()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Missing title or recipe!"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 422


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(id):
    '''
    An endpoint required the special permission, updating an existing drink.
    '''
    try:
        drink_input = request.get_json()
        target_drink = Drink.query.get(id)

        if target_drink:
            title_new = drink_input.get('title', None)
            recipe_new = drink_input.get('recipe', None)

            if title_new:
                target_drink.title = title_new
            if recipe_new:
                target_drink.recipe = recipe_new

            target_drink.update()

            return jsonify({
                "success": True,
                "drinks": target_drink.long()
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "drink doesn't exist."
            }), 404

    except Exception as e:
        print(e)
        abort(404)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    '''
    An endpoint required the special permission, deleting a selected drink.
    '''
    try:
        target_drink = Drink.query.get(drink_id)
        if target_drink:
            target_drink.delete()
            return jsonify({
                "success": True,
                "delete": target_drink.id
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "The drink doesn't exist."
            })
    except Exception as e:
        print(e)
        abort(404)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    '''
    An error handler for unprocessable entity.
    '''
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    '''
    An error handler for 404 Not Found Error.
    '''
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    '''
    An error handler for 401 Unauthorized Error.
    '''
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Sorry, you are not authorized for this action"
    }), 401
