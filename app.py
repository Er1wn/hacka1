from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personas.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

categorias_validas_ingreso = ['salario', 'extras']
categorias_validas_egreso = [
    'vivienda', 'deudas', 'servicios', 'supermercado', 'movilidad', 'entretenimiento']


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(40), nullable=False)
    telefono = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)

    def __init__(self, nombre, telefono, password):
        self.nombre = nombre
        self.telefono = telefono
        self.password = password


class Transactions (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaccion = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)

    def __init__(self, transaccion, monto, categoria, telefono):
        self.transaccion = transaccion
        self.monto = monto
        self.categoria = categoria
        self.telefono = telefono


def calcular_saldo(telefono):

    transacciones_ingresos = db.session.query(Transactions).filter_by(
        telefono=telefono).filter_by(transaccion='ingreso')
    saldo = 0
    for transaccion in transacciones_ingresos:
        saldo = saldo + transaccion.monto

    transacciones_egresos = db.session.query(Transactions).filter_by(
        telefono=telefono).filter_by(transaccion='egreso')

    for transaccion in transacciones_egresos:
        saldo = saldo - transaccion.monto

    return saldo


@app.route('/nuevo_usuario', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        nombre = request.form['Nombre']
        telefono = request.form['Telefono']
        password = request.form['Password']
        confirma = request.form['confirmacion']
        print("nuevo usuario con estos datos",
              nombre, telefono, password, confirma)

        try:
            usuario_existente = db.session.execute(
                db.select(Users).filter_by(telefono=telefono)).one()
        except:
            usuario_existente = None

        if usuario_existente == None:
            if password == confirma:
                usuario = Users(nombre, telefono, password)
                db.session.add(usuario)
                db.session.commit()
                return redirect(url_for('home_usuario', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono)))
        else:
            print('La vendiste pa')

    return render_template('sign_up.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telefono = request.form['Telefono']
        password = request.form['Password']

        print('login con los datos', telefono, password)

        try:
            usuario = Users.query.filter_by(telefono=telefono).first()

        except:
            usuario = None

        if usuario != None:
            dict_user = usuario.__dict__
            nombre = dict_user['nombre']
            pass_correcta = dict_user['password']
            print(pass_correcta)
            if pass_correcta == password:
                print('Password correcta, Bienvenid@')
                return redirect(url_for('home_usuario', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono)))
            else:
                print('Che no sos de luque para robar cuentas')

    return render_template('login.html')


@app.route('/borrar/<int:id>')
def borrar(id):
    usuario_a_eliminar = Users.query.get(id)
    db.session.delete(usuario_a_eliminar)
    db.session.commit()
    return redirect(url_for('login', nombre='', telefono=''))


@app.route('/')
def inicio():
    return render_template('inicio.html')


@app.route('/home_usuario')
def home_usuario():
    args = request.args
    try:
        nombre = args['nombre']
        telefono = args['telefono']
    except:
        print('no iniciaste sesion')
        nombre = None
        telefono = None
        return redirect(url_for('login'))
    print('argumentos de la pagina son', nombre, telefono)
    return render_template('home_usuario.html', nombre=nombre, telefono=telefono, saldo=calcular_saldo(telefono))


@app.route('/ingresar_datos', methods=['GET', 'POST'])
def ingresar_datos():
    if request.method == 'POST':
        # Verificamos los argumentos recibidos de la pagina de sign_up o login
        args = request.args
        try:
            nombre = args['nombre']
            telefono = args['telefono']
        except:
            # Si intenta ingresar a la pagina principal sin iniciar sesion, le redireccionamos
            print('No iniciaste sesion, master. ')
            return redirect(url_for('login'))

        # Validamos que los datos de ingreso y egreso se procesen solo si ya se inicio sesion
        opcion = request.form['opcion']
        monto = request.form['monto']
        categoria = request.form['categoria']
        telefono = request.form['telefono']

        print('Se recibio la transaccion de',
              opcion, monto, categoria, telefono)

        # Realizamos las operaciones necesarias segun sea ingreso o egreso
        if (opcion == 'ingreso') and (categoria in categorias_validas_ingreso):
            transaccion = Transactions(opcion, monto, categoria, telefono)
            db.session.add(transaccion)
            db.session.commit()
        elif (opcion == 'egreso') and (categoria in categorias_validas_egreso):
            transaccion = Transactions(opcion, monto, categoria, telefono)
            db.session.add(transaccion)
            db.session.commit()
        else:
            print('La transaccion no corresponde con la categoria. ')

    return render_template('ingresar_datos.html')


if __name__ == '__main__':
    db.create_all()
app.run(debug=True)
