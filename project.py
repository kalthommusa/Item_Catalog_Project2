from werkzeug import secure_filename
import os
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, WeddingVenues, VenueItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# config for picture upload
UPLOAD_FOLDER = 'UPLOAD_FOLDER/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Wedding Venues Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///weddingvenuesappwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
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
    # ADD PROVIDER TO LOGIN SESSION

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


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
    except BaseException:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showWeddingVenues'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showWeddingVenues'))

# API Endpoints for GET Requests

# JSON data to view all wedding venues


@app.route('/weddingvenues/JSON')
def weddingVenuesJSON():
    weddingvenues = session.query(WeddingVenues).all()
    return jsonify(weddingvenues=[w.serialize for w in weddingvenues])


# JSON data to view items in a specific wedding venue
@app.route('/weddingvenues/<int:weddingvenue_id>/items/JSON')
def weddingVenuesItemsJSON(weddingvenue_id):
    weddingvenue = session.query(
        WeddingVenues).filter_by(id=weddingvenue_id).one()
    items = session.query(VenueItem).filter_by(
        weddingvenues_id=weddingvenue_id).all()
    return jsonify(VenueItems=[i.serialize for i in items])


# JSON data for a specific item
@app.route('/weddingvenues/<int:weddingvenue_id>/item/<int:item_id>/JSON')
def itemJSON(weddingvenue_id, item_id):
    item = session.query(VenueItem).filter_by(id=item_id).one()
    return jsonify(Venueitem=item.serialize)


# Show all wedding venues
@app.route('/')
@app.route('/weddingvenues/')
def showWeddingVenues():
    """
    A function that shows a list of all wedding venues in the home page,
    takes no arguments.
    return:
    -It shows a list of all wedding venues names as well as
    gives the ability to the users who logged in to modify
    the wedding venues that they have posted
    -otherwise, it shows wedding venues without the ability to modify them.
    """
    weddingvenues = session.query(
        WeddingVenues).order_by(asc(WeddingVenues.name))
    if 'username' not in login_session:
        return render_template(
            'publicweddingvenues.html',
            weddingvenues=weddingvenues)
    else:
        return render_template(
            'weddingvenues.html',
            weddingvenues=weddingvenues)


