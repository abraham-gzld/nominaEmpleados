// Cargar los datos del empleado al modal de edición cuando se hace clic en "Editar"
$('#editEmployeeModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Botón que activó el modal
    var id = button.data('id');
    var nombre = button.data('nombre');
    var apellido = button.data('apellido');
    var curp = button.data('curp');
    var rfc = button.data('rfc');
    var nss = button.data('nss');
    var puesto = button.data('puesto');
    var departamento = button.data('departamento');
    var salario = button.data('salario');

    var modal = $(this);
    modal.find('#edit_id_empleado').val(id);
    modal.find('#edit_nombre').val(nombre);
    modal.find('#edit_apellido').val(apellido);
    modal.find('#edit_curp').val(curp);
    modal.find('#edit_rfc').val(rfc);
    modal.find('#edit_nss').val(nss);
    modal.find('#edit_puesto').val(puesto);
    modal.find('#edit_departamento').val(departamento);
    modal.find('#edit_salario_base').val(salario);
  });