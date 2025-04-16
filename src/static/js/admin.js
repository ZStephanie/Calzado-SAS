const sideMenu = document.querySelector('aside');
const menuBtn = document.querySelector('#menu_bar');
const closeBtn = document.querySelector('#close_btn');
const themeToggler = document.querySelector('.theme-toggler');
const themeImage = document.getElementById('themeImage')

menuBtn.addEventListener('click', ()=>{
    sideMenu.style.display ="block"
})
closeBtn.addEventListener('click', ()=>{
    sideMenu.style.display ="none"
})

themeToggler.addEventListener('click', () => {
    const isDark = document.body.classList.toggle('dark-theme-variables');
    
    themeToggler.querySelector('span:nth-child(1)').classList.toggle('active', !isDark);
    themeToggler.querySelector('span:nth-child(2)').classList.toggle('active', isDark);

    if (isDark) {
        themeImage.src = '/static/img/CALZADO_SAS_BLANCO.png';
    } else {
        themeImage.src = '/static/img/CALZADO_SAS.png';
    }
});

function eliminarProductoJavaScript(id) {
    const idR = document.querySelector('#id_' + id);
    let nombre_imagen = idR.dataset.foto;
  
    let fila = document.querySelector('#Registro_' + id);
  
    var urlForm = "{{ url_for('formViewBorrarProducto') }}";
    $.ajax({
      type: "POST",
      data: { id: id, nombre_imagen: nombre_imagen },
      url: urlForm,
      success: function (resp) {
        console.log(resp);
        if (resp == 1) {
          fila.remove(); // Elimina la fila del DOM
          mensajeAlerta(msg = 'Producto eliminado con éxito.', tipo = 1);
        } else {
          console.log('Error al intentar borrar el producto');
        }
      }
    });
  }
  