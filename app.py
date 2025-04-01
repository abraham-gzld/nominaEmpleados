from flask import Flask, jsonify, redirect, render_template, request, url_for
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

@app.route("/generar_nomina", methods=["GET", "POST"])
def generar_nomina():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    id_empleado = request.form['empleado']
    periodo_inicio = request.form['periodo_inicio']
    periodo_fin = request.form['periodo_fin']
    
    salario_base = float(request.form['salario_base'])
    puntualidad = float(request.form['puntualidad'])
    asistencia = float(request.form['asistencia'])
    
    imss = float(request.form['imss'])
    isr = float(request.form['isr'])
    cuota_sindical = float(request.form['cuota_sindical'])
    fondo_retiro = float(request.form['fondo_retiro'])
    infonavit = float(request.form['infonavit'])
    caja_ahorro = float(request.form['caja_ahorro'])

    # Guardar nómina en la tabla 'nominas'
    total_percepciones = salario_base + puntualidad + asistencia
    total_deducciones = imss + isr + cuota_sindical + fondo_retiro + infonavit + caja_ahorro
    total_neto = total_percepciones - total_deducciones

    sql_nomina = "INSERT INTO nominas (id_empleado, fecha_emision, periodo_inicio, periodo_fin, total_percepciones, total_deducciones, total_neto) VALUES (%s, NOW(), %s, %s, %s, %s, %s)"
    cursor.execute(sql_nomina, (id_empleado, periodo_inicio, periodo_fin, total_percepciones, total_deducciones, total_neto))
    conexion.commit()
    
    id_nomina = cursor.lastrowid  # Obtener el ID de la nómina generada

    # Guardar percepciones fijas
    percepciones = [
        ("Sueldo Base", salario_base),
        ("Puntualidad", puntualidad),
        ("Asistencia", asistencia)
    ]
    for concepto, monto in percepciones:
        cursor.execute("INSERT INTO percepciones (id_nomina, concepto, monto) VALUES (%s, %s, %s)", (id_nomina, concepto, monto))

    # Guardar deducciones fijas
    deducciones = [
        ("ISR", isr),
        ("IMSS", imss),
        ("Cuota Sindical", cuota_sindical),
        ("Fondo Retiro", fondo_retiro),
        ("INFONAVIT", infonavit),
        ("Caja de Ahorro", caja_ahorro)
    ]
    for concepto, monto in deducciones:
        cursor.execute("INSERT INTO deducciones (id_nomina, concepto, monto) VALUES (%s, %s, %s)", (id_nomina, concepto, monto))

    # Guardar percepciones adicionales agregadas por el usuario
    percepciones_extra = request.form.getlist('percepcion_concepto[]')
    montos_extra = request.form.getlist('percepcion_monto[]')
    for concepto, monto in zip(percepciones_extra, montos_extra):
        cursor.execute("INSERT INTO percepciones (id_nomina, concepto, monto) VALUES (%s, %s, %s)", (id_nomina, concepto, float(monto)))

    # Guardar deducciones adicionales agregadas por el usuario
    deducciones_extra = request.form.getlist('deduccion_concepto[]')
    montos_deducciones_extra = request.form.getlist('deduccion_monto[]')
    for concepto, monto in zip(deducciones_extra, montos_deducciones_extra):
        cursor.execute("INSERT INTO deducciones (id_nomina, concepto, monto) VALUES (%s, %s, %s)", (id_nomina, concepto, float(monto)))

    conexion.commit()
    
    return redirect(url_for('nominas'))

@app.route('/consultar_nominas')
def consultar_nominas():
    conexcion = obtener_conexion()
    cursor = conexcion.cursor()
    cursor.execute("""
        SELECT n.id_nomina, e.nombre, e.apellido, n.fecha_emision, 
               n.periodo_inicio, n.periodo_fin, n.total_percepciones, 
               n.total_deducciones, n.total_neto
        FROM nominas n
        JOIN empleados e ON n.id_empleado = e.id_empleado
        ORDER BY n.fecha_emision DESC
    """)
    nominas = cursor.fetchall()
    cursor.close()

    return render_template("consultar_nominas.html", nominas=nominas)


