function agregarPercepcion() {
    let div = document.createElement("div");
    div.innerHTML = '<input type="text" name="percepcion_concepto[]" placeholder="Concepto" required> ' +
                    '<input type="number" step="0.01" name="percepcion_monto[]" placeholder="Monto" required><br>';
    document.getElementById("percepciones").appendChild(div);
}
function agregarDeduccion() {
    let div = document.createElement("div");
    div.innerHTML = '<input type="text" name="deduccion_concepto[]" placeholder="Concepto" required> ' +
                    '<input type="number" step="0.01" name="deduccion_monto[]" placeholder="Monto" required><br>';
    document.getElementById("deducciones").appendChild(div);
}

function cargarPercepcionesYDeducciones() {
    let empleadoSelect = document.getElementById("empleado");
    let salarioBase = parseFloat(empleadoSelect.options[empleadoSelect.selectedIndex].getAttribute("data-salario")) || 0;
    
    document.getElementById("salario_base").value = salarioBase.toFixed(2);
    document.getElementById("puntualidad").value = (salarioBase * 0.05).toFixed(2);
    document.getElementById("asistencia").value = (salarioBase * 0.03).toFixed(2);
    document.getElementById("imss").value = (salarioBase * 0.085).toFixed(2);
    document.getElementById("isr").value = (salarioBase * 0.10).toFixed(2);
    document.getElementById("cuota_sindical").value = (salarioBase * 0.03).toFixed(2);
    document.getElementById("fondo_retiro").value = (salarioBase * 0.03).toFixed(2);
    document.getElementById("infonavit").value = (salarioBase * 0.30).toFixed(2);
    document.getElementById("caja_ahorro").value = (salarioBase * 0.06).toFixed(2);
}

