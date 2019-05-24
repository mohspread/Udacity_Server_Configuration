#!/usr/bin/env python
from flask import(
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, MenuItem, User


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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Menu Application"

"""to initiate a connection with the database"""

engine = create_engine('sqlite:///categorymenuwithusers.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Validate state token"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    """Obtain authorization code"""
    code = request.data

    """Upgrade the authorization code into a credentials object"""
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    """Check that the access token is valid"""
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    """If there was an error in the access token info, abort"""
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    """Verify that the access token is used for the intended user"""
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    """Verify that the access token is valid for this app"""
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    """Store the access token in the session for later use"""
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    """Get user info"""
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(data["email"])
    """If logged in Username is not Registered, Then create an account."""
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    """Display Welcome Message
    and Google Account Pic
    while redirecting user to homepage."""

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;"' +
               '"border-radius: 150px;-webkit-border-radius: 150px;"' +
               '"-moz-border-radius: 150px;">')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


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

    """to disconnect the current user
    by deleting the contents of login_session."""


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    token = login_session['access_token']
    short_url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = short_url % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

    """Return JSON format of the all items."""


@app.route('/catalog/JSON')
def jsonAll():
    categories = session.query(Category).all()
    category_all = [c.serialize for c in categories]
    for c in range(len(category_all)):
        items = [i.serialize for i in session.query(MenuItem)
                 .filter_by(category_id=category_all[c]["id"]).all()]
        if items:
            category_all[c]["Item"] = items
    return jsonify(Category=category_all)

    """Return JSON format of the all categories."""


@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])

    """Return JSON format of the all items."""


@app.route('/items/JSON')
def itemsJSON():
    items = session.query(MenuItem).all()
    return jsonify(items=[r.serialize for r in items])

    """Return JSON format of the all items inside specific category."""


@app.route('/categories/<int:category_id>/menu/JSON')
def categoryMenuJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(MenuItem).filter_by(
        category_id=category_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

    """Return JSON format of the a single item inside a category."""


@app.route('/categories/<int:category_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(category_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)

    """Show all the available categories on the website,
     "State" variable has been used here also
     to get the Login button in Homepage."""


@app.route('/')
@app.route('/categories/')
def categoryMenu():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    menuitems = session.query(MenuItem).order_by(MenuItem.id.desc())
    return render_template("menu.html", categories=categories,
                           menuitems=menuitems,
                           login_session=login_session, STATE=state)

    """Create new category, Only in case user is logged in,
     then redirect again to Homepage"""


@app.route('/categories/new', methods=['GET', 'POST'])
def categoryNew():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['NewCategory']:
            NewCategory = Category(
                name=request.form['NewCategory'],
                user_id=login_session['user_id'])
            session.add(NewCategory)
            session.commit()
            return redirect(url_for('categoryMenu'))
        else:
            return "Name field cannot be empty"
    else:
        return render_template("newcategory.html", login_session=login_session)

    """Edit existing category, Only in case
     logged in user is the creator, in case not,
     The Edit Pencil will not even show"""


@app.route('/categories/<int:category_id>/menu/edit', methods=['GET', 'POST'])
def categoryEdit(category_id):
    if 'username' not in login_session:
        return "You are not authorized to view this page, Please login.."
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['NewName']:
            if login_session['user_id'] == category.user_id:
                category.name = request.form['NewName']
                session.add(category)
                session.commit()
                return redirect('/categories/')
            else:
                return "You are not the Owner of this Category!"
        else:
            return "Name field cannot be empty."
    else:
        return render_template("editcategory.html",
                               category=category, login_session=login_session)


@app.route('/categories/<int:category_id>/menu/delete',
           methods=['GET', 'POST'])
def categoryDelete(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(MenuItem).filter_by(category_id=category_id)
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if login_session['user_id'] == category.user_id:
            for item in items:
                session.delete(item)
            session.delete(category)
            session.commit()
            return redirect(url_for(('categoryMenu')))
        else:
            return "You are not the Owner of this Category!"
    else:
        return render_template("deletecategory.html",
                               login_session=login_session,
                               category=category)


@app.route('/categories/menu/new', methods=['GET', 'POST'])
def itemAdd():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['NewItem']:
            NewItem = MenuItem(name=request.form['NewItem'],
                               user_id=login_session['user_id'],
                               category_id=request.form['categoryid'],
                               description=request.form['desc'])
            session.add(NewItem)
            session.commit()
            return redirect(url_for('categoryMenu'))
        else:
            return "Name field cannot be empty"
    else:
        # defining categories to get all categories
        # avaialble then add it to
        # Option Select in HTML
        categories = session.query(Category).all()
        return render_template("newitem.html",
                               categories=categories,
                               login_session=login_session)


@app.route('/categories/<int:category_id>/menu/<int:item_id>')
def showItem(category_id, item_id):
    categories = session.query(Category).all()
    menuitems = session.query(MenuItem).filter_by(category_id=category_id)
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(MenuItem).filter_by(id=item_id).first()
    r = ""
    return render_template("items.html", item=item,
                           menuitems=menuitems, r=r,
                           category=category, login_session=login_session,
                           categories=categories)


@app.route('/categories/<int:category_id>/menu/')
def showMenuItems(category_id):
    url_category_id = category_id
    categories = session.query(Category).all()
    menuitems = session.query(MenuItem).filter_by(
        category_id=category_id).order_by(MenuItem.id.desc())
    return render_template("menu.html", menuitems=menuitems,
                           categories=categories,
                           category_id=url_category_id,
                           login_session=login_session)


@app.route('/categories/<int:category_id>/menu/<int:item_id>/delete',
           methods=['POST', 'GET'])
def RemoveMenuItem(item_id, category_id):
    menuitems = session.query(MenuItem).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if login_session['user_id'] == menuitems.user_id:
            session.delete(menuitems)
            session.commit()
            return redirect(url_for(('showMenuItems'),
                            category_id=category_id))
        else:
            return "you are not the owner of this item"
    else:
        return render_template("deletemenuitem.html",
                               login_session=login_session,
                               menuitems=menuitems, category=category)


@app.route('/categories/<int:category_id>/menu/<int:item_id>/edit',
           methods=['POST', 'GET'])
def EditMenuItem(item_id, category_id):
    if 'username' not in login_session:
        return "You are not authorized to view this page, Please login.."
    menuitems = session.query(MenuItem).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['NewName']:
            if login_session['user_id'] == menuitems.user_id:
                menuitems.name = request.form['NewName']
                menuitems.description = request.form['Description']
                session.add(menuitems)
                session.commit()
                return redirect('/categories/')
            else:
                return "You are not the owner of this item."
        else:
            return "Name field cannot be empty."
    else:
        return render_template("editmenuitem.html",
                               menuitems=menuitems,
                               category=category,
                               login_session=login_session,
                               item=menuitems)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'ieOiG6Gt5rwEL1bf49e9T9v1'
    app.run(host='0.0.0.0', port=5000)
