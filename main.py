from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
import cgi
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:goldie@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'c337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
#    completed = db.Column(db.Boolean)
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title, body, owner):
        self.title = title
#        self.completed = False
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_error = ""
        email_error = ""

        if not password:
            password_error = "Enter your password."
        if not email:
            email_error = "Enter your email."

        if password_error or email_error:
            return render_template("login.html", password=password, passwordError=password_error, email=email, emailError=email_error)

        user = User.query.filter_by(email=email).first()
        not_registered_error = ""
        if user and user.password == password:
            session['email'] = email
            flash("Logged In" + email)
            return redirect("/blog")
        else:
            not_registered_error = "Please register first!"
            return render_template("login.html", not_registeredError=not_registered_error)
#            flash('User password incorrect, or user does not exist', 'Error!')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
#        email = request.form['email']
#        password = request.form['password']
#        verify = request.form['verify']
        password = cgi.escape(request.form['password'])
        verify = cgi.escape(request.form['verify'])
        email = cgi.escape(request.form['email'])
        password_error = ""
        email_error = ""
        verify_error = ""


        if not password:
            password_error = "Please enter a password."
        elif len(password) < 3:
            password_error = "Password should be between 3 and 20 characters."
        elif len(password) > 20:
            password_error = "Password should be between 3 and 20 characters."
        if verify != password:
            verify_error = "Please match this password with the first one."
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        if match == None:
            email_error = "Please enter a valid email."

        if password_error or verify_error or email_error:
            return render_template("register.html", password=password, passwordError=password_error, verify=verify, verifyError=verify_error, email=email, emailError=email_error)

        existing_user = User.query.filter_by(email=email).first()
        duplicate_user_error = ""
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            flash('Welcome' + email)
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            return render_template("register.html", duplicateError=duplicate_user_error)

    return render_template('register.html')


#@app.route('/', methods=['POST', 'GET'])
#def index():
#    return redirect('/blog')


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        
        blog_title_error = ""
        blog_body_error = ""

        if blog_title == "":
            blog_title_error = "Include a title!"
        if blog_body == "":
            blog_body_error = "Include a post!"

        if not blog_body_error and not blog_title_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')

        return render_template('newpost.html', blog_body_error=blog_body_error, blog_title_error=blog_title_error, blog_body=blog_body, blog_title=blog_title)
    

    blogs = Blog.query.all()

    return render_template('newpost.html', title="Add Blog Entry", blogs=blogs)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    owner = User.query.filter_by(email=session['email']).first()
    blog_id = request.args.get('id')
    blogs = Blog.query.filter_by(owner=owner).all()

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("post.html", title=post.title, body=post.body)

    return render_template('blog.html', title="Build A Blog", blogs=blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("home.html")

if __name__ == '__main__':
    app.run()