from crypt import methods
from nis import cat
from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for
from flask_login import (current_user,LoginManager,login_user,logout_user,login_required)
import hashlib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuariovm:pimenta11@localhost:3306/meubanco'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://viniciusoliveira:pimenta11@viniciusoliveira.mysql.pythonanywhere-services.com:3306/viniciusoliveira$meubanco'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


app.secret_key = 'Mamonas44'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    end = db.Column('usu_end', db.String(256))


    def __init__(self,nome,email,senha,end):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.end = end
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anun_nome', db.String(256))
    desc = db.Column('anun_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco= db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))


    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id


class Categoria(db.Model):
    __tablename__= "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__(self, nome, desc):
        self.nome = nome
        self.desc = desc


class Compras(db.Model):
    __tablename__ = "compra"
    id = db.Column('com_id', db.Integer, primary_key=True)
    qtd = db.Column('com_qtd', db.Integer)
    preco = db.Column('com_preco', db.Integer)
    total = db.Column('com_total', db.Integer)
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))
    anu_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))

    def __init__(self, qtd, preco, total, usu_id, anu_id):
        self.qtd = qtd
        self.preco = preco
        self.total = total
        self.usu_id = usu_id
        self.anu_id = anu_id


class Favoritos (db.Model):
    __tablename__ = "favoritos"
    id = db.Column('fav_id', db.Integer, primary_key=True)
    anu_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, usu_id, anu_id):
        self.usu_id = usu_id
        self.anu_id = anu_id


class Pergunta (db.Model):
    __tablename__ = "perguntas"
    id = db.Column('per_id', db.Integer, primary_key=True)
    anu_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))
    pergunta = db.Column('per_pergunta', db.String(256))
    resposta = db.Column('per_resposta', db.String(256))

    def __init__(self, usu_id, anu_id, pergunta, resposta):
        self.usu_id = usu_id
        self.anu_id = anu_id
        self.pergunta = pergunta
        self.resposta = resposta



@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('paginanaoencontrada.html')


@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)
 

@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email = email, senha = senha).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/")

def index():
    return render_template('index.html')


@app.route("/cad/usuario")
def cadusuario():
    return render_template('user.html', usuarios = Usuario.query.all(), titulo="Usuario")


@app.route("/usuario/novo", methods=['POST'])
def caduser():
    hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get('user'), request.form.get('email'), hash , request.form.get('end') )
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('cadusuario'))


@app.route("/usuario/detalhar/<int:id>")
def buscausuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome


@app.route("/usuario/editar/<int:id>", methods = ['GET','POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('user')
        usuario.email = request.form.get('email')
        usuario.senha = hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
        usuario.end = request.form.get('end')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('cadusuario'))
    
    return render_template('editusuario.html', usuario = usuario, titulo="Usuario")



@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('cadusuario'))


@app.route("/cad/anuncio")
@login_required
def anuncio():
    return render_template('anuncio.html', anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), titulo="Anuncios")


@app.route("/anuncio/criar", methods = ['POST'])
def criaranuncio():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'), request.form.get('qtd'), request.form.get('preco'), request.form.get('cat'), request.form.get('usu'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))


@app.route("/anuncio/compra")
@login_required
def compra():
    return render_template('compra.html', compras = Compras.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo = "Compras") 


@app.route("/anuncio/criarcompra", methods = ['POST'])
def criarcompra():
    compra = Compras(request.form.get('qtd'), request.form.get('preco'), request.form.get('total'), request.form.get('usu'), request.form.get('anu'))
    db.session.add(compra)
    db.session.commit()
    return redirect(url_for('compra'))


@app.route("/anuncio/pergunta")
@login_required
def pergunta():
    return render_template('pergunta.html', titulo="Perguntas")


@app.route("/anuncio/favoritos")
@login_required
def favoritos():
    return render_template('favorito.html', titulo="Favoritos")


@app.route("/config/categoria")
@login_required
def categoria():
    return render_template('categoria.html', categorias = Categoria.query.all(), titulo="Categorias")


@app.route("/categoria/criar", methods = ['POST'])
def criarcategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))



@app.route("/relatorio/vendas")
@login_required
def rel_vendas():
    return render_template('relvendas.html', titulo="Relatórios Vendas")


@app.route("/relatorio/compras")
@login_required
def rel_compras():
    return render_template('relcompras.html', titulo="Relatórios Compras")


if __name__ == 'cf':
    db.create_all()
    #app.run()

    