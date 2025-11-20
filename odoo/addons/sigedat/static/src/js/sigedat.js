$( () => {
    //INFO Agrego los valores necesarios por el controlador a los campos hidden
    $('#usuario').val(usuario);
    $('#grupo').val(grupo);
    $('#base').val(base);

    //INFO Si es un usuario antiguo debe poder ingresar, sin que le pida mas datos
    if(es_usuario_antiguo == "1"){
        $('#formulario').hide();
        $('#tratamiento_datos').prop( "checked", true );
        $('#habeas_data').prop( "checked", true );
        $('#continuar').click();
    }

});