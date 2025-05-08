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

    // Implementar búsqueda en tiempo real usando el sistema de tokens de funcionesMoncheap.py y df_tokens.py
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const productContainer = document.getElementById('productContainer');
    const mostLiked = document.getElementById('masGustados');
    const mostViewed = document.getElementById('masVisitados');
    let searchTimeout;

    if (searchInput) {
        // Eliminar el evento de clic del botón de búsqueda ya que haremos búsqueda en tiempo real
        if (searchButton) {
            searchButton.style.display = 'none'; // Ocultar el botón de búsqueda ya que no es necesario
        }
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.trim();
            
            // Limpiar el timeout anterior
            clearTimeout(searchTimeout);
            
            // Esperar 300ms después de que el usuario deje de escribir
            searchTimeout = setTimeout(() => {
                if (searchTerm === '') {
                    // Si la búsqueda está vacía, cargar todos los productos desde el backend
                    
                    // Mostrar las secciones de productos más gustados y visitados
                    mostViewed.style.display = "block";
                    mostLiked.style.display = "block";
                    
                    // Mostrar indicador de carga
                    productContainer.innerHTML = '<div class="text-center w-100"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
                    
                    // Llamar al endpoint para obtener todos los productos
                    fetch('/get_all_products')
                        .then(response => response.json())
                        .then(products => {
                            if (products.length === 0) {
                                productContainer.innerHTML = '<div class="text-center w-100"><p>No hay productos disponibles.</p></div>';
                                return;
                            }
                            
                            // Crear HTML para todos los productos
                            let productsHTML = '';
                            products.forEach(product => {
                                // Determinar si el producto está en favoritos
                                const isFavorite = window.favoritos && window.favoritos.includes(product.id_producto);
                                const heartSvg = isFavorite ? favorite : notfavorite;
                                const heartTitle = isFavorite ? 'Quitar de favoritos' : 'Añadir a favoritos';
                                
                                // Formatear el precio si existe
                                let precioHTML = '';
                                if (product.precio !== undefined && product.precio !== null) {
                                    precioHTML = `<p class="card-text fw-bold">€${parseFloat(product.precio).toFixed(2)}</p>`;
                                } else {
                                    precioHTML = `<p class="card-text fw-bold text-muted">Precio no disponible</p>`;
                                }
                                
                                productsHTML += `
                                <div class="col-md-4 col-lg-3 mb-4">
                                    <div class="card shadow-lg product-card">
                                        <div class="image-container">
                                            <a href="/producto/${product.id_producto}" class="text-decoration-none text-dark">
                                                <img src="${product.img}" class="card-img-top product-img" alt="${product.nombre}">
                                            </a>
                                            <button class="heart-btn" data-product-id="${product.id_producto}" data-bs-toggle="tooltip" data-bs-placement="top" title="${heartTitle}">
                                                ${heartSvg}
                                            </button>
                                        </div>
                                        <div class="card-body text-center">
                                            <a href="/producto/${product.id_producto}" class="text-decoration-none text-dark">
                                                <h5 class="card-title">${product.nombre}</h5>
                                                <p class="card-text text-muted">${product.categoria || ''}</p>
                                                ${precioHTML}
                                            </a>
                                        </div>
                                    </div>
                                </div>`;
                            });
                            
                            // Actualizar el contenedor de productos
                            productContainer.innerHTML = productsHTML;
                            
                            // Reinicializar los tooltips para los nuevos botones
                            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                            var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
                                return new bootstrap.Tooltip(tooltipTriggerEl);
                            });
                            
                            // Agregar eventos a los nuevos botones de corazón
                            document.querySelectorAll(".heart-btn").forEach(button => {
                                button.addEventListener("click", function() {
                                    let productId = this.getAttribute("data-product-id");
                                    let isFavorited = this.innerHTML.trim() === favorite.trim();
                                    
                                    if (isFavorited) {
                                        this.innerHTML = notfavorite;
                                        this.setAttribute("title", "Añadir a favoritos");
                                    } else {
                                        this.innerHTML = favorite; 
                                        this.setAttribute("title", "Quitar de favoritos");
                                    }
                                    
                                    fetch(`/toggle_favorite/${productId}`, { method: "POST" })
                                        .then(response => response.json())
                                        .catch(error => {
                                            console.error("Error en la solicitud:", error);
                                        });
                                });
                            });
                        })
                        .catch(error => {
                            console.error('Error al cargar todos los productos:', error);
                            productContainer.innerHTML = '<div class="text-center w-100"><p>Error al cargar los productos. Inténtalo de nuevo.</p></div>';
                        });
                    
                    return;
                }

                // Ocultar las secciones de productos más gustados y visitados durante la búsqueda
                mostViewed.style.display = "none";
                mostLiked.style.display = "none";

                // Mostrar indicador de carga
                productContainer.innerHTML = '<div class="text-center w-100"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';

                // Realizar la búsqueda usando el endpoint que utiliza funcionesMoncheap.py y df_tokens.py
                fetch(`/search?q=${encodeURIComponent(searchTerm)}`)
                    .then(response => response.json())
                    .then(products => {
                        if (products.length === 0) {
                            // Si no hay resultados, mostrar mensaje
                            productContainer.innerHTML = '<div class="text-center w-100"><p>No se encontraron productos que coincidan con tu búsqueda.</p></div>';
                            return;
                        }

                        // Crear HTML para los productos encontrados
                        let productsHTML = '';
                        products.forEach(product => {
                            // Determinar si el producto está en favoritos
                            const isFavorite = window.favoritos && window.favoritos.includes(product.id_producto);
                            const heartSvg = isFavorite ? favorite : notfavorite;
                            const heartTitle = isFavorite ? 'Quitar de favoritos' : 'Añadir a favoritos';
                            
                            // Formatear el precio si existe
                            let precioHTML = '';
                            if (product.precio !== undefined && product.precio !== null) {
                                precioHTML = `<p class="card-text fw-bold">€${parseFloat(product.precio).toFixed(2)}</p>`;
                            } else {
                                precioHTML = `<p class="card-text fw-bold text-muted">Precio no disponible</p>`;
                            }

                            productsHTML += `
                            <div class="col-md-4 col-lg-3 mb-4">
                                <div class="card shadow-lg product-card">
                                    <div class="image-container">
                                        <a href="/producto/${product.id_producto}" class="text-decoration-none text-dark">
                                            <img src="${product.img}" class="card-img-top product-img" alt="${product.nombre}">
                                        </a>
                                        <button class="heart-btn" data-product-id="${product.id_producto}" data-bs-toggle="tooltip" data-bs-placement="top" title="${heartTitle}">
                                            ${heartSvg}
                                        </button>
                                    </div>
                                    <div class="card-body text-center">
                                        <a href="/producto/${product.id_producto}" class="text-decoration-none text-dark">
                                            <h5 class="card-title">${product.nombre}</h5>
                                            <p class="card-text text-muted">${product.categoria || ''}</p>
                                            ${precioHTML}
                                        </a>
                                    </div>
                                </div>
                            </div>`;
                        });

                        // Actualizar el contenedor de productos
                        productContainer.innerHTML = productsHTML;

                        // Reinicializar los tooltips para los nuevos botones
                        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                        var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
                            return new bootstrap.Tooltip(tooltipTriggerEl);
                        });

                        // Agregar eventos a los nuevos botones de corazón
                        document.querySelectorAll(".heart-btn").forEach(button => {
                            button.addEventListener("click", function() {
                                let productId = this.getAttribute("data-product-id");
                                let isFavorited = this.innerHTML.trim() === favorite.trim();

                                if (isFavorited) {
                                    this.innerHTML = notfavorite;
                                    this.setAttribute("title", "Añadir a favoritos");
                                } else {
                                    this.innerHTML = favorite;
                                    this.setAttribute("title", "Quitar de favoritos");
                                }

                                fetch(`/toggle_favorite/${productId}`, { method: "POST" })
                                    .then(response => response.json())
                                    .catch(error => {
                                        console.error("Error en la solicitud:", error);
                                    });
                            });
                        });
                    })
                    .catch(error => {
                        console.error('Error en la búsqueda:', error);
                        productContainer.innerHTML = '<div class="text-center w-100"><p>Error al realizar la búsqueda. Inténtalo de nuevo.</p></div>';
                    });
            }, 300);
        });
    }
});


  
