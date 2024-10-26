from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_secreto'  # Cambia esto por una clave secreta segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facturas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo para la base de datos
class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False)
    cliente = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.String(20), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Cargar el usuario por ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Ruta principal para ver las facturas
@app.route('/')
@login_required
def index():
    facturas = Factura.query.all()
    return render_template('index.html', facturas=facturas)

# Ruta para agregar una factura
@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    numero = request.form['numero']
    cliente = request.form['cliente']
    monto = request.form['monto']

    nueva_factura = Factura(numero=numero, cliente=cliente, monto=monto)
    db.session.add(nueva_factura)
    db.session.commit()
    return redirect(url_for('index'))

# Ruta para eliminar una factura
@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    factura = Factura.query.get_or_404(id)
    db.session.delete(factura)
    db.session.commit()
    return redirect(url_for('index'))

# Ruta para editar una factura
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    factura = Factura.query.get_or_404(id)

    if request.method == 'POST':
        factura.numero = request.form['numero']
        factura.cliente = request.form['cliente']
        factura.monto = request.form['monto']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('editar.html', factura=factura)

# Ruta para registrarse
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe. Intenta con otro.')
            return redirect(url_for('register'))

        nuevo_usuario = User(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario registrado exitosamente. Inicia sesión.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.')

    return render_template('login.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
