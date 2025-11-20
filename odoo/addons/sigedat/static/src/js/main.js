
var coordenadas;
var marker;

$( document ).ready(function() {
    console.log( "ready!" );
    console.log( "tramite_id" + tramite_id );
});

var map = L.map('map').
    setView(
        [4.63913,-74.064557],
        12
    );

L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
    maxZoom: 18
}).addTo(map);

L.control.scale().addTo(map);
map.on('click', function(e){
    marker = new L.marker(e.latlng, {draggable: true}).addTo(map);
    coordenadas = e.latlng;
    //tramite_id = $(this).attr("tramite_id")
    let formulario = `<form role="form" id="form" enctype="multipart/form-data" method="post" class="form-horizontal" action="/sigedat/visor/enviar_coordenadas">
          <input style="display: none;" type="text" id="lat" name="lat" value="${coordenadas.lat.toFixed(6)}" />
          <input style="display: none;" type="text" id="lng" name="lng" value="${coordenadas.lng.toFixed(6)}" />
          <input style="display: none;" type="text" id="tramite_id" name="tramite_id" value="${tramite_id}" />
          <div class="form-group">
            <button type="submit" value="submit" class="btn btn-primary trigger-submit">Seleccionar</button>
            <button onclick="cancelar()" type="button" class="btn btn-danger">Cancel</button>
          </div>
        </form>`;

    marker.bindPopup(formulario).openPopup();
    $("#form").submit(function(event){
      console.log('Datos Cargados');
    });
});


function cancelar() {
  console.log('Cancelar');
  map.removeLayer(marker);
}


function enviar() {
    var formData = {
      tramite_id: tramite_id,
      coordenadas: coordenadas,
    };


    $.post("http://localhost/sigedat/visor/enviar_coordenadas", formData, function() {
      alert( "success" );
    })
      .done(function() {
        alert( "second success" );
      })
      .fail(function() {
        alert( "error" );
      })
      .always(function() {
        alert( "finished" );
    });

}


function crear_punto(datos) {
  let coordenadas_tramite = datos.coordenadas;
  let marker_tramite = new L.marker(coordenadas_tramite, {draggable: false}).addTo(map);
  let info = `
  <table class="table">
    <tbody>
      <tr>
        <th>NÚMERO DE ACUERDO</th>
        <td>${datos.acuerdo}</td>
      </tr>
      <tr>
        <th>OBJETO</th>
        <td>${datos.objeto}</td>
      </tr>
      <tr>
        <th>NOMBRE FRENTE</th>
        <td>${datos.frente}</td>
      </tr>
      <tr>
        <th>ESTADO</th>
        <td>${datos.estado}</td>
      </tr>
    </tbody>
  </table>
  <div class="form-group">
    <button class="btn btn-primary trigger-submit" onclick=\"window.open('/web#id=${datos.id}&view_type=form&model=sigedat.tramite');\">Ver</button>
  </div>
  `;

  marker_tramite.bindPopup(info).openPopup();
}



function traer_tramite() {
    var formData = {
      acuerdo: $("#acuerdo").val(),
      objeto: $("#objeto").val(),
      frente: $("#frente").val(),
      state: $("#state").val(),
      coordenadas: coordenadas,
    };

    $.ajax({
      type: "POST",
      url: "http://localhost:8069/sigedat/visor/get_tramite",    // ruta controlador Odoo
      data: formData,
      dataType: "json",
      encode: true,
    }).done(function (data) {
      console.log(data);
      for(let info of data.data) {
        let datos = {
          id: info.id,
          acuerdo: info.acuerdo,
          objeto: info.objeto,
          frente: info.frente,
          state: info.state,
          coordenadas: [parseFloat(info.latitud), parseFloat(info.longitud)]
        }
        crear_punto(datos);
      }

    });

}