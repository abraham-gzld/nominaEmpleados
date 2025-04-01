from flask import Flask, redirect, render_template, request, url_for
from backend.conexionBD import obtener_conexion
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/empleados')
def empleados():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute('select * from empleados')
    empleados = cursor.fetchall()


    return render_template('empleados.html', empleados = empleados)

@app.route('/agregar_empleado', methods=['POST'])
def agregar_empleado():
    # Obtener los datos del formulario
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    curp = request.form['curp']
    rfc = request.form['rfc']
    nss = request.form['nss']
    puesto = request.form['puesto']
    departamento = request.form['departamento']
    salario_base = request.form['salario_base']

    # Insertar los datos en la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO empleados (nombre, apellido, curp, rfc, nss, puesto, departamento, salario_base)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (nombre, apellido, curp, rfc, nss, puesto, departamento, salario_base))

    conexion.commit()  # Guardar cambios
    return redirect('/empleados')  # Redirigir a la página de empleados

@app.route('/editar_empleado', methods=['POST'])
def editar_empleado():
    if request.method == 'POST':
        # Obtener los datos del formulario
        id_empleado = request.form['id_empleado']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        curp = request.form['curp']
        rfc = request.form['rfc']
        nss = request.form['nss']
        puesto = request.form['puesto']
        departamento = request.form['departamento']
        salario_base = request.form['salario_base']

        # Conectar a la base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Consulta SQL para actualizar la información del empleado
        cursor.execute("""
            UPDATE empleados
            SET nombre = %s, apellido = %s, curp = %s, rfc = %s, nss = %s, puesto = %s, departamento = %s, salario_base = %s
            WHERE id_empleado = %s
        """, (nombre, apellido, curp, rfc, nss, puesto, departamento, salario_base, id_empleado))

        # Guardar los cambios
        conexion.commit()

        # Cerrar la conexión
        cursor.close()
        conexion.close()

        # Redirigir de vuelta a la página de empleados
        return redirect(url_for('empleados'))

@app.route('/nominas')
def nominas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_empleado,salario_base, nombre, apellido FROM empleados")
    empleados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("generaNomina.html", empleados=empleados)


@app.route('/consultar_nominas')
def consultar_nominas():
    return "Consultar Nóminas"

@app.route('/configuracion')
def configuracion():
    return "Configuración"

if __name__ == '__main__':
    app.run(debug=True)
