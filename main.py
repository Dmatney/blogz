"""build-a-blog"""
from flask import Flask,request,redirect,render_template,session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:z1ppysk1ppy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'yoasdfawerur_seasdfcreasft_key'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(256))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    
    def __init__ (self, title, body,owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(128))
    password = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','signup','validate_info','blog', 'index',"/signup"]
    if request.endpoint not in allowed_routes and 'user' not in session:
        print("1")
        return redirect('/login')

@app.route('/')
def index():
    #todo fix this for blogz
    return redirect('blog')

@app.route('/signup', methods=['POST','GET'])
def validate_info():
    if request.method == 'GET':
        return render_template('signup.html')
    username = request.form['username']
    password = request.form['password']
    verifypassword = request.form['verifypassword']
    usernameerror = ''
    passworderror = ''
    if username == '':
        usernameerror = "Please add a user name"
    elif ' ' in username:
        usernameerror = "The user name can not contain spaces"
    elif len(username) <3 or len(username) > 20:
        usernameerror = "The user name must be between 3 and 20 characters long"
    if password == '' or verifypassword == '':
        passworderror = 'Please add a password and verify it'
    elif password != verifypassword:
        passworderror = 'Password and verify password fields MUST match'
    elif ' ' in password:
        passworderror = 'Password can not contain spaces'
    elif len(password) <3 or len(password) > 20:
        passworderror = 'Password must be between 3 and 20 characters long'
    if not usernameerror and not passworderror:
        new_user = User(username,password)
        db.session.add(new_user)
        db.session.commit()
        users = User.query.filter_by(username=username)
        user = users.first()
        session['user'] = user.username
        return redirect('/blog')
    else:
        return render_template('signup.html', usernameerror = usernameerror, passworderror = passworderror, username = username)
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        usererror = ""
        passworderror = ""

        if users.count() == 0:
            usererror = "Username does not exist"
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                return redirect("/newpost")
            passworderror = "Wrong password"
        return render_template('login.html', usererror = usererror, passworderror = passworderror)

@app.route('/index')
def home():
    user = User.query.all()
    username = request.args.get('username')
    if username:
        x = User.query.filter_by(username = username).first()
        return render_template('index.html', user = x)
    return render_template('index.html', user = user)
@app.route("/logout", methods=['POST', 'GET'])
def logout():
    del session['user']
    return redirect("/")

@app.route('/blog')
def blog():
    blog = Blog.query.all()
    blog_id = request.args.get('id')
    user = User.query.all()
    if blog_id:
        x = Blog.query.filter_by(id = blog_id)
        return render_template('blog.html', blog = x, user = user)
    owner_id = request.args.get('owner_id')
    
    if owner_id:  
        x = Blog.query.filter_by(owner_id = owner_id)
        return render_template('blog.html', blog = x, user = user)
    return render_template('blog.html', blog = blog, user = user)

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    error = ''
    username = session.get('user')
    print(username)
    user = User.query.filter_by(username=username).first()
    owner_id = user.id
    if request.method == 'POST':
        title = request.form['title']
        post = request.form['post']
        error_1 = ""
        error_2 = ""
        if not title:
            error_1 = "Please add a title"
        if not post:
            error_2 = "Please add a post"
        if not title or not post:
            return render_template('submit.html', error_1 = error_1, error_2 = error_2)
        else:
            new_blog = Blog(title, post, owner_id)
            db.session.add(new_blog)
            db.session.commit()            
            blog_id = './blog?id='+str(new_blog.id)
            return redirect(blog_id)
    
    return render_template('submit.html', error = error)

if __name__ == '__main__':
    app.run()