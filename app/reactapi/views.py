from flask import render_template, redirect, request, url_for, flash, \
    current_app, jsonify, make_response
from flask_login import (
    login_user, 
    logout_user, 
    login_required, 
    current_user)
from . import reactapi
from .. import db
from ..models import User
from ..email import send_email
from ..auth.forms import LoginForm, RegistrationForm, ProfileForm
from flask_cors import cross_origin
from flask_wtf.csrf import generate_csrf,CSRFError
import sys

def createResponse(message):
    # CORS:n vaatimat Headerit
    default_origin = 'http://localhost:3000'
    origin = request.headers.get('Origin',default_origin)
    response = make_response(jsonify(message))    
    response.headers.set('Access-Control-Allow-Credentials','true')
    response.headers.set('Access-Control-Allow-Origin',origin) 
    return response


@reactapi.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    message = {'virhe':'csrf-token puuttuu.'}
    return createResponse(message)


@reactapi.app_errorhandler(401)
def page_not_allowed(e):
    message = {'virhe':'Kirjautuminen puuttuu.'}
    return createResponse(message)


@reactapi.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'reactapi' \
            and request.endpoint != 'static':
        return "Unconfirmed user"


@reactapi.route("/getcsrf", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_csrf():
    token = generate_csrf()
    response = jsonify({"detail": "CSRF cookie set"})
    response.headers.set('Access-Control-Expose-Headers','X-CSRFToken') 
    response.headers.set("X-CSRFToken", token)
    return response


# Huom. Tässä on jäetty 'OPTIONS' ja origins varmuuden vuoksi,
# axios-kutsuja ei ole testattu ilman niitä,
# fetch-kutsut toimivat ilmankin.
# Axios on korvattu fetchillä, jotta käyttäjän istunto säilyy eli
# sen vaatimat evästeet välittyvät selaimelta oikein. 
@reactapi.route('/logout')
@cross_origin(supports_credentials=True)
# Huom. Header asettuu automaattisesti oikein: 
# Access-Control-Allow-Origin: http://localhost:3000
@login_required
def logout():
    # sessio = request.cookies.get('session')
    # print(f"reactapi/logout,sessio:{sessio}")
    logout_user()
    return "OK"


@reactapi.route('/signin', methods=['GET','POST'])
@cross_origin(supports_credentials=True)
def signin():
    form = LoginForm()
    sys.stderr.write(f"\nviews.py,SIGNIN:{form.email.data}'\n")
    if form.validate_on_submit():
        sys.stderr.write(f"\nviews.py,SIGNIN, validate_on_submit OK'\n")
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # next = request.args.get('next')
            # if next is None or not next.startswith('/'):
            #    next = url_for('main.index')
            sys.stderr.write('\nviews.py,SIGNIN:OK\n')
            return 'OK'
        else:
            response = jsonify({'virhe':'Väärät tunnukset'})
            # response.status_code = 200
            return response
            # return "Väärä salasana"    
    else:
        # print("validointivirheet:"+str(form.errors))
        response = jsonify(form.errors)
        # response.status_code = 200
        return response
        # return "Virhe lomakkeessa"
  

@reactapi.route('/signup', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def signup():
    form = RegistrationForm()
    sys.stderr.write('\nviews.py,SIGNUP,email:'+form.email.data+'\n')
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        # flash('A confirmation email has been sent to you by email.')
        return "OK"
    else:
        # print("validointivirheet:"+str(form.errors))
        # return "Virhe lomakkeessa:"+str(form.errors)
        response = jsonify(form.errors)
        response.status_code = 200
        return response


@reactapi.route('/haeProfiili', methods=['GET', 'POST'])
# Tarvitaanko tätä, unsafe cross domain request?
# credentials:'include' => unsafe request => origin määritettävä muuksi kuin '*'
# @cross_origin(supports_credentials=True,origin='localhost:3000'
# Evästeet lähetetään myös cross domain
# @cross_origin(supports_credentials=True,origins=['http://localhost:3000'])
@cross_origin(supports_credentials=True)
@login_required
# Huom. Header Access-Control-Allow-Credentials: true ei välity,
# jos ei ole kirjautunut eli session-evästettä ei saavu, ja syntyy
# CORS-virhe. Näin myös, jos @login_manager.login_view on asettamatta, sillä tällöin 
# suoritus päättyy 401-virheeseen. Tämä tilanne käsitellään tässä
# Blueprintin 401-virhekäsittelijällä.  
def haeProfiili():
    id = current_user.get_id()
    # taulun rivi objektiksi
    print("RESPONSE:",current_user.get_id())
    user = {
        'email':current_user.email,
        'username':current_user.username
        }
    response = jsonify(user)
    response.status_code = 200
    return response


@reactapi.route('/tallennaProfiili', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def tallennaProfiili():
    form = ProfileForm()
    sys.stderr.write('\nviews.py,tallennaProfiili,email:'+form.email.data+'\n')
    if form.validate_on_submit():
        user = current_user
        print('\n'\
            "user.email:",user.email,'\n'\
            "current_user.email:",current_user.email,'\n'\
            "form.email.data.lower():",form.email.data.lower(),'\n')
        '''
        Huom. 
        user-objektin muutokset näkyvät myös current_user-objektissa
        db.session.add(user)-komentoa ei tarvita
        vrt. 
        form.populate_obj(user) tai form.populate_obj(current_user)
        form = ProfileForm(obj=user)
        '''
        if current_user.email != form.email.data.lower():
            print("tallennaProfiili, uusi sähköpostiosoite")
            user.confirmed = False
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        # Huom. 
        # user.username = form.username.data
        # db.session.commit()   
        # toimisi myös 
        # Huom. Tässä muuttuu myös current_user
        form.populate_obj(user)
        print('\n'\
            "user.email:",user.email,'\n'\
            "current_user.email:",current_user.email,'\n'\
            "form.email.data.lower():",form.email.data.lower(),'\n')
        db.session.commit()   
        # flash('A confirmation email has been sent to you by email.')
        return "OK"
    else:
        # print("validointivirheet:"+str(form.errors))
        # return "Virhe lomakkeessa:"+str(form.errors)
        response = jsonify(form.errors)
        response.status_code = 200
        return response