# Create a new wedding venue
@app.route('/weddingvenue/new/', methods=['GET', 'POST'])
def newWeddingVenue():
    """
    A function to add a new wedding venue,takes no arguments.
    return:
    -It allows the logged in users to add a new wedding venue
    -otherwise, it redirects the users to the login page.
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newWeddingVenue = WeddingVenues(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newWeddingVenue)
        session.commit()
        flash(
            'New Wedding Venues %s Successfully Created' %
            newWeddingVenue.name)
        return redirect(url_for('showWeddingVenues'))
    else:
        return render_template('newWeddingVenue.html')


# Edit a wedding venue
@app.route(
    '/weddingvenues/<int:weddingvenue_id>/edit/',
    methods=[
        'GET',
        'POST'])
def editWeddingVenue(weddingvenue_id):
    """
    A function that edits a specific wedding venue, it takes an id for
    a specific wedding venue as an argument.
    return:
    -It allows the logged in users to edit only the wedding venue that
    they have posted and gives them the option to cancel the edit operation.
    -If the users are logged in but they're trying to edit a wedding venue
    that they didn't post it, a flash message will appear as a feedback that
    they cannot edit the wedding venue.
    """
    editedWeddingVenue = session.query(
        WeddingVenues).filter_by(id=weddingvenue_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    # local permission check for logged in users to edit only their data
    if editedWeddingVenue.user_id != login_session['user_id']:
        flash('You are not authorized to edit this wedding venue. \
              Please create your own wedding venue in order to edit.')
        return redirect(url_for('showWeddingVenues'))
    if request.method == 'POST':
        if request.form['name']:
            editedWeddingVenue.name = request.form['name']
            flash(
                'Wedding Venues Successfully Edited %s' %
                editedWeddingVenue.name)
            return redirect(url_for('showWeddingVenues'))
    else:
        return render_template(
            'editWeddingVenue.html',
            weddingvenue=editedWeddingVenue)


# Delete a wedding venue
@app.route(
    '/weddingvenues/<int:weddingvenue_id>/delete/',
    methods=[
        'GET',
        'POST'])
def deleteWeddingVenue(weddingvenue_id):
    """
    A function that deletes a specific wedding venue, it takes an id for
    a specific wedding venue as an argument.
    return:
    -It allows the logged in users to delete only the wedding venue that
    they have posted and gives them the option to cancel the delete operation.
    -If the users are logged in but they're trying to delete a wedding venue
    that they haven't post it, a flash message will appear as a feedback that
    they cannot delete the wedding venue.
    """
    deletedWeddingVenue = session.query(
        WeddingVenues).filter_by(id=weddingvenue_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    # local permission check for logged in users to edit only their data
    if deletedWeddingVenue.user_id != login_session['user_id']:
        flash('You are not authorized to delete this wedding venue. \
              Please create your own wedding venue in order to delete.')
        return redirect(url_for('showWeddingVenues'))
    if request.method == 'POST':
        session.delete(deletedWeddingVenue)
        session.commit()
        flash('%s Successfully Deleted' % deletedWeddingVenue.name)
        return redirect(
            url_for(
                'showWeddingVenues',
                weddingvenue_id=weddingvenue_id))
    else:
        return render_template(
            'deleteWeddingVenue.html',
            weddingvenue=deletedWeddingVenue)


# Show details of specific wedding venue
@app.route('/weddingvenues/<int:weddingvenue_id>/items/')
def showItems(weddingvenue_id):
    """
    A function that takes an id for a specific wedding venue as an argument.
    return:
    -It shows all items' details for a specific wedding venue as well as gives
    the ability to the users who logged in to modify the items that
    they have posted
    -otherwise, it only shows item details for a specific wedding venue
    without the ability to modify it.
    """
    weddingvenue = session.query(
        WeddingVenues).filter_by(id=weddingvenue_id).one()
    creator = getUserInfo(weddingvenue.user_id)
    items = session.query(VenueItem).filter_by(
        weddingvenues_id=weddingvenue_id).all()
    if 'username' not in login_session or\
            creator.id != login_session['user_id']:

        return render_template(
            'publicitems.html',
            items=items,
            weddingvenue=weddingvenue,
            creator=creator)
    else:
        return render_template(
            'items.html',
            items=items,
            weddingvenue=weddingvenue,
            creator=creator)


# Determine if the fileuploaded it's allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Create a new item
@app.route(
    '/weddingvenues/<int:weddingvenue_id>/new/',
    methods=[
        'GET',
        'POST'])
def newItem(weddingvenue_id):
    """
    A function to add a new item, it takes an id for a specific
    wedding venue that the user want to make an item for it as an argument.
    return:
    -It allows only the logged in users to add a new item
    to a specific wedding venue
    -otherwise, it redirects the user to the login page.
    """
    if 'username' not in login_session:
        return redirect('/login')
    weddingvenue = session.query(
        WeddingVenues).filter_by(id=weddingvenue_id).one()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        newItem = VenueItem(
            location=request.form["location"],
            price=request.form["price"],
            contact_number=request.form["phoneNum"],
            capacity=request.form["capacity"],
            picture=filename,
            weddingvenues_id=weddingvenue_id,
            user_id=weddingvenue.user_id)
        session.add(newItem)
        session.commit()
        flash('New Item Successfully Created')
        return redirect(url_for('showItems', weddingvenue_id=weddingvenue_id))
    else:
        return render_template('newitem.html', weddingvenue_id=weddingvenue_id)


# Edit an item
@app.route(
    '/weddingvenues/<int:weddingvenue_id>/item/<int:item_id>/edit',
    methods=[
        'GET',
        'POST'])
def editItem(weddingvenue_id, item_id):
    """
    A function to edit an item, it takes an id for a specific item that
    it's going to edit and an id for the wedding venue that the item
    belongs to as arguments.
    return:
    -It allows the logged in users to edit only the item that they have
    posted and gives them the option to cancel the edit operation.
    -If the users are logged in but they're trying to edit an item that
    they haven't post it, a flash message will appear as a feedback that
    they cann't update the item.
    """

    if 'username' not in login_session:
        return redirect('/login')
    weddingvenue = session.query(
        WeddingVenues).filter_by(id=weddingvenue_id).one()
    editedItem = session.query(VenueItem).filter_by(id=item_id).one()

    # local permission check for logged in users to edit only their data
    if login_session['user_id'] != weddingvenue.user_id:
        flash('You are not authorized to edit items to this wedding venue. \
              Please create your own wedding venue in order to edit items.')
        return redirect(url_for('showItems', weddingvenue_id=weddingvenue_id))
    if request.method == 'POST':
        if request.form['location']:
            editedItem.location = request.form['location']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['phoneNum']:
            editedItem.contact_number = request.form['phoneNum']
        if request.form['capacity']:
            editedItem.capacity = request.form['capacity']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showItems', weddingvenue_id=weddingvenue_id))
    else:
        return render_template(
            'edititem.html',
            weddingvenue_id=weddingvenue_id,
            item_id=item_id,
            item=editedItem)


# Delete an item
@app.route(
    '/weddingvenues/<int:weddingvenue_id>/item/<int:item_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteItem(weddingvenue_id, item_id):
    """
    A function to delete an item, it takes an id for a specific item that
    it's going to delete and an id for the wedding venue that the item
    belongs to as arguments.
    return:
    -It allows the logged in users to delete only the item that they have
    posted and gives them the option to cancel the delete operation.
    -If the users are logged in but they're trying to delete an item that
    they haven't post it, a flash message will appear as a feedback that
    they cannot delete the item.
    """
    if 'username' not in login_session:
        return redirect('/login')
    weddingvenue = session.query(
        WeddingVenues).filter_by(id=weddingvenue_id).one()
    deletedItem = session.query(VenueItem).filter_by(id=item_id).one()
    venue_poster = getUserID(login_session["email"])
    # local permission check for logged in users to edit only their data
    if login_session['user_id'] != deletedItem.user_id:
        flash('You are not authorized to delete item to this wedding venue. \
              Please create your own wedding venue in order to delete items.')
        return redirect(url_for('showItems', weddingvenue_id=weddingvenue_id))
    if request.method == 'POST':
        """
        Delete associated wedding venue picture while deleting a wedding venue
        """
        os.remove(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                deletedItem.picture))
        session.delete(deletedItem)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showItems', weddingvenue_id=weddingvenue_id))
    else:
        return render_template(
            'deleteitem.html',
            item=deletedItem,
            weddingvenue_id=weddingvenue_id,
            item_id=item_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