def obtener_nomina_por_id(id_nomina):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    query = """
        SELECT n.id_nomina, e.nombre, e.apellido, n.fecha_emision, n.periodo_inicio, n.periodo_fin,
               n.total_percepciones, n.total_deducciones, n.total_neto
        FROM nominas n
        JOIN empleados e ON n.id_empleado = e.id_empleado
        WHERE n.id_nomina = %s
    """
    cursor.execute(query, (id_nomina,))
    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return {
            'id_nomina': result[0],
            'nombre': result[1],
            'apellido': result[2],
            'fecha_emision': result[3],
            'periodo_inicio': result[4],
            'periodo_fin': result[5],
            'total_percepciones': result[6],
            'total_deducciones': result[7],
            'total_neto': result[8]
        }
    return None
@app.route('/detalle_nomina/<id_nomina>')
def detalle_nomina(id_nomina):
    # Obtener los detalles de la nómina y el empleado
    nomina = obtener_detalle_nomina(id_nomina)
    if nomina:
        # Asegúrate de incluir la información del empleado
        empleado = obtener_nomina_por_id(nomina['id_nomina'])  # O lo que sea necesario
        nomina['empleado'] = {
            'nombre': empleado['nombre'],
            'apellido': empleado['apellido']
        }
        return jsonify(nomina)
    else:
        return jsonify({'error': 'No se encontró la nómina'}), 404


def obtener_detalle_nomina(id_nomina):
    # Obtener los detalles generales de la nómina
    nomina = obtener_nomina_por_id(id_nomina)
    
    if nomina:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Obtener datos del empleado
        query_empleado = "SELECT nombre, apellido, puesto FROM empleados WHERE id_empleado = (SELECT id_empleado FROM nominas WHERE id_nomina = %s)"
        cursor.execute(query_empleado, (id_nomina,))
        empleado = cursor.fetchone()  # Suponemos que este es un solo resultado

        # Obtener percepciones asociadas a esta nómina
        query_percepciones = "SELECT concepto, monto FROM percepciones WHERE id_nomina = %s"
        cursor.execute(query_percepciones, (id_nomina,))
        percepciones = cursor.fetchall()

        # Obtener deducciones asociadas a esta nómina
        query_deducciones = "SELECT concepto, monto FROM deducciones WHERE id_nomina = %s"
        cursor.execute(query_deducciones, (id_nomina,))
        deducciones = cursor.fetchall()

        # Obtener incapacidades asociadas al empleado de esta nómina
        query_incapacidades = """
            SELECT tipo, fecha_inicio, fecha_fin, dias_incapacidad
            FROM incapacidades
            WHERE id_empleado = (SELECT id_empleado FROM nominas WHERE id_nomina = %s)
        """
        cursor.execute(query_incapacidades, (id_nomina,))
        incapacidades = cursor.fetchall()

        cursor.close()

        # Añadir los datos del empleado al diccionario de la nómina
        if empleado:
            nomina['empleado'] = {
                'nombre': empleado[0],
                'apellido': empleado[1],
                'puesto': empleado[2]
            }

        # Añadir percepciones, deducciones e incapacidades al diccionario de la nómina
        nomina['percepciones'] = [{'concepto': perc[0], 'monto': perc[1]} for perc in percepciones]
        nomina['deducciones'] = [{'concepto': ded[0], 'monto': ded[1]} for ded in deducciones]
        nomina['incapacidades'] = [{'tipo': incap[0], 'fecha_inicio': incap[1], 'fecha_fin': incap[2], 'dias_incapacidad': incap[3]} for incap in incapacidades]

        return nomina
    else:
        return None

@app.route('/configuracion')
def configuracion():
    return render_template('index.html')

    
app.run(debug=True)


@app.route('/configuracion')
def configuracion():
    return "Configuración"

if __name__ == '__main__':
    app.run(debug=True)
