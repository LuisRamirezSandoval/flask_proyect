from MySQLdb import STRING
from flask import Flask, render_template, request, flash, jsonify
from flask_mysqldb import MySQL
import functools, operator


aplicacion = Flask(__name__)

aplicacion.config['MYSQL_HOST']= 'localhost'
aplicacion.config['MYSQL_USER']= 'root'
aplicacion.config['MYSQL_PASSWORD']= ''
aplicacion.config['MYSQL_DB']= 'registro_citas'

mysql = MySQL(aplicacion)

aplicacion.secret_key = 'mysecretkey'

@aplicacion.route('/')
def principal():
    return render_template('index.html')

class servicio:

    @aplicacion.route('/servicios')
    def servicios():
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM servicio')
        datos = cur.fetchall()
        return render_template('servicios.html', servicio = datos)

class Usuario:
    @aplicacion.route('/registrar')
    def registrar():

        return render_template('registrar.html')
        
    @aplicacion.route('/add_registrar', methods=['POST'])
    def add_registrar():
        if request.method == 'POST':
            Nombre = request.form['name']
            Apellido_Paterno = request.form['apellido_paterno']
            Apellido_Materno = request.form['apellido_materno']
            Fecha_Nacimiento = request.form['date']
            Correo = request.form['email']
            Telefono = request.form['tel']
            Servicio = request.form['servicio']
            Fecha = request.form['fecha']
            Hora = request.form['hora']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO usuario (Nombre, Apellido_Paterno,Apellido_Materno, Fecha_Nacimiento,Correo, Telefono) VALUES (%s, %s, %s, %s, %s, %s)',
            (Nombre,Apellido_Paterno,Apellido_Materno, Fecha_Nacimiento,Correo, Telefono))
            servicio_selec = cur.execute("SELECT ID_Servicio FROM servicio WHERE Nombre = '%s'" % Servicio)
            ser = cur.fetchall()
            ser = int(ser[0][0])
            cur.execute("SELECT id_usuario FROM usuario WHERE Correo = '%s'" % Correo)
            id_usu = cur.fetchall()
            id_usu = int(id_usu[0][0])
            cur.execute('INSERT INTO cita (Fecha, Hora, id_usuario, ID_Servicio) VALUES (%s, %s, %s, %s)', (Fecha,Hora,id_usu,ser))
            flash('')
            mysql.connection.commit()
        return render_template('registrar.html')

    @aplicacion.route('/consultar')
    def consulta():
        return render_template('consultar.html')

    @aplicacion.route('/add_consulta', methods=['POST'])
    def add_consulta():
        if request.method=='POST':
            correo = request.form['email']
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM usuario WHERE Correo = '%s'" % correo)
            id_usuario = cur.fetchall()
            id_usuario = int(id_usuario[0][0])
            cur.execute("SELECT Fecha,Hora FROM cita WHERE id_usuario = '%s'" % id_usuario)
            datos = cur.fetchall()
            print(id_usuario)
            print(datos)
            flash('')
            mysql.connection.commit()
        return render_template('consultar.html', consulta = datos)

    @aplicacion.route('/reagendar')
    def reagendar():
        return render_template('reagendar.html')

    @aplicacion.route('/add_reagendar', methods=['POST'])
    def add_reagendar():
        if request.method=='POST':
            correo = request.form['email']
            Fecha = request.form['fecha']
            Hora = request.form['hora']
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM usuario WHERE Correo = '%s'" % correo)
            id_usuario = cur.fetchall()
            id_usuario = int(id_usuario[0][0])
            cur.execute("UPDATE cita SET Fecha = '%s' WHERE id_usuario = '%s'" % (Fecha, id_usuario))
            cur.execute("UPDATE cita SET Hora = '%s' WHERE id_usuario = '%s'" % (Hora, id_usuario))
            flash('')
            mysql.connection.commit()
        return render_template('reagendar.html')

@aplicacion.route('/sesion')
def sesion():
    return render_template('sesion.html')

