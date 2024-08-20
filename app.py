from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '123'  # セッション管理のために必要です。適切な秘密鍵に変更してください。

# 仮のユーザー情報（通常はデータベースに保存される）
users = {
    'test@example.com': '123'  # メールアドレスとパスワードのマッピング
}

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

        if password == confirm_password:
            # サインアップが成功したらログインページにリダイレクト
            flash('サインアップが成功しました。ログインしてください。')
            return redirect(url_for('login'))
        else:
            # パスワードが一致しない場合、エラーメッセージを表示する
            flash('パスワードが一致しません。もう一度試してください。')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # 仮のユーザー認証処理
        if email in users and users[email] == password:
            flash('ログイン成功！')
            return redirect(url_for('my_closet'))  # ログイン成功後にリダイレクトするページ
        else:
            flash('メールアドレスまたはパスワードが間違っています。')

    return render_template('login.html')


@app.route('/my-closet')
def my_closet():
    return render_template('my-closet.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
