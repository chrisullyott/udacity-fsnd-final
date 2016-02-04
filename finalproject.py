# !flask
from flask import (Flask, render_template, url_for, request, redirect, flash,
jsonify)
from functools import wraps
app = Flask(__name__)

# !sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

# !database
from database_setup import Base, Restaurant, MenuItem, User
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# !oauth
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response
CLIENT_ID = json.loads(
  open('oauth/google_client_secrets.json', 'r').read())['web']['client_id']

# !libraries
import dicttoxml

# !helpers
from pprint import pprint

# !user login
def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'username' in login_session:
      return f(*args, **kwargs)
    else:
      flash('Please log in first.')
      return redirect('/login')
  return decorated_function

@app.route('/')
@app.route('/login')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase +
    string.digits) for x in xrange(32))
  login_session['state'] = state
  return render_template('_page.html', title='Hello friend!', view='login',
    STATE=state)

# Handle oauth connect
@app.route('/gconnect', methods=['POST'])
def gconnect():

  # If valid state token
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state token'))
    response.headers['Content-Type'] = 'application/json'
    return response

  # Get authorization code
  code = request.data

  # Upgrade authorization code to credentials object
  try:
    oauth_flow = flow_from_clientsecrets('oauth/google_client_secrets.json',
      scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(
      json.dumps('Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Check for valid access token.
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
    % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])

  # Abort if errors
  if result.get('error') is not None:
    response.make_response(json.dumps(result.get('error')), 500)
    response.headers['Content-Type'] = 'application/json'

  # Match access token to intended user
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(
      json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
    response = make_response(
      json.dumps("Token's client ID does not match app's."), 401)
    print "Token's client ID does not match an app token."
    response.headers['Content-Type'] = 'application/json'
    return response

  # Access token with the app
  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('You are connected!'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Store the access token
  login_session['access_token'] = credentials.access_token
  login_session['gplus_id'] = gplus_id

  # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params=params)

  data = answer.json()

  login_session['provider'] = 'google'
  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']

  print 'User email is: ' + str(login_session['email'])
  user_id = getUserID(login_session['email'])
  if user_id:
    print 'Existing user #' + str(user_id) + ' matches this email.'
  else:
    user_id = createUser(login_session)
    print 'New user id #' + str(user_id) + ' created.'
    if user_id is None:
      print 'A new user could not be created.'
  login_session['user_id'] = user_id
  print 'Login session is tied to: id #' + str(login_session['user_id'])

  output = ''
  output += '<h2>Welcome, '
  output += login_session['username']
  output += '!</h2>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 80px; height: 80px;border-radius: 40px;"> '
  flash("You are now logged in as %s" % login_session['username'])
  return output

@app.route('/fbconnect', methods=['POST'])
def fbconnect():

  # If valid state token
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Get authorization code
  access_token = request.data

  # Upgrade authorization code to credentials object
  print "Facebook access token received: %s" % access_token

  app_id = json.loads(
    open('oauth/fb_client_secrets.json', 'r').read())['web']['app_id']
  app_secret = json.loads(
    open('oauth/fb_client_secrets.json', 'r').read())['web']['app_secret']
  url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
      app_id, app_secret, access_token)
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]

  # Use token to get user info from API
  userinfo_url = "https://graph.facebook.com/v2.4/me"

  # Strip expire tag from access token
  token = result.split("&")[0]

  url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]

  data = json.loads(result)
  login_session['provider'] = 'facebook'
  login_session['username'] = data["name"]
  login_session['email'] = data["email"]
  login_session['facebook_id'] = data["id"]

  # The token must be stored in the login_session in order to properly logout,
  # let's strip out the information before the equals sign in our token
  stored_token = token.split("=")[1]
  login_session['access_token'] = stored_token

  # Get user picture
  url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
  h = httplib2.Http()
  result = h.request(url, 'GET')[1]
  data = json.loads(result)

  login_session['picture'] = data["data"]["url"]

  # Check if user exists
  user_id = getUserID(login_session['email'])
  if not user_id:
    user_id = createUser(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

  flash("You are now logged in as %s" % login_session['username'])
  return output

@app.route('/gdisconnect')
def gdisconnect():
  access_token = login_session['access_token']
  print 'In gdisconnect access token is:'
  print access_token
  print 'User name is: '
  print login_session['username']
  if access_token is None:
	  print 'Access Token is None'
	  response = make_response(json.dumps('Current user not connected.'), 401)
	  response.headers['Content-Type'] = 'application/json'
	  return response
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]
  print 'Google logout result is:'
  print result
  if result['status'] == '200':
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    response = make_response(
      json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
  else:
  	response = make_response(
  	  json.dumps('Failed to revoke token for given user.', 400))
  	response.headers['Content-Type'] = 'application/json'
  	return response

@app.route('/fbdisconnect')
def fbdisconnect():
  facebook_id = login_session['facebook_id']
  # The access token must be included to successfully log out
  access_token = login_session['access_token']
  url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
  h = httplib2.Http()
  result = h.request(url, 'DELETE')[1]
  return "you have been logged out"

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
  if 'provider' in login_session:
    if login_session['provider'] == 'google':
      gdisconnect()
      return redirect(url_for('showRestaurants'))
    if login_session['provider'] == 'facebook':
      fbdisconnect()
      del login_session['facebook_id']
      del login_session['username']
      del login_session['email']
      del login_session['picture']
      del login_session['user_id']
      del login_session['provider']
      flash("You have successfully been logged out.")
      return redirect(url_for('showRestaurants'))
  else:
    flash("You were not logged in")
    return redirect(url_for('showRestaurants'))

# !user helper functions
def createUser(login_session):
  newUser = User(name=login_session['username'], email=login_session[
                 'email'], picture=login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email=login_session['email']).one()
  return user.id

def getUserInfo(user_id):
  user = session.query(User).filter_by(id=user_id).one()
  return user

def getUserID(email):
  try:
    user = session.query(User).filter_by(email=email).one()
    return user.id
  except:
    return None

# !routing: app
@app.route('/restaurants')
def showRestaurants():
  restaurants = session.query(Restaurant).order_by('id desc').all()
  return render_template('_page.html', title='Restaurants', view='showRestaurants', restaurants=restaurants, login_session=login_session)

@app.route('/restaurants/new', methods=['GET', 'POST'])
@login_required
def newRestaurant():
  if request.method == 'POST':
    restaurant = Restaurant(name = request.form['name'].strip(), user_id = login_session['user_id'])
    session.add(restaurant)
    session.commit()
    flash('Restaurant ' + '"' + restaurant.name + '"' + ' created.')
    return redirect(url_for('showRestaurants'))
  else:
    return render_template('_page.html', title='New Restaurant', view='newRestaurant')

@app.route('/restaurants/edit/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  owner = getUserInfo(restaurant.user_id)
  if owner.id != login_session['user_id']:
    flash('You do not have access to edit %s.' % restaurant.name)
    return redirect(url_for('showRestaurants'))
  if request.method == 'POST':
    if request.form['name']:
        restaurant.name = request.form['name'].strip()
    session.add(restaurant)
    session.commit()
    flash('Restaurant ' + '"' + restaurant.name + '"' + ' updated.')
    return redirect(url_for('showRestaurants'))
  else:
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    return render_template('_page.html', title='Edit Restaurant', view='editRestaurant', restaurant=restaurant)

@app.route('/restaurants/delete/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def deleteRestaurant(restaurant_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  owner = getUserInfo(restaurant.user_id)
  if owner.id != login_session['user_id']:
    flash('You do not have access to edit %s.' % restaurant.name)
    return redirect(url_for('showRestaurants'))
  if request.method == 'POST':
    session.delete(restaurant)
    session.commit()
    flash('Restaurant ' + '"' + restaurant.name + '"' + ' deleted.')
    return redirect(url_for('showRestaurants'))
  else:
    return render_template('_page.html', title='Delete Restaurant', view='deleteRestaurant', restaurant=restaurant)

@app.route('/restaurants/<int:restaurant_id>')
@app.route('/restaurants/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  owner = getUserInfo(restaurant.user_id)
  items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).order_by('id desc')
  return render_template('_page.html', title=restaurant.name, view='showMenu', restaurant=restaurant, items=items, owner=owner, login_session=login_session)

@app.route('/restaurants/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
@login_required
def newMenuItem(restaurant_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  owner = getUserInfo(restaurant.user_id)
  if owner.id != login_session['user_id']:
    flash('You do not have access to edit %s.' % restaurant.name)
    return redirect(url_for('showRestaurants'))
  if request.method == 'POST':
    newItem = MenuItem(
      name = request.form['name'].strip(),
      description = request.form['description'].strip(),
      course = request.form['course'].strip(),
      price = request.form['price'].strip(),
      restaurant_id = restaurant.id)
    session.add(newItem)
    session.commit()
    flash('Menu item ' + '"' + newItem.name + '"' + ' created.')
    return redirect(url_for('showMenu', restaurant_id=restaurant_id))
  else:
    return render_template('_page.html', title='New Menu Item', view='newMenuItem', restaurant=restaurant)

@app.route('/restaurants/<int:restaurant_id>/menu/edit/<int:menu_item_id>', methods=['GET', 'POST'])
@login_required
def editMenuItem(restaurant_id, menu_item_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  owner = getUserInfo(restaurant.user_id)
  if owner.id != login_session['user_id']:
    flash('You do not have access to edit %s.' % restaurant.name)
    return redirect(url_for('showRestaurants'))
  item = session.query(MenuItem).filter_by(id=menu_item_id).one()
  if request.method == 'POST':
    item.name = request.form['name'].strip()
    item.description = request.form['description'].strip()
    item.course = request.form['course'].strip()
    item.price = request.form['price'].strip()
    session.add(item)
    session.commit()
    flash('Menu item ' + '"' + item.name + '"' + ' updated.')
    return redirect(url_for('showMenu', restaurant_id=restaurant_id))
  else:
    return render_template('_page.html', title='Edit Menu Item', view='editMenuItem', restaurant=restaurant, item=item)

@app.route('/restaurants/<int:restaurant_id>/menu/delete/<int:menu_item_id>', methods=['GET', 'POST'])
@login_required
def deleteMenuItem(restaurant_id, menu_item_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  owner = getUserInfo(restaurant.user_id)
  if owner.id != login_session['user_id']:
    flash('You do not have access to edit %s.' % restaurant.name)
    return redirect(url_for('showRestaurants'))
  item = session.query(MenuItem).filter_by(id=menu_item_id).one()
  if request.method == 'POST':
    session.delete(item)
    session.commit()
    flash('Menu item ' + '"' + item.name + '"' + ' deleted.')
    return redirect(url_for('showMenu', restaurant_id=restaurant_id))
  else:
    return render_template('_page.html', title='Delete Menu Item', view='deleteMenuItem', restaurant=restaurant, item=item)

# !routing: JSON
@app.route('/restaurants/json')
def showRestaurantsJSON():
    restaurants = session.query(Restaurant).all()
    json = jsonify(Restaurants=[r.serialize for r in restaurants])
    response = make_response(json, 200)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/restaurants/xml')
def showRestaurantsXML():
    restaurants = session.query(Restaurant).all()
    xml = dicttoxml.dicttoxml([r.serialize for r in restaurants])
    response = make_response(xml, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/restaurants/<int:restaurant_id>/menu/json')
def restaurantMenuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    json = jsonify(MenuItems=[i.serialize for i in items])
    response = make_response(json, 200)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/restaurants/<int:restaurant_id>/menu/xml')
def restaurantMenuXML(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    xml = dicttoxml.dicttoxml([i.serialize for i in items])
    response = make_response(xml, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/json')
def restaurantMenuItemJSON(restaurant_id, menu_item_id):
    item = session.query(MenuItem).filter_by(id=menu_item_id).one()
    json = jsonify(Item=[item.serialize])
    response = make_response(json, 200)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/xml')
def restaurantMenuItemXML(restaurant_id, menu_item_id):
    item = session.query(MenuItem).filter_by(id=menu_item_id).one()
    xml = dicttoxml.dicttoxml([item.serialize])
    response = make_response(xml, 200)
    response.headers['Content-Type'] = 'application/xml'
    return response

# !run
if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host='0.0.0.0', port=5000)
