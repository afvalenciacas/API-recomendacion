var sentimientoSeleccionado = null;
var generosSeleccionados = [];
var contador = 0;

function seleccionarImagen(emocion) {
  // Reiniciar todos los estilos de imágenes
  var imagenes = document.querySelectorAll('.imagen-mood');
  imagenes.forEach(function (imagen) {
    imagen.classList.remove('imagen-seleccionada');
  });

  // Resaltar la imagen seleccionada
  var imagenSeleccionada = document.getElementById(emocion);
  imagenSeleccionada.classList.add('imagen-seleccionada');

  // quitar el atributo disabled al boton
  var confirmaremocionBtn = document.getElementById('confirmaremocion');
  confirmaremocionBtn.disabled = false;

  // Almacenar el sentimiento seleccionado
  sentimientoSeleccionado = emocion;
}

function confirmarSeleccion() {
    if (sentimientoSeleccionado) {
      // Enviar el sentimiento seleccionado a la REST API
      enviarSentimientoAPI(sentimientoSeleccionado);

      window.location.href = '/genero';
    } else {
      alert('Selecciona un sentimiento antes de confirmar.');
    }
  }
  
function enviarSentimientoAPI(sentimiento) {
    // URL de la REST API donde enviar el sentimiento
    var urlAPI = 'http://127.0.0.1:5000/api/enviar-sentimiento';
  
    // Objeto de opciones para la solicitud
    var opciones = {
      method: 'POST', // Método HTTP para enviar datos
      headers: {
        'Content-Type': 'application/json', // Tipo de contenido JSON
      },
      body: JSON.stringify({ sentimiento: sentimiento }), // Convertir a JSON y enviar en el cuerpo
    };
  
    // Realizar la solicitud HTTP
    fetch(urlAPI, opciones)
      .then(function (respuesta) {
        if (!respuesta.ok) {
          throw new Error('Error en la solicitud.');
        }
        return respuesta.json();
      })
      .then(function (datos) {
        // Aquí puedes manejar la respuesta de la API si es necesario
        console.log('Respuesta de la API:', datos);
      })
      .catch(function (error) {
        console.error('Error al enviar el sentimiento:', error);
      });
}



function seleccionarGenero(genero, boton) {
    if (generosSeleccionados.includes(genero)) {
        // Si ya está seleccionado, quitarlo de la lista y restaurar el color
        generosSeleccionados = generosSeleccionados.filter(item => item !== genero);
        boton.style.backgroundColor = "";
    } else if (generosSeleccionados.length < 3) {
        // Si no está seleccionado y hay menos de tres seleccionados, agregarlo a la lista y cambiar el color
        generosSeleccionados.push(genero);
        boton.style.backgroundColor = "cornflowerblue";
    }

    // Habilitar o deshabilitar el botón "Generar Playlist" según la cantidad de elementos seleccionados
    var generarPlaylistBtn = document.getElementById('generarPlaylist');
    generarPlaylistBtn.disabled = generosSeleccionados.length !== 3;
}

function generarListaGeneros() {
    // Enviar los géneros seleccionados a la REST API
        enviarGenerosAPI(generosSeleccionados);
    window.location.href = '/playlist';
}

function enviarGenerosAPI(generos) {
    // URL de la REST API donde enviar la playlist
    var urlAPI = 'http://127.0.0.1:5000/api/enviar-generos';

    // Objeto de opciones para la solicitud
    var opciones = {
        method: 'POST', // Método HTTP para enviar datos
        headers: {
            'Content-Type': 'application/json', // Tipo de contenido JSON
        },
        body: JSON.stringify({ generos: generos }), // Convertir a JSON y enviar en el cuerpo
    };

    // Realizar la solicitud HTTP
    fetch(urlAPI, opciones)
        .then(function (respuesta) {
            if (!respuesta.ok) {
                throw new Error('Error en la solicitud.');
            }
            return respuesta.json();
        })
        .then(function (datos) {
            // Aquí puedes manejar la respuesta de la API si es necesario
            console.log('Respuesta de la API:', datos);
        })
        .catch(function (error) {
            console.error('Error al enviar la playlist:', error);
        });
}


function enviarFoto(photoId) {
    // Aquí puedes implementar la lógica para enviar la foto, por ejemplo, mediante una solicitud AJAX.
    // En este ejemplo, simplemente mostramos un mensaje en la consola.
    const photo = document.getElementById(photoId);
    console.log('Enviando foto:', photo.src);

    //Aqui se supone que se hace otra llamada al servidor para detectar emocion (pendiente)
    //LLamamos genero 
    window.location.href = '/genero';

}

function meGusta() {
  // Aquí puedes agregar la lógica que desees al hacer click en "Me Gusta"
  // Por ejemplo, mostrar el mensaje en la tercera columna.
  document.getElementById('mensajeColumna').style.display = 'block';
}

function generarPlaylist() {
  // Aquí puedes agregar la lógica que desees al hacer click en "Dame otra playlist"
  contador = parseInt(contador) + 1
  console.log(contador);
  document.getElementById('mensajeColumna').style.display = 'none';

   // URL de la REST API donde enviar la playlist
   var urlAPI = 'http://127.0.0.1:5000/api/generar-playlist';

   // Objeto de opciones para la solicitud
   var opciones = {
       method: 'POST', // Método HTTP para enviar datos
       headers: {
           'Content-Type': 'application/json', // Tipo de contenido JSON
       },
       body: JSON.stringify({ contador: contador }), // Convertir a JSON y enviar en el cuerpo
   };

   // Realizar la solicitud HTTP
   fetch(urlAPI, opciones)
       .then(function (respuesta) {
           if (!respuesta.ok) {
               throw new Error('Error en la solicitud.');
           }

           return respuesta.json();

          })
       .then(function (datos) {
           // Aquí puedes manejar la respuesta de la API si es necesario
           console.log('Respuesta de la API:', datos.playlist); 
          if (datos.playlist == "" ){
            window.location.href = '/';
          }

          var playlistContainer = document.getElementById('playlistholder');
         
          // Convertir saltos de línea en <br> para que se muestren en HTML
          var playlistHTML = datos.playlist.replace(/\n/g, '<br>');
    
          // Aplicar estilo de justificación a la izquierda al contenedor
          playlistContainer.style.textAlign = 'left'; 
          
          // Display the playlist as HTML within the container
          playlistContainer.innerHTML = playlistHTML;
           
       })
       .catch(function (error) {
           console.error('Error al enviar la playlist:', error);
       });
}
