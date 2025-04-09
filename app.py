from flask import Flask, jsonify, redirect, render_template, request, url_for
from backend.conexionBD import obtener_conexion
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def index():
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
    
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/agregar_incapacidad', methods=['GET', 'POST'])
def agregar_incapacidad():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener lista de empleados
    cursor.execute("SELECT id_empleado, nombre FROM empleados")
    empleados = cursor.fetchall()

    if request.method == 'POST':
        id_empleado = request.form['id_empleado']
        fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d')
        fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d')
        tipo = request.form['tipo']
        dias_incapacidad = (fecha_fin - fecha_inicio).days + 1
        imagen_filename = None  # Por si no se sube imagen

        # Manejo de la imagen
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(imagen_path)
                imagen_filename = f"uploads/{filename}"  # Guardar ruta relativa

        # Insertar datos en la base de datos
        cursor.execute("""
            INSERT INTO incapacidades (id_empleado, fecha_inicio, fecha_fin, dias_incapacidad, tipo, imagen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_empleado, fecha_inicio, fecha_fin, dias_incapacidad, tipo, imagen_filename))

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for('index'))

    cursor.close()
    conexion.close()
    return render_template('agregar_incapacidad.html', empleados=empleados)

@app.route('/nominas')
def nominas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_empleado,salario_base, nombre, apellido FROM empleados")
    empleados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("generaNomina.html", empleados=empleados)

@app.route("/nominas_por_quincena/<int:quincena>")
def nominas_por_quincena(quincena):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM nominas WHERE quincena = %s", (quincena,))
    nominas = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return render_template("nominas.html", nominas=nominas)

@app.route("/generar_nomina", methods=["POST"])
def generar_nomina():
    from datetime import datetime

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Obtener datos del formulario
        id_empleado = request.form['empleado']
        periodo_inicio = datetime.strptime(request.form['periodo_inicio'], '%Y-%m-%d').date()
        periodo_fin = datetime.strptime(request.form['periodo_fin'], '%Y-%m-%d').date()
        salario_base = float(request.form['salario_base'])

        # Validación de datos
        if salario_base <= 0:
            return "El salario base debe ser un número positivo.", 400

        # Consultar incapacidades dentro del período
        cursor.execute("""
            SELECT tipo, fecha_inicio, fecha_fin, dias_incapacidad
            FROM incapacidades
            WHERE id_empleado = %s AND fecha_inicio <= %s AND fecha_fin >= %s
        """, (id_empleado, periodo_fin, periodo_inicio))

        incapacidades = cursor.fetchall()

        dias_incapacidad_total = 0
        for tipo, fecha_inicio, fecha_fin, _ in incapacidades:
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            inicio_incapacidad = max(fecha_inicio, periodo_inicio)
            fin_incapacidad = min(fecha_fin, periodo_fin)

            if inicio_incapacidad <= fin_incapacidad:
                dias_incapacidad_total += (fin_incapacidad - inicio_incapacidad).days + 1

        # Calcular días del período y sueldo diario
        dias_periodo = (periodo_fin - periodo_inicio).days + 1
        dias_trabajados = dias_periodo - dias_incapacidad_total
        sueldo_diario = salario_base / dias_periodo
        salario_base_real = sueldo_diario * dias_trabajados  # Sueldo base después de restar los días de incapacidad

        # Calcular percepciones
        puntualidad = 0.05 * salario_base_real
        asistencia = 0.03 * salario_base_real

        # Calcular deducciones
        imss = 0.085 * salario_base_real
        isr = 0.10 * salario_base_real
        cuota_sindical = 0.03 * salario_base_real
        fondo_retiro = 0.03 * salario_base_real
        infonavit = 0.30 * salario_base_real
        caja_ahorro = 0.06 * salario_base_real

        # Calcular totales
        total_percepciones = salario_base_real + puntualidad + asistencia
        total_deducciones = imss + isr + cuota_sindical + fondo_retiro + infonavit + caja_ahorro
        total_neto = total_percepciones - total_deducciones

        # Insertar en la tabla 'nominas'
        sql_nomina = """INSERT INTO nominas 
            (id_empleado, fecha_emision, periodo_inicio, periodo_fin, total_percepciones, total_deducciones, total_neto) 
            VALUES (%s, NOW(), %s, %s, %s, %s, %s)"""
        cursor.execute(sql_nomina, (id_empleado, periodo_inicio, periodo_fin, total_percepciones, total_deducciones, total_neto))
        conexion.commit()

        id_nomina = cursor.lastrowid

        # Percepciones
        percepciones = [
            ("Sueldo Base", salario_base_real),
            ("Puntualidad", puntualidad),
            ("Asistencia", asistencia)
        ]
        cursor.executemany("INSERT INTO percepciones (id_nomina, concepto, monto) VALUES (%s, %s, %s)", [(id_nomina, c, m) for c, m in percepciones])

        # Deducciones
        deducciones = [
            ("ISR", isr),
            ("IMSS", imss),
            ("Cuota Sindical", cuota_sindical),
            ("Fondo Retiro", fondo_retiro),
            ("INFONAVIT", infonavit),
            ("Caja de Ahorro", caja_ahorro)
        ]
        cursor.executemany("INSERT INTO deducciones (id_nomina, concepto, monto) VALUES (%s, %s, %s)", [(id_nomina, c, m) for c, m in deducciones])

        # Confirmar cambios en la base de datos
        conexion.commit()

    except Exception as e:
        # Manejo de errores
        print(f"Error al generar nómina: {e}")
        return "Ocurrió un error al generar la nómina.", 500

    finally:
        # Cerrar cursor y conexión
        cursor.close()
        conexion.close()

    return redirect(url_for('nominas'))



@app.route('/consultar_nominas', methods=['GET'])
def consultar_nominas():
    quincena = request.args.get('quincena')  # Obtener el parámetro 'quincena' de la URL
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if quincena == '1':  # Primera Quincena (del 1 al 15)
        cursor.execute("""
            SELECT n.id_nomina, e.nombre, e.apellido, n.fecha_emision, 
                   n.periodo_inicio, n.periodo_fin, n.total_percepciones, 
                   n.total_deducciones, n.total_neto
            FROM nominas n
            JOIN empleados e ON n.id_empleado = e.id_empleado
            WHERE DAY(n.periodo_inicio) <= 15
            ORDER BY n.fecha_emision DESC
        """)
    elif quincena == '2':  # Segunda Quincena (del 16 al último día del mes)
        cursor.execute("""
            SELECT n.id_nomina, e.nombre, e.apellido, n.fecha_emision, 
                   n.periodo_inicio, n.periodo_fin, n.total_percepciones, 
                   n.total_deducciones, n.total_neto
            FROM nominas n
            JOIN empleados e ON n.id_empleado = e.id_empleado
            WHERE DAY(n.periodo_inicio) > 15
            ORDER BY n.fecha_emision DESC
        """)
    else:
        # Si no se especifica ninguna quincena, mostramos todas las nóminas
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
    conexion.close()

    return render_template('consultar_nominas.html', nominas=nominas)



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
        return jsonify(nomina)  
    else:
        return jsonify({'error': 'No se encontró la nómina'}), 404


def filas_a_diccionario(cursor, filas):
    columnas = [col[0] for col in cursor.description]
    return [dict(zip(columnas, fila)) for fila in filas]

def obtener_detalle_nomina(id_nomina):
    # Obtener los detalles generales de la nómina
    nomina = obtener_nomina_por_id(id_nomina)
    
    if nomina:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Obtener datos del empleado
        query_empleado = """
            SELECT nombre, apellido, puesto 
            FROM empleados 
            WHERE id_empleado = (SELECT id_empleado FROM nominas WHERE id_nomina = %s)
        """
        cursor.execute(query_empleado, (id_nomina,))
        empleado = cursor.fetchone()

        # Obtener percepciones asociadas a esta nómina
        query_percepciones = "SELECT concepto, monto FROM percepciones WHERE id_nomina = %s"
        cursor.execute(query_percepciones, (id_nomina,))
        percepciones = filas_a_diccionario(cursor, cursor.fetchall())

        # Obtener deducciones asociadas a esta nómina
        query_deducciones = "SELECT concepto, monto FROM deducciones WHERE id_nomina = %s"
        cursor.execute(query_deducciones, (id_nomina,))
        deducciones = filas_a_diccionario(cursor, cursor.fetchall())

        # Obtener incapacidades asociadas al empleado
        query_incapacidades = """
            SELECT tipo, fecha_inicio, fecha_fin, dias_incapacidad
            FROM incapacidades
            WHERE id_empleado = (SELECT id_empleado FROM nominas WHERE id_nomina = %s)
        """
        cursor.execute(query_incapacidades, (id_nomina,))
        incapacidades = filas_a_diccionario(cursor, cursor.fetchall())

        cursor.close()

        # Agregar datos del empleado
        if empleado:
            nomina['empleado'] = {
                'nombre': empleado[0],
                'apellido': empleado[1],
                'puesto': empleado[2]
            }

        # Asignar listas de diccionarios
        nomina['percepciones'] = percepciones
        nomina['deducciones'] = deducciones
        nomina['incapacidades'] = incapacidades

        return nomina
    else:
        return None




    
app.run(debug=True)
if __name__ == '__main__':
    app.run(debug=True)
