document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todas las imágenes de productos
    const productImages = document.querySelectorAll('.product-img');

    productImages.forEach(img => {
        // Manejar el evento de error de carga
        img.onerror = function() {
            this.classList.add('error');
        };

        // Manejar el evento de carga exitosa
        img.onload = function() {
            this.classList.remove('error');
        };

        // Si la imagen ya está cargada pero tiene un src inválido
        if (img.complete && (img.naturalWidth === 0 || !img.src || img.src.endsWith('undefined') || img.src.endsWith('null'))) {
            img.classList.add('error');
        }
    });
});

