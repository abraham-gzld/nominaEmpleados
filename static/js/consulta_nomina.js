// Función para cargar el detalle de la nómina en el modal
let datosNomina = null;

function verDetalle(idNomina) {
    $.get('/detalle_nomina/' + idNomina, function(data) {
        if (data.error) {
            alert(data.error);
            return;
        }

        // Asignar los datos de la nómina a la variable global
        datosNomina = data;

        // Llenar el modal con los datos de la nómina
        $('#empleadoNombre').text(data.empleado.nombre + ' ' + data.empleado.apellido);
        $('#empleadoPuesto').text(data.empleado.puesto); // Mostrar el puesto
        $('#fechaEmision').text(data.fecha_emision);
        $('#periodo').text(data.periodo_inicio + ' al ' + data.periodo_fin);
        $('#totalPercepciones').text(data.total_percepciones);
        $('#totalDeducciones').text(data.total_deducciones);
        $('#totalNeto').text(data.total_neto);

        // Llenar las percepciones
        let percepcionesHtml = '';
        data.percepciones.forEach(function(percepcion) {
            percepcionesHtml += `<li>${percepcion.concepto}: $${percepcion.monto}</li>`;
        });
        $('#listaPercepciones').html(percepcionesHtml);

        // Llenar las deducciones
        let deduccionesHtml = '';
        data.deducciones.forEach(function(deduccion) {
            deduccionesHtml += `<li>${deduccion.concepto}: $${deduccion.monto}</li>`;
        });
        $('#listaDeducciones').html(deduccionesHtml);

        // Llenar las incapacidades
        let incapacidadesHtml = '';
        data.incapacidades.forEach(function(incapacidad) {
            incapacidadesHtml += `<li>${incapacidad.tipo} del ${incapacidad.fecha_inicio} al ${incapacidad.fecha_fin} (${incapacidad.dias_incapacidad} días)</li>`;
        });
        $('#listaIncapacidades').html(incapacidadesHtml);

        // Mostrar el modal
        $('#detalleNominaModal').modal('show');
    });
}
function descargarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    if (!datosNomina || !datosNomina.empleado) {
        alert("No se pudieron cargar los detalles de la nómina.");
        return;
    }

    const salario_base_real = parseFloat(
        datosNomina.percepciones.find(p => p.concepto === "Sueldo Base")?.monto || 0
    );

    doc.setFontSize(20);
    doc.text("Nómina de Pago", 105, 20, null, null, 'center');
    doc.setFontSize(12);

    doc.text(`Empleado: ${datosNomina.empleado.nombre} ${datosNomina.empleado.apellido}`, 20, 40);
    doc.text(`Puesto: ${datosNomina.empleado.puesto}`, 20, 50);
    doc.text(`Fecha de Emisión: ${datosNomina.fecha_emision}`, 20, 60);
    doc.text(`Periodo: ${datosNomina.periodo_inicio} al ${datosNomina.periodo_fin}`, 20, 70);

    // Tabla de percepciones
    let y = 90;
    doc.text("Percepciones:", 20, y);
    y += 10;

    const percepcionesConPorcentaje = datosNomina.percepciones.map(p => {
        let porcentaje = '';
        if (p.concepto === "Puntualidad") porcentaje = " (5%)";
        if (p.concepto === "Asistencia") porcentaje = " (3%)";
        return [`${p.concepto}${porcentaje}`, `$${parseFloat(p.monto).toFixed(2)}`];
    });

    doc.autoTable({
        startY: y,
        head: [['Concepto', 'Monto']],
        body: percepcionesConPorcentaje,
        theme: 'grid',
        headStyles: { fillColor: [22, 160, 133] },
        styles: { fontSize: 10 },
    });

    // Tabla de deducciones
    y = doc.lastAutoTable.finalY + 10;
    doc.text("Deducciones:", 20, y);
    y += 10;

    const deduccionesConPorcentaje = datosNomina.deducciones.map(d => {
        let porcentaje = '';
        switch (d.concepto) {
            case "IMSS": porcentaje = " (8.5%)"; break;
            case "ISR": porcentaje = " (10%)"; break;
            case "Cuota Sindical": porcentaje = " (3%)"; break;
            case "Fondo Retiro": porcentaje = " (3%)"; break;
            case "INFONAVIT": porcentaje = " (30%)"; break;
            case "Caja de Ahorro": porcentaje = " (6%)"; break;
        }
        return [`${d.concepto}${porcentaje}`, `$${parseFloat(d.monto).toFixed(2)}`];
    });

    doc.autoTable({
        startY: y,
        head: [['Concepto', 'Monto']],
        body: deduccionesConPorcentaje,
        theme: 'grid',
        headStyles: { fillColor: [242, 85, 96] },
        styles: { fontSize: 10 },
    });

    // Totales
    y = doc.lastAutoTable.finalY + 10;
    doc.text(`Total Percepciones: $${datosNomina.total_percepciones}`, 20, y);
    doc.text(`Total Deducciones: $${datosNomina.total_deducciones}`, 20, y + 10);
    doc.text(`Total Neto: $${datosNomina.total_neto}`, 20, y + 20);

    doc.save('nomina.pdf');
}

function filtrarPorQuincena() {
    var quincena = document.getElementById("quincenaSelect").value; // Obtener valor del select
    var rows = document.querySelectorAll("#tablaNominas .nomina"); // Seleccionar todas las filas de la tabla

    rows.forEach(function(row) {
        var periodoInicio = row.getAttribute("data-periodo-inicio"); // Obtener la fecha de inicio del periodo
        var fechaInicio = new Date(periodoInicio); // Convertir a un objeto Date para manipularla

        var dia = fechaInicio.getDate(); // Obtener el día del mes

        // Filtrar según la quincena seleccionada
        if (quincena === "" || (quincena === "1" && dia <= 15) || (quincena === "2" && dia > 15)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

