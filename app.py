from flask import Flask, render_template, redirect, url_for, request, make_response, flash, session
import math
import psycopg2

# LIBs de cadastro de fotos
from PIL import Image
import os   #Esta lib é para o sistema interagir com o Windows
import base64
from io import BytesIO #Esta lib é para o sistema encriptar a foto

# LIBs de geração de PDF
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from reportlab.lib.pagesizes import letter #Tamanho da folha
from reportlab.pdfgen import canvas #Canvas é a folha de papel
from reportlab.lib import colors #Cores
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle #Estilos de parágrafos
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph #TableStyle é para estilizar a tabela

# LIBs de autenticação
from functools import wraps #Decorator
from werkzeug.security import generate_password_hash, check_password_hash #Hash para senhas
from datetime import timedelta #Para o tempo de expiração do token
from dotenv import load_dotenv #Carregar variáveis de ambiente do arquivo .env
from flask_wtf.csrf import CSRFProtect #Proteção contra CSRF (Cross-Site Request Forgery)
load_dotenv() #Carregar as variáveis de ambiente do arquivo .env



app = Flask(__name__)

#Configurações de segurança
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key-granddrive')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #Tempo de expiração do token
csrf = CSRFProtect(app) #Proteção contra CSRF (Cross-Site Request Forgery)

# Conexão com o banco de dados, utilizando token/chave para autenticar
def connection_db():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_NAME', 'granddrive'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', '1234')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ================= ROTAS DE NAVEGAÇÃO ====================

# Rota de autenticação
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Tratamento para verificar se usuário digitou todos os campos
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error') # Mostra mensagem embaixo dos inputs
            return redirect(url_for('login.html'))

        # Checa se a conexão com o banco de dados foi realizada
        conn = connection_db()
        if not conn:
            flash('Erro ao conectar ao banco de dados.', 'error')
            return redirect(url_for('login.html'))
        
        # Tratamento de exceções
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user and (user[2], password):
                    session.permanent = True # Mantém a sessão ativa
                    session['logged_in'] = True # Cria a sessão de login
                    session['username'] = user[1] # Cria a sessão do usuário
                    session['user_id'] = user[0] # Cria a sessão do ID do usuário
                    flash('Login realizado com sucesso!', 'success') # Mostra mensagem de sucesso
                    return redirect(url_for('home')) # Redireciona para a página inicial
                else:
                    flash('Usuário ou senha inválidos.', 'error')
                    return redirect(url_for('login.html')) # Redireciona para a página de login
                        
        except Exception as e:
            print(user)
            flash(f'Erro ao realizar login: {e}', 'error') # Mostra mensagem de erro
        
        finally:
            if conn:
                conn.close()
    return render_template('login.html')
        
# Rota de navegação inicial
@app.route('/')
def home():
    return render_template('main.html')

# Rota de navegação de cadastro
@app.route('/n-cadastro')
def n_cadastro():
    return render_template('index.html')

# Rota de navegação de login
@app.route('/n-login', methods=['GET'])
def n_login():
    return render_template('login.html')

# Rota de navegação consulta clientes/inicio
@app.route('/n_consulta-clientes', methods=['GET'])
def n_consulta_clientes():
    return redirect(url_for('paginacao', page=1))

# Rota de navegação de filtro/inicio
@app.route('/n_filter', methods=['GET'])
def n_filter():
    return render_template('filter-find.html')


# =============== FUNÇÕES ==================

# Rota para a página de cadastro
@app.route('/cadastro', methods=['POST'])
def cadastro():
    if request.method == 'POST':
        try:
            clientname = request.form['name']
            surname = request.form['surname']
            cpf = request.form['cpf']
            birth = request.form['birth']
            city = request.form['city']
            country = request.form['country']

            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO clients (clientname, surname, cpf, birth, city, country) VALUES (%s, %s, %s, %s, %s, %s)", (clientname, surname, cpf, birth, city, country))
            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('shop', message='Cadastro realizado com sucesso!'))

        except Exception as e:
            return redirect(url_for('home', message=f'Erro ao realizar cadastro: {e}'))

# Rota de navegação de locação
@app.route('/shop')
def shop():
    return render_template('shop.html')

# Rota para a página de locação
@app.route('/shop', methods=['POST'])
def rental():
    if request.method == 'POST':
        try:
            car = request.form['carname']
            client = request.form.get('idclient', 'Cliente não especificado')
            date = request.form['datestart']
            days = request.form['dateend']
            prices = request.form['prices']
            availability = request.form['availability']

            connection = connection_db()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO rentals (car, client, datestart, dateend, prices, availability) VALUES (%s, %s, %s, %s, %s, %s)", 
                          (car, client, date, days, prices, availability))
            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('consulta', message='Locação realizada com sucesso!'))
        except Exception as e:
            return redirect(url_for('shop', message=f'Erro ao realizar locação: {e}')) 
        
