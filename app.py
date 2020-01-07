from flask import Flask, render_template, flash, redirect, \
    url_for, session, request, logging
# Libreria que se conecta con MYSQL
from flask_mysqldb import MySQL
# Libreria que me permite encriptar password
from passlib.hash import sha256_crypt
# salto de lineas en los formularios
from functools import wraps
# importando los formularios
from formularios import *

app = Flask(__name__)
app.debug = True
# Cadena de Conexion a Mi Bd
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ventas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Inicializando MYSQL
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/productos')
def productos():
    # crear un cursor
    cur = mysql.connection.cursor()
    # Todos los productos
    # te devuelve un valor numerico result
    result = cur.execute("SELECT * FROM producto")
    # cur.fetchall() todos los registros de la tabla
    productos = cur.fetchall()
    if result > 0:
        return render_template("productos.html", prod=productos)
    else:
        msg = "Joan No te duermas carajo!!!!"
        return render_template("productos.html", msg=msg)
    cur.close()


@app.route('/producto/<string:id>/')
def producto(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM producto WHERE idprod =%s", [id])
    producto = cur.fetchone()
    return render_template("producto.html", pro=producto)
    cur.close()


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegistrarUsuario(request.form)  # Herencia POO
    if request.method == 'POST' and form.validate():
        nombre = form.nombre.data
        usuario = form.usuario.data
        correo = form.correo.data
        password = sha256_crypt.encrypt(str(form.password.data))
        obs = form.comentarios.data
        # Grabarlo en la BD
        # crear un cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios(nombre,correo,usuario,pass,observacion)values(%s,%s,%s,%s,%s)",
                    (nombre, correo, usuario, password, obs))
        mysql.connection.commit()
        cur.close()
        flash("Registro Grabado con exito")
        redirect(url_for("login"))
    return render_template("registrar.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        usuario = request.form['usuario']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM usuarios WHERE usuario = %s", [usuario])
        if result > 0:
            data = cur.fetchone()
            password = data['pass']
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = usuario
                flash('Exito ', 'success')
                return redirect(url_for('dashbaord'))
            else:
                error = 'Password incorrecto'
                return render_template('login.html', error=error)
                # close connection
            cur.close()
        else:
            error = 'Usuario no existe'
            return render_template('login.html', error=error)
    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Sin Autroizacion")
            return redirect(url_for('login'))

    return wrap


@app.route('/dashboard')
@is_logged_in
def dashbaord():
    return render_template("dashboard.html")


@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Session cerrada")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run()
