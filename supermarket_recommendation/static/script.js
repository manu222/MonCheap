document.addEventListener("DOMContentLoaded", () => {
   
     // Función para animar contenedores
     function animateContainer(container) {
        if (container) {
            container.style.opacity = "0";
            container.style.transform = "translateY(-20px)";

            setTimeout(() => {
                container.style.transition = "opacity 0.8s ease-out, transform 0.8s ease-out";
                container.style.opacity = "1";
                container.style.transform = "translateY(0)";
            }, 200);
        }
    }

    // Aplicar animación si los contenedores existen
    animateContainer(document.querySelector(".login-container"));
    animateContainer(document.querySelector(".register-container"));

    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // SVG para el estado "favorito" y "no favorito"
    let favorite = `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M16.0298 5.33C17.5998 3.88 19.6898 3 21.9998 3C26.9698 3 30.9998 7.03 30.9998 12C30.9998 20 20.9998 29 15.9998 31C10.9998 29 0.999817 20 0.999817 12C0.999817 7.03 5.02982 3 9.99982 3C12.3098 3 14.4098 3.88 15.9998 5.3L16.0298 5.33Z" fill="#ff0000"></path> <path d="M16 5.30451C14.407 3.87551 12.309 2.99951 10 2.99951C5.029 2.99951 1 7.02951 1 11.9995C1 19.9995 11 28.9995 16 30.9995C21 28.9995 31 19.9995 31 11.9995C31 7.02951 26.971 2.99951 22 2.99951C18.477 2.99951 15.479 5.05051 14 7.99951M27 11.9998C27 9.23781 24.762 6.99981 22 6.99981" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>`;

    let notfavorite = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M12 6.00019C10.2006 3.90317 7.19377 3.2551 4.93923 5.17534C2.68468 7.09558 2.36727 10.3061 4.13778 12.5772C5.60984 14.4654 10.0648 18.4479 11.5249 19.7369C11.6882 19.8811 11.7699 19.9532 11.8652 19.9815C11.9483 20.0062 12.0393 20.0062 12.1225 19.9815C12.2178 19.9532 12.2994 19.8811 12.4628 19.7369C13.9229 18.4479 18.3778 14.4654 19.8499 12.5772C21.6204 10.3061 21.3417 7.07538 19.0484 5.17534C16.7551 3.2753 13.7994 3.90317 12 6.00019Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>`

    // Agregar evento a cada botón de "corazón"
    document.querySelectorAll(".heart-btn").forEach(button => {
        button.addEventListener("click", function() {
            let productId = this.getAttribute("data-product-id");
            // Determinar si actualmente el producto está en favoritos comparando el contenido
            let isFavorited = this.innerHTML.trim() === favorite.trim();

            // Alterna el contenido inmediatamente para feedback visual
            if (isFavorited) {
                this.innerHTML = notfavorite;
                this.setAttribute("title", "Añadir a favoritos");
            } else {
                this.innerHTML = favorite;
                this.setAttribute("title", "Quitar de favoritos");
            }

            // Enviar la solicitud al backend para actualizar el estado
            fetch(`/toggle_favorite/${productId}`, { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Actualizamos el ícono según la respuesta exitosa
                        if (isFavorited) {
                            this.innerHTML = notfavorite;
                            this.setAttribute("title", "Añadir a favoritos");
                        } else {
                            this.innerHTML = favorite;
                            this.setAttribute("title", "Quitar de favoritos");
                        }
                    } else {
                        // En caso de error, podemos revertir la acción
                        console.error("Error al actualizar favorito");
                    }
                })
                .catch(error => {
                    console.error("Error en la solicitud:", error);
                });
        });
    });
});
