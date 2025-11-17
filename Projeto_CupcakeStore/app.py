import sqlite3
import os 
from flask import Flask, render_template, request, redirect, url_for, session

# inicia site
app = Flask(__name__)
app.secret_key = 'senha123' 


# pega a pasta atual e junta com o nome do arquivo
pasta = os.path.dirname(os.path.abspath(__file__))
banco_de_dados = os.path.join(pasta, 'cupcake_store.db')

# home
@app.route('/')
def index():
    # verifica se tem alguem logado
    nome = session.get('cliente_nome') # se nao tiver fica none
    
    # conecta no banco
    con = sqlite3.connect(banco_de_dados)
    con.row_factory = sqlite3.Row # pra pegar pelo nome da coluna
    
    # pega todos os cupcakes
    todos_cupcakes = con.execute('SELECT * FROM Cupcake').fetchall()
    
    con.close() # fecha conexao
    
    return render_template('index.html', cupcakes=todos_cupcakes, cliente_nome=nome)

# pagina detalhes do produto
@app.route('/cupcake/<int:id_do_cupcake>')
def detalhe_cupcake(id_do_cupcake):
    nome = session.get('cliente_nome')
    
    con = sqlite3.connect(banco_de_dados)
    con.row_factory = sqlite3.Row
    
    # pega um cupcake pelo id
    meu_cupcake = con.execute('SELECT * FROM Cupcake WHERE id_cupcake = ?', (id_do_cupcake,)).fetchone()
    
    con.close()
    
    return render_template('detalhe_cupcake.html', cupcake=meu_cupcake, cliente_nome=nome)

# login
@app.route('/login')
def login_page():
    nome = session.get('cliente_nome')
    return render_template('login.html', cliente_nome=nome)

# quando clica em criar conta
@app.route('/registrar', methods=['POST'])
def registrar():
    # pegando o que o digitou no formulario
    cpf_digitado = request.form['cpf']
    nome_digitado = request.form['nome']
    email_digitado = request.form['email']
    senha_digitada = request.form['senha']

    con = sqlite3.connect(banco_de_dados)
    
    try:
        # tenta salvar no banco
        con.execute('INSERT INTO Cliente (cpf, nome, email, senha) VALUES (?, ?, ?, ?)',
                     (cpf_digitado, nome_digitado, email_digitado, senha_digitada))
        con.commit() # salva de verdade
    except:
        con.close()
        return "Deu erro: Esse email ou CPF ja existe!"

    con.close()
    # se deu certo manda pro login
    return redirect(url_for('login_page'))

# quando clica em entrar 
@app.route('/autenticar', methods=['POST'])
def autenticar():
    email_login = request.form['email']
    senha_login = request.form['senha']
    
    con = sqlite3.connect(banco_de_dados)
    con.row_factory = sqlite3.Row
    
    # procura se tem esse usuario
    usuario = con.execute('SELECT * FROM Cliente WHERE email = ? AND senha = ?', (email_login, senha_login)).fetchone()
    con.close()

    if usuario:
        # quando acha salva na sessao pra lembrar dele
        session['cliente_cpf'] = usuario['cpf']
        session['cliente_nome'] = usuario['nome']
        return redirect(url_for('index'))
    else:
        return "Email ou senha errados."

# sair da conta
@app.route('/logout')
def logout():
    session.clear() # limpa tudo
    return redirect(url_for('index'))

# botao de comprar
@app.route('/adicionar_ao_carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    cpf_usuario = session.get('cliente_cpf')
    
    # se nao tiver logado nao deixa comprar
    if not cpf_usuario:
        return redirect(url_for('login_page'))

    id_produto = request.form['cupcake_id']
    qtd = 1 # sempre adiciona 1 por enquanto

    con = sqlite3.connect(banco_de_dados)
    
    # salva na tabela do carrinho
    con.execute('INSERT INTO Carrinho_Item (fk_cliente_cpf, fk_cupcake_id, quantidade) VALUES (?, ?, ?)',
                 (cpf_usuario, id_produto, qtd))
    con.commit()
    con.close()

    return redirect(url_for('ver_carrinho'))

# ver o carrinho
@app.route('/carrinho')
def ver_carrinho():
    nome = session.get('cliente_nome')
    cpf = session.get('cliente_cpf')

    if not cpf:
        return redirect(url_for('login_page'))

    con = sqlite3.connect(banco_de_dados)
    con.row_factory = sqlite3.Row

    #  junta as tabelas pra pegar nome e preco do produto
    sql = '''
        SELECT c.nome, c.sabor, c.preco, c.imagem, ci.quantidade, ci.id_carrinho_item
        FROM Carrinho_Item ci
        JOIN Cupcake c ON ci.fk_cupcake_id = c.id_cupcake
        WHERE ci.fk_cliente_cpf = ?
    '''
    lista_itens = con.execute(sql, (cpf,)).fetchall()

    # calcula total somando tudo
    total = 0
    for item in lista_itens:
        total = total + (item['preco'] * item['quantidade'])
        
    con.close()

    return render_template('carrinho.html',
                           cliente_nome=nome,
                           itens_carrinho=lista_itens,
                           total_carrinho=total)

# botao excluir do carrinho
@app.route('/remover_item/<int:id_do_item>')
def remover_item(id_do_item):
    cpf = session.get('cliente_cpf')
    
    if not cpf:
        return redirect(url_for('login_page'))

    con = sqlite3.connect(banco_de_dados)
    
    # deleta o item so se for desse cliente
    con.execute('DELETE FROM Carrinho_Item WHERE id_carrinho_item = ? AND fk_cliente_cpf = ?',
                 (id_do_item, cpf))
    con.commit()
    con.close()

    return redirect(url_for('ver_carrinho'))

# roda o site
if __name__ == '__main__':
    app.run(debug=True)