# Rota para a página de consulta
@app.route("/consulta", methods=['GET', 'POST'])
def consulta():
    try:
        message = request.args.get('message')
        connection = connection_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM modelscars")
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('consulta.html', result=result, message=message)
    except Exception as e:
        return redirect(url_for('home', message=f'Erro na consulta: {e}'))

# Rota para a página de filtro
@app.route("/filter", methods=['GET', 'POST'])
def filtro():
    try:
        if request.method == 'POST':
            filter_find = request.form['filter_input']
            connection = connection_db()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM clients WHERE LOWER(clientname) LIKE LOWER(%s)", (f'%{filter_find}%',))
                finders = cursor.fetchall()

            connection.close()  # Feche a conexão após a consulta
            return render_template('filter-find.html', finders=finders)

        return render_template('filter-find.html', finders=None)

    except Exception as e:
        return redirect(url_for('home', message=f'Erro ao realizar consulta: {e}'))

# Rota para a página de paginação
@app.route("/paginacao", methods=['GET', 'POST'])
def paginacao():
    page = request.args.get('page', 1, type=int)
    quantidade = 5

    connection = connection_db()
    cursor = connection.cursor()

    #Aqui ele vai contar a quantidade de registros
    cursor.execute('SELECT count(*) FROM clients')
    total_items = cursor.fetchone()[0]

    #Calcular o número total de páginas
    total_pages = math.ceil(total_items / quantidade)

    #Calcular a saída da consulta
    offset = (page - 1) * quantidade

    cursor.execute('''SELECT id, clientname, surname, cpf, birth, city, country FROM clients ORDER BY clientname LIMIT %s OFFSET %s''', (quantidade, offset))

    clientes = cursor.fetchall()
    cursor.close()
    connection.close()

    # Dicionário de valores
    # clientes_lista = []
    # for cliente in clientes:
    #     clientes_lista.append({
    #         'id':cliente[0],
    #         'name':cliente[1],
    #         'surname':cliente[2],
    #         'cpf':cliente[3],
    #         'birth':cliente[4],
    #         'city':cliente[5],
    #         'country':cliente[6]
    #     })

    #return render_template('grid_completo.html', clientes=clientes_lista, page=page, total_pages=total_pages)
    return render_template('consulta-clientes.html', clientes=clientes, page=page, total_pages=total_pages)

# Rota para a página de edição
@app.route("/cadastro_foto", methods=['GET', 'POST'])
def cadastro_foto():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        matricula = request.form['matricula']
        cidade = request.form['cidade']
        estado = request.form['estado']
        foto = request.files['foto']

        if foto:
            #Lê a imagem como dados binários
            foto_binaria = foto.read()

            conn = connection_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientenovo2 (nome, cpf, cidade, matricula, estado, foto) VALUES (%s, %s, %s, %s, %s, %s)", (nome, cpf, cidade, matricula, estado, foto_binaria))
            conn.commit()
            cursor.close()
            conn.close()

        return redirect(url_for('cadastro_foto'))
   
    return render_template('upload.html')

# Rota para gerar pdf

@app.route("/gerar_pdf", methods=['GET', 'POST'])
def gerar_pdf():
    try:
        # Estabelece conexão com o banco de dados
        conn = connection_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        clientes = cursor.fetchall()
        cursor.close()
        conn.close()

        # Cria o buffer de memória para o PDF
        pdf_buffer = BytesIO()

        # Cria o documento PDF
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para o título
        title_style = styles['Title']
        title = Paragraph('Relatório de Clientes', title_style)
        elements.append(title)
        elements.append(Paragraph('<br/><br/>', styles['Normal']))  # Espaço entre título e tabela

        # Prepara os dados para a tabela
        headers = ['ID', 'Nome', 'Sobrenome', 'CPF', 'Data de Nascimento', 'Cidade', 'País']
        data = [headers] + list(clientes)

        # Cria a tabela
        table = Table(data)

        # Estilo da tabela
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ])
        table.setStyle(table_style)

        # Adiciona a tabela aos elementos
        elements.append(table)

        # Constrói o PDF
        doc.build(elements)

        # Prepara a resposta
        pdf_buffer.seek(0)
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=relatorio_clientes.pdf'

        return response

    except Exception as e:
        # Tratamento de erro
        print(f"Erro ao gerar PDF: {e}")
        return f"Erro ao gerar PDF: {e}", 500


# Rota para a página de login

if __name__ == "__main__":
    app.run(debug=True, port=8085, host='127.0.0.1')
