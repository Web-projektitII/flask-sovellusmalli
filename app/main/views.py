from flask import render_template, redirect, jsonify, url_for, abort, flash, current_app, request, send_from_directory, send_file
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Role, User
from ..decorators import admin_required
import os, json, boto3
from botocore.client import Config
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

ALLOWED_EXTENSIONS = { 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/img/')
@main.route('/img/<path:filename>')
def img(filename = None):
    # Profiilikuvat Flask-sovelluskansiossa profiilikuvat,
    # paitsi oletusprofiilikuva static-kansiossa.
    app = current_app._get_current_object()
    if filename is None:
        return send_from_directory('static','default_profile.png')
    elif app.config['KUVAPALVELU'] == 'local':
        basedir = os.path.abspath('.')
        kuvapolku = os.path.join(basedir, app.config['KUVAPOLKU'])
        # print("ABSOLUUTTINEN KUVAPOLKU:"+kuvapolku)
        # return send_from_directory('c://projektit/flask-sovellusmalli/app/profiilikuvat/', filename)
        return send_from_directory(kuvapolku, filename)
    
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile-all/', methods=['GET', 'POST'])
@login_required
def edit_profile_all():
    # Profiili, jossa on myös profiilikuva
    form = EditProfileForm()
    app = current_app._get_current_object()
    kuvapalvelu = app.config['KUVAPALVELU']
    KUVAPOLKU = app.config['KUVAPOLKU']
    if form.validate_on_submit():
        # check if the post request has the file part
        kuvanimi = form.img.data
        if 'file' in request.files and file.filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Lomakkeelta lähetettynä paikallinen tallennus,
                # S3-tallennus tehty erikseen Javascriptillä
                kuvanimi = secure_filename(file.filename)
                filename = str(current_user.id) + '_' + kuvanimi
                file.save(os.path.join(KUVAPOLKU, filename))
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.img = kuvanimi
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.img.data = current_user.img
    if current_user.img:
        kuva = str(current_user.id) + '_' + current_user.img 
        if kuvapalvelu != 'local':
            kuva = os.path.join(KUVAPOLKU, kuva)
    else:
        kuva = ''    
    # return redirect(url_for('profile'))
    return render_template('edit_profile_S3.html', form=form, kuva=kuva)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/edit-profile_S3', methods=['GET', 'POST'])
@login_required
def edit_profile_S3():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile_S3.html', form=form)


@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    # users = User.query.all() 
    if request.form.get('painike'):
        users = request.form.getlist('users')
        if len(users) > 0:
            query_start = "INSERT INTO users (id,active) VALUES "
            query_end = " ON DUPLICATE KEY UPDATE active = VALUES(active)"
            query_values = ""
            active = request.form.getlist('active')
            for v in users:
                if v in active:
                    query_values += "("+v+",1),"
                else:
                    query_values += "("+v+",0),"
            query_values = query_values[:-1]
            query = query_start + query_values + query_end
            # print("\n"+query+"\n")
            # result = db.session.execute('SELECT * FROM my_table WHERE my_column = :val', {'val': 5})
            db.session.execute(query)
            db.session.commit()
            # return query
            #return str(request.form.getlist('users')) + \
            #       "<br>" + \
            #        str(request.form.getlist('active'))
        else:
            flash("Käyttäjälista puuttuu.")
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.name).paginate(
        page=page, per_page=current_app.config['FS_POSTS_PER_PAGE'],
        error_out=False)
    lista = pagination.items
    return render_template('users.html',users=lista,pagination=pagination,page=page)

@main.route('/poista', methods=['GET', 'POST'])
@login_required
@admin_required
def poista():
    # print("POISTA:"+request.form.get('id'))
    user = User.query.get(request.form.get('id'))
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash(f"Käyttäjä {user.name} on poistettu")
        return jsonify("OK, käyttäjä on poistettu.")
    else:
        return jsonify("Virhe: käyttäjää ei löydy.")

@main.route('/sign-s3/')
@login_required
def sign_s3():
  S3_BUCKET = os.environ.get('S3_BUCKET')
  AWS_REGION = os.environ.get('AWS_REGION') 
  file_name = request.args.get('file-name')
  file_type = request.args.get('file-type')
  kuva = str(current_user.id) + '_' + file_name
  # s3 = boto3.client('s3')
  s3 = boto3.client('s3',
    config=Config(signature_version='s3v4'),
    region_name=AWS_REGION)
  
  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = kuva,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )
  dump = json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, kuva)
  })
  return dump


@main.route('/save-local', methods=['GET', 'POST'])
@login_required
def save_local():
    # cwd = os.getcwd()
    # print("WORKING DIRECTORY:"+cwd)
    app = current_app._get_current_object()
    KUVAPOLKU = app.config['KUVAPOLKU']
    virhe = ''
    msg = ''
    try:
        if 'file' in request.files:
            file = request.files['file']
    except RequestEntityTooLarge as e:
        app.logger.info(e)
        koko = round(app.config['MAX_CONTENT_LENGTH'] / (1000 * 1000))
        msg = f"Kuvaa ei tallennettu, sen koko saa olla maks. {koko} MB."
        return json.dumps({'virhe':msg})
    if file and file.filename != '' and allowed_file(file.filename):
        kuvanimi = secure_filename(file.filename)
        filename = str(current_user.id) + '_' + kuvanimi
        file.save(os.path.join(KUVAPOLKU, filename))
        msg = f"Tiedosto tallennettiin nimellä {filename}."
    else:
        virhe = "Tiedostoa ei annettu."
    dump = json.dumps({
        'img':kuvanimi,
        'kuva':filename,
        'msg': msg,
        'virhe': virhe
        })
    return dump
