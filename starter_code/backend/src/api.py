import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# Initialize the datbase
db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def drinks():
    try:
        drinks_all = Drink.query.all()
        drinks = [drink.short() for drink in drinks_all]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception:
        abort(404)



@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks_all = Drink.query.all()
        drinks = [drink.long() for drink in drinks_all]

        if query is None:
            abort(400)

        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception:
        abort(404)



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    try:
        title = body.get('title')
        recipe = body.get('recipe')

        drink = Drink(title=title, recipe=json.dumps([recipe]))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except Exception:
        abort(422)



@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    body = request.get_json()
    # drink = Drink.query.get(drink_id)
    drink = Drink.query.filter(Drink.id == drink_id).first()
    if (body is {} or drink == None):
        abort(404)

    title = body.get('title')
    recipe = body.get('recipe')

    try:
        drink.title = title
        drink.recipe = json.dumps([recipe])
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except Exception:
        abort(422)



@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    # drink = Drink.query.get(drink_id)
    drink = Drink.query.filter(Drink.id == drink_id).first()
    if drink is None:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except Exception:
        abort(422)


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False, 
        'error': 422,
        'message': 'Unprocessable'
      }), 422


# implement error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    }), 400


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Forbidden'
    }), 403


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error'
    }), 500



@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code