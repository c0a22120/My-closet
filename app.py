from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mycloset.db'
app.config['SECRET_KEY'] = '123kkk123kkk'  # セッションやメッセージに必要
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Clothing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if password != confirm_password:
            flash('パスワードが一致しません。')
            return redirect(url_for('signup'))

        existing_user_email = User.query.filter_by(email=email).first()
        existing_user_username = User.query.filter_by(username=username).first()
        
        if existing_user_email:
            flash('このメールアドレスはすでに登録されています。')
            return redirect(url_for('signup'))
        
        if existing_user_username:
            flash('このユーザー名はすでに登録されています。')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('サインアップが成功しました。ログインしてください。')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            flash('ログイン成功')
            return redirect(url_for('my_closet'))
        else:
            flash('メールアドレスまたはパスワードが間違っています。')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('ログアウトしました。')
    return redirect(url_for('home'))



@app.route('/my-closet')
def my_closet():
    username = session.get('username', 'ゲスト')
    clothes = Clothing.query.all()
    return render_template('my-closet.html', username=username, clothes=clothes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        image = request.files['image']
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        clothing = Clothing(
            image=filename,
            name=request.form['name'],
            brand=request.form['brand'],
            category=request.form['category'],
            price=request.form['price'],
            size=request.form['size'],
            color=request.form['color'],
            gender=request.form['gender'],
            season=request.form['season'],
            description=request.form['description']
        )
        db.session.add(clothing)
        db.session.commit()
        return redirect(url_for('my_closet'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
