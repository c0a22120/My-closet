from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

db = SQLAlchemy()

# ユーザーの登録カラム
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    profile_image = db.Column(db.String(120), default='default_profile.png')

# 服の登録カラム
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

# アプリケーションの設定
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mycloset.db'
    app.config['SECRET_KEY'] = '123kkk123kkk'  # セッションやメッセージに必要
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

    db.init_app(app)

    with app.app_context():
        db.create_all()  # データベースのテーブルを作成する

    return app


app = create_app()

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

    # ユーザー情報を取得
    user = User.query.filter_by(username=username).first()

    # ユーザーが見つからない場合はデフォルトの値を設定
    if user is None:
        profile_image = 'default.png'  # デフォルトの画像
    else:
        profile_image = user.profile_image

    clothing_count = len(clothes)  # 服の数をカウント
    total_amount = sum(clothing.price for clothing in clothes)  # 合計金額を計算

    return render_template(
        'my-closet.html',
        username=username,
        clothes=clothes,
        user=user,
        profile_image=profile_image,
        clothing_count=clothing_count,
        total_amount=total_amount
    )


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


@app.route('/edit-clothing/<int:clothing_id>', methods=['GET', 'POST'])
def edit_clothing(clothing_id):
    clothing = Clothing.query.get_or_404(clothing_id)  # 服の情報を取得

    if request.method == 'POST':
        # POST リクエスト時に服の情報を更新
        clothing.name = request.form['name']
        clothing.brand = request.form['brand']
        clothing.category = request.form['category']
        clothing.price = request.form['price']
        clothing.size = request.form['size']
        clothing.color = request.form['color']
        clothing.gender = request.form['gender']
        clothing.season = request.form['season']
        clothing.description = request.form['description']

        db.session.commit()  # データベースに変更を保存
        flash('服の情報が更新されました！')
        return redirect(url_for('my_closet'))


    return render_template('edit_clothing.html', clothing=clothing)



@app.route('/update-profile-image', methods=['GET', 'POST'])
def update_profile_image():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user = User.query.filter_by(username=session['username']).first()
        file = request.files.get('profile_image')

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/uploads', filename))
            user.profile_image = filename
            db.session.commit()

        return redirect(url_for('my_closet'))

    return render_template('update_profile_image.html')

@app.route('/delete-clothing/<int:clothing_id>', methods=['POST'])
def delete_clothing(clothing_id):
    # 対象の服をデータベースから取得
    clothing = Clothing.query.get_or_404(clothing_id)

    db.session.delete(clothing)
    db.session.commit()

    flash('アイテムが削除されました。')
    return redirect(url_for('my_closet'))

if __name__ == '__main__':
    app.run(debug=True)
