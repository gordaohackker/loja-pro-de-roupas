from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'segredo')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Produtos disponíveis na loja
produtos_disponiveis = [
    {'id': 1, 'nome': 'Vestido Floral', 'preco': 89.90},
    {'id': 2, 'nome': 'Conjunto Verão', 'preco': 119.90},
    {'id': 3, 'nome': 'Blusa Cropped', 'preco': 49.90}
]

@app.route('/')
def index():
    return render_template('index.html')

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
            if email == 'admin@loja.com':
                return redirect('/admin')
            return redirect('/loja')
        else:
            return render_template('login.html', erro='Usuário ou senha incorretos.')
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
    if 'user' not in session:
        return redirect('/login')
    return render_template('loja.html', nome=session['user']['nome'], produtos=produtos_disponiveis)

@app.route('/admin')
def admin():
    if 'user' not in session or session['user']['email'] != 'admin@loja.com':
        return redirect('/login')
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Carrinho de compras
@app.route('/adicionar/<int:produto_id>')
def adicionar(produto_id):
    if 'carrinho' not in session:
        session['carrinho'] = []
    for produto in produtos_disponiveis:
        if produto['id'] == produto_id:
            session['carrinho'].append(produto)
            break
    session.modified = True
    return redirect(url_for('loja'))

@app.route('/carrinho')
def carrinho():
    if 'user' not in session:
        return redirect('/login')
    carrinho = session.get('carrinho', [])
    total = sum([p['preco'] for p in carrinho])
    return render_template('carrinho.html', carrinho=carrinho, total=total)

@app.route('/remover/<int:index>')
def remover(index):
    if 'carrinho' in session:
        try:
            session['carrinho'].pop(index)
            session.modified = True
        except IndexError:
            pass
    return redirect('/carrinho')

@app.route('/finalizar')
def finalizar():
    session.pop('carrinho', None)
    return "<h2>Compra finalizada com sucesso! Obrigado.</h2><a href='/loja'>Voltar para loja</a>"

if __name__ == '__main__':
    app.run(debug=True)
