from flask import Flask, render_template, request, redirect, session
import sqlite3, os
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'segredo')
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/')
def index(): return render_template('index.html')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()
        if user:
            session['user'] = dict(user)
            if email == 'admin@loja.com': return redirect('/admin')
            return redirect('/loja')
        else: return render_template('login.html', erro='Usuário ou senha incorretos.')
    return render_template('login.html')
@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
            conn.commit()
            return redirect('/login')
        except:
            return render_template('cadastro.html', erro='Email já cadastrado.')
        finally:
            conn.close()
    return render_template('cadastro.html')
@app.route('/loja')
def loja():
    if 'user' not in session: return redirect('/login')
    return render_template('loja.html', nome=session['user']['nome'])
@app.route('/admin')
def admin():
    if 'user' not in session or session['user']['email'] != 'admin@loja.com': return redirect('/login')
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin.html', users=users)
@app.route('/logout')
def logout(): session.clear(); return redirect('/')
