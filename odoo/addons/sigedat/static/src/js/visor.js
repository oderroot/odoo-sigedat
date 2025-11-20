
function traer_puntos(){
  console.log('Taer puntos....');
  $.ajax({
      type: "POST",
      dataType: 'text',
      url: '/sigedat/visor/get_tramite',
  })
      .done(function( data ) {
          crear_puntos(data);
      })
      .fail( function(xhr, textStatus, errorThrown) {
          alert(xhr.responseText);
          alert(textStatus);
      });

}


traer_puntos();


var map = L.map('map').setView([4.655623, -74.103412], 12);

var tiles = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
  maxZoom: 18,
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
    'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  id: 'mapbox/streets-v11',
  tileSize: 512,
  zoomOffset: -1
}).addTo(map);

var marker = L.marker();


function crear_puntos(datos) {
  datos_puntos = JSON.parse(datos)['data']
  for (var punto of datos_puntos) {
    let lat = punto.latitud;
    let lng = punto.longitud;
    let marker_tramite = new L.marker([lat, lng], {draggable: false}).addTo(map);
    let info = `
    <table class="table">
      <tbody>
        <tr>
          <th>NÚMERO DE ACUERDO</th>
          <td>${punto.acuerdo}</td>
        </tr>
        <tr>
          <th>OBJETO</th>
          <td>${punto.objeto}</td>
        </tr>
        <tr>
          <th>NOMBRE FRENTE</th>
          <td>${punto.frente}</td>
        </tr>
        <tr>
          <th>ESTADO</th>
          <td>${punto.state}</td>
        </tr>
      </tbody>
    </table>
    <div class="form-group">
      <button class="btn btn-primary trigger-submit" onclick=\"window.open('/web#id=${punto.id}&view_type=form&model=sigedat.tramite');\">Ver</button>
    </div>
    `;

    marker_tramite.bindPopup(info).openPopup();
  }
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