class Admin:
    @aplicacion.route('/login_admi', methods=['POST'])
    def login():
        if request.method == 'POST':
            correo = request.form['email']
            passw = int(request.form['pass'])
            cur = mysql.connection.cursor()
            cur.execute("SELECT Usuario FROM administrador WHERE Usuario = '%s'" % correo)
            email = cur.fetchall()
            try:
                email_tupla = convertTuple(email)
                email_final = convertString(email_tupla)
            except:
                print('No se pudo acceder')

            cur.execute("SELECT Contrasena FROM administrador WHERE Contrasena = '%s'" % passw)
            contra = cur.fetchall()
            try:
                contra = int(contra[0][0])
            except:
                print('Contraseña Incorrecta')
            
            try:
                if(correo == email_final):
                    print('hola mundo')
                    if(passw == contra):
                        print('HOLAMUNDO')
                        return render_template('admi_index.html')
                        
                    else: 
                        print('x')
                        flash('')
                        return render_template('sesion.html')
                        
                else :
                    print('y')
                    flash('')
                    return render_template('sesion.html')
            except:
                print('z')
                flash('')
                return render_template('sesion.html')

    @aplicacion.route('/admi_servicio', methods=['POST'])
    def add_servicio():
        return render_template('add_servicio.html')
    
    @aplicacion.route('/add_servicio', methods=['POST'])
    def add_newServicio():
        if request.method == 'POST':
            nombre_servicio = request.form['servicio']
            descripcion = request.form['descrip']
            id_admi = int(request.form['id'])
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO servicio (Nombre, Descripcion, ID_Administrador) VALUES (%s, %s, %s)',
            (nombre_servicio,descripcion,id_admi))
            flash('')
            mysql.connection.commit()
        return render_template('add_servicio.html')
    
    @aplicacion.route('/admi_eliminar', methods=["POST"])
    def delete_servicio():
        return render_template('delete_servicio.html')

    @aplicacion.route('/delete_servicio', methods=['POST'])
    def delete_newServicio():
        if request.method == 'POST':
            id_servicio = int(request.form['id_servicio'])
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM servicio WHERE ID_Servicio = '%s'" % id_servicio)
            flash('')
            mysql.connection.commit()
        return render_template('delete_servicio.html')

    @aplicacion.route('/admi_agendar', methods=["POST"])
    def agendar_servicio():
        return render_template('agendar_servicio.html')

    @aplicacion.route('/agendar_servicio', methods=["POST"])
    def agendar_newServicio():
        if request.method == 'POST':
            Nombre = request.form['name']
            Apellido_Paterno = request.form['apellido_paterno']
            Apellido_Materno = request.form['apellido_materno']
            Fecha_Nacimiento = request.form['date']
            Correo = request.form['email']
            Telefono = request.form['tel']
            Servicio = request.form['servicio']
            Fecha = request.form['fecha']
            Hora = request.form['hora']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO usuario (Nombre, Apellido_Paterno,Apellido_Materno, Fecha_Nacimiento,Correo, Telefono) VALUES (%s, %s, %s, %s, %s, %s)',
            (Nombre,Apellido_Paterno,Apellido_Materno, Fecha_Nacimiento,Correo, Telefono))
            cur.execute("SELECT ID_Servicio FROM servicio WHERE Nombre = '%s'" % Servicio)
            ser = cur.fetchall()
            ser = int(ser[0][0])
            cur.execute("SELECT id_usuario FROM usuario WHERE Correo = '%s'" % Correo)
            id_usu = cur.fetchall()
            id_usu = int(id_usu[0][0])
            cur.execute('INSERT INTO cita (Fecha, Hora, id_usuario, ID_Servicio) VALUES (%s, %s, %s, %s)', (Fecha,Hora,id_usu,ser))
            flash('')
            mysql.connection.commit()
        return render_template('agendar_servicio.html')

    @aplicacion.route('/admi_consulta', methods=['POST'])
    def admi_consulta():
        return render_template('admi_consulta.html')

    @aplicacion.route('/add_newconsulta', methods=['POST'])
    def admi_newConsulta():
        if request.method=='POST':
            correo = request.form['email']
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM usuario WHERE Correo = '%s'" % correo)
            id_usuario = cur.fetchall()
            id_usuario = int(id_usuario[0][0])
            cur.execute("SELECT Fecha,Hora FROM cita WHERE id_usuario = '%s'" % id_usuario)
            datos = cur.fetchall()
            flash('')
            mysql.connection.commit()
        return render_template('admi_consulta.html', consulta = datos)


def convertTuple(tup):
    tup = functools.reduce(operator.add, (tup))
    return tup

def convertString(tup):
    str = functools.reduce(operator.add, (tup))
    return str

if __name__ == "__main__":
    aplicacion.run(debug=True)