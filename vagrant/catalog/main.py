# ====================
# Imports
# ====================
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask import session

from db_setup import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json
import random
import string
import urllib2

# ====================
# Globals
# ====================
googleTokenURL = 'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={}'
secretKey = 'dev_key'

engine = create_engine('sqlite:///catalog.db')
DBSession = sessionmaker(bind = engine)
db_session = DBSession()

# ====================
# Functions
# ====================
def generateState():
    validCharacters = string.ascii_uppercase + string.digits
    state = ''.join(random.choice(validCharacters) for x in range(32))

    return state

def getUserID(email):
    user = db_session.query(User).filter(User.email == email).first()
    if user:
        return user.id
    else:
        return None

def itemDict(item):
    # Returns a dictionary representing an item.
    if item:
        return {"category_id": item.category_id, "item_id": item.id, "name": item.name, "description": item.description}
    else:
        return {}

def categoryDict(category):
    # Returns a dictionary representing a category.

    categoryDict = dict()
    if category:
        items = db_session.query(Item).filter(Item.category_id == category.id).all()
        itemsArray = []

        for item in items:
             itemsArray.append(itemDict(item))
        
        categoryDict['id'] = category.id
        categoryDict['name'] = category.name
        categoryDict['items'] = itemsArray

    return categoryDict


# ====================
# Flask routing
# ====================
app = Flask(__name__)

@app.route('/')
def catalog():
    user = session.get('username')
    categories = db_session.query(Category).all()

    return render_template('catalog.html', user = user, categories = categories)
  
@app.route('/json/')
def catalogJSON():
    categories = db_session.query(Category).all()
    cat = dict()
    categoriesArray = []

    for category in categories:
        categoriesArray.append(categoryDict(category))

    cat["categories"] = categoriesArray

    response = make_response(json.dumps(cat))
    response.headers['Content-Type'] = 'application/json'
    
    return response

@app.route('/category/<int:category_id>/')
def showCategory(category_id):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    
    return render_template('category.html', category = category)

@app.route('/category/<int:category_id>/json/')
def showCategoryJSON(category_id):
    category = db_session.query(Category).filter(Category.id == category_id).first()
    catDict = categoryDict(category)

    response = make_response(json.dumps(catDict))
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/category/<int:category_id>/<int:item_id>/')
def showItem(category_id, item_id):
    item = db_session.query(Item).filter(Item.id == item_id).filter(Item.category_id == category_id).first()
    user = getUserID(session.get('email'))

    return render_template('item.html', item = item, user = user)

@app.route('/category/<int:category_id>/<int:item_id>/json/')
def showItemJSON(category_id, item_id):
    item = db_session.query(Item).filter(Item.id == item_id).filter(Item.category_id == category_id).first()
    
    response = make_response(json.dumps(itemDict(item)))
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/category/<int:category_id>/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    item = db_session.query(Item).filter(Item.id == item_id).filter(Item.category_id == category_id).first()
    user = getUserID(session.get('email'))

    if request.method == 'GET':
        if user == item.user_id:
            return render_template('edit_item.html', item = item)
        else:
            return "You do not own this item!"
    elif request.method == 'POST':
        name = request.values.get('name')
        description = request.values.get('description')

        if user == item.user_id:
            item.name = name
            item.description = description
            db_session.add(item)
            db_session.commit()

        return redirect(url_for('catalog'))


@app.route('/category/<int:category_id>/<int:item_id>/delete/', methods=['POST'])
def deleteItem(category_id, item_id):
    item = db_session.query(Item).filter(Item.id == item_id).filter(Item.category_id == category_id).first()
    user = getUserID(session.get('email'))

    if user == item.user_id:
        db_session.delete(item)
        db_session.commit()

        return redirect(url_for('catalog'))
    else:
        return "You do not own this item!"

@app.route('/login/')
def login():
    state = generateState()
    session['state'] = state

    return render_template('login.html', STATE = state)

@app.route('/gconnect/', methods=['POST'])
def gconnect():
    client_state = request.args.get('state')
    if client_state != session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'

        return response
    else:
        id_token = request.data
        id_claims = urllib2.urlopen(googleTokenURL.format(id_token)).read()
        id_claims_json = json.loads(id_claims)

        stored_id = session.get('id_token')
        if stored_id == id_token:
            response = make_response(json.dumps('Current user is already logged in.'), 200)
            response.headers['Content-Type'] = 'application/json'

            return response
        else:
            session['id_token'] = id_token
            session['username'] = id_claims_json['name']
            session['email'] = id_claims_json['email']

            if getUserID(session['email']):
                print "Existing user."
            else:
                new_user = User(name = session['username'], email = session['email'])
                db_session.add(new_user)
                db_session.commit()

            return 'Welcome, {}!'.format(session['username'])

@app.route('/gdisconnect/')
def gdisconnect():
    id_token = session.get('id_token')
    if id_token:
        del session['id_token']
        del session['username']
        del session['email']

        return 'Logged out.'
    else:
        return redirect(url_for('catalog'))

@app.route('/newitem/', methods = ['GET', 'POST'])
def newItem():
    if request.method == 'GET':
        if session.get('email'):
            categories = db_session.query(Category).all()

            return render_template('new_item.html', categories = categories)
        else:
            return redirect(url_for('catalog'))
    else:
        category = int(request.values.get('category'))
        name = request.values.get('name')
        description = request.values.get('description')
        user_id = getUserID(session.get('email'))

        item = Item(name = name, description = description, category_id = category, user_id = user_id)
        db_session.add(item)
        db_session.commit()

        return redirect(url_for('catalog'))

if __name__ == '__main__':
    app.secret_key = secretKey
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
