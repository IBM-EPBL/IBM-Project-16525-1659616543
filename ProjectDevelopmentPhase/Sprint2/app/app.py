from forms import LoginForm, RegisterForm, Transaction, Customize
from flask import Flask, render_template, url_for, redirect, flash, make_response, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from sendgrid_integration import SendGrid
from database import insert_user_credential, insert_user_profile, fetchUserByEmail, fetchUserById, insert_user_transaction,fetch_user_transactions,global_view_query, insert_user_customize, initialise

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = 'B7-1A3E'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "error"

sendgrid_obj = SendGrid()


class User:   

    def __init__(self, id, email):
        self.id = id
        self.email = email

    def to_json(self):        
        return {
                "email": self.email
        }

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    user = fetchUserById(user_id)
    if user == []:
        return None
    user = user[0]
    usr_obj = User(user["ID"], user["EMAIL"])
    return usr_obj


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = fetchUserByEmail(form.email.data)
        if user != []:
            user = user[0]
            if user["PASSWORD"] == form.password.data:
                usr_obj = User(user["ID"], user["EMAIL"])
                login_user(usr_obj)
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('email', user['EMAIL'])
                return resp

            else:
                error = "Invalid Credentials"
        else:
            error = "There is no account registered with this email"

    return render_template('login.html', form=form, error = error)

@app.route('/home')
@login_required
def home():
    print("request cookies",request.cookies)
    return render_template('home.html',global_view_query = global_view_query)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        entered_email = form.email.data
        entered_password = form.password.data
        resp = make_response(render_template('email_confirmation.html', email= entered_email))
        resp.set_cookie('email', entered_email)
        resp.set_cookie('password', entered_password, max_age=3000)
        # otp = sendgrid_obj.confirmation_mail(entered_email)
        otp = 5000
        if otp == None:
            return render_template('register.html', form=form, error="Please try again!")
        
        resp.set_cookie('otp', str(otp),max_age=3000)
        return resp

    return render_template('register.html', form=form)


@app.route('/confirm_email', methods=['POST'])
def confirm_email():
    otp_generated = request.cookies.get('otp')
    # otp_generated = 5000
    email = request.cookies.get('email')
    password = request.cookies.get('password')
    if otp_generated is None:
        print("otp expired")
        return render_template('email_confirmation.html', email= email, expired="OTP expired!")
    
    otp_received = request.form['otp']

    if str(otp_generated) == otp_received:
        # insert the new user credential
        insert_user_credential(email, password)

        res = fetchUserByEmail(email)
        login_id = res[0]["ID"]

        # insert new user profile for created credential
        insert_user_profile(login_id)
        resp = make_response(redirect(location=url_for('login')))

        # delete the otp and password cookies before rendering the page
        resp.set_cookie('password', expires=0)
        resp.set_cookie('otp', expires=0)
        return resp

    else:
        resp = make_response(render_template('email_confirmation.html', email= email, error="OTP mismatch! Retry"))
        return resp

@app.route('/add_transaction', methods=['GET','POST'])
def add_transaction():
    form = Transaction();
    useremail = request.cookies.get('email')
    if form.validate_on_submit():
        transaction = form.transaction.data
        mode = form.mode.data
        category = form.category.data
        datestamp = form.datestamp.data
        note = form.note.data
        insert_user_transaction(useremail, transaction, mode, category, datestamp, note)
        return render_template('home.html', error="Transaction recorded")
    return render_template('add_transaction.html', form=form, error = "Nil")

@app.route('/customize', methods=['GET','POST'])
def add_customization():
    form = Customize();
    useremail = request.cookies.get('email')
    if form.validate_on_submit():
        name = form.name.data
        budget = form.budget.data
        total_spent = form.total_spent.data
        phone = form.phone.data
        profession = form.profession.data
        alert = form.alert.data
        insert_user_customize(useremail, name, budget, total_spent, phone, profession, alert)
        return render_template('home.html', error="Customization set successfully")
    return render_template('customize.html', form=form)
 
    
@app.route('/view_transaction', methods=['GET','POST'])
def view_transaction():
    return render_template('view_transaction.html',fetch_user_transactions= fetch_user_transactions)

app.run("0.0.0.0", 5000,debug=True)