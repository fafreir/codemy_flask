from flask import Flask, flash, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, validators
from wtforms.validators import DataRequired
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Cursos\\Codemy_Flask\\users.db'

app.config['SECRET_KEY'] = 'fabricio'


app.config['SQLALCHEMY_DATABASE_URI'] = \
    '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        usuario='root',
        senha='password',
        servidor='localhost',
        database='our_users'
)

db = SQLAlchemy(app)  # Inicializar o BD
# migrate = Migrate(app, db)

migrate = Migrate(app, db)


class Users(db.Model):  # Create Model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120), )
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __rep__(self):
        return '<Name %r>' % self.name


with app.app_context():
    db.create_all()


class UserForm(FlaskForm):  # Validar os campos
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite color")
    # password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!')])
    password_hash = PasswordField('Password', [validators.data_required(
    ), validators.EqualTo('password_hash2', message='Password must match!')])
    password_hash2 = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


@ app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(
                form.password_hash.data, method='pbkdf2:sha256')
            user = Users(name=form.name.data, email=form.email.data,
                         favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.email.favorite_color = ''
        form.password_hash = ''
        flash('User added Sucessfully!')
    our_users = Users.query.order_by(Users.id)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@ app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@ app.route('/')
def index():
    flash("Welcome to website")
    first_name = "fabricio"
    bold = 'This video is <strong> really fantastic </strong>'
    lista = ['Embraer', 'Sonda', 1989]
    return render_template('index.html', first_name=first_name, video=bold, lista=lista)


@ app.errorhandler(404)  # Invalid URL
def page_not_found(e):
    return render_template("404.html"), 404


@ app.errorhandler(500)  # Internal Server Error
def page_not_found(e):
    return render_template("500.html"), 500

# Create a Form Class


class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


@ app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        # form.name.data = ''
        flash("Form submitted Sucessfully!")
    return render_template("name.html", name=name, form=form)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error!  Looks like there was a problem...try again!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Sucessfully!!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash('Whoops! There was a problem deleting user, try again...')
        return render_template('add_user.html', form=form, name=name, our_users=our_users)


if __name__ == '__main__':
    app.run(debug=True)
