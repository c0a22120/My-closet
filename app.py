from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = '123kkk123kkk'  # セッションやメッセージに必要
db = SQLAlchemy(app)

# ユーザーモデルの定義
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# データベースの作成
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

        # パスワード確認
        if password != confirm_password:
            flash('パスワードが一致しません。')
            return redirect(url_for('signup'))

        # ユーザーの存在確認
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('このメールアドレスはすでに登録されています。')
            return redirect(url_for('signup'))

        # ユーザーの登録
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

        # ユーザーの確認
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('ログイン成功')
            return redirect(url_for('my_closet'))
        else:
            flash('メールアドレスまたはパスワードが間違っています。')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/my-closet')
def my_closet():
    return render_template('my-closet.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
