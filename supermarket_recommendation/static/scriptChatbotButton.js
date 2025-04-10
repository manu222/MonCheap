function crearBotonFlotante() {
    // Crear el botón
    const boton = document.createElement("button");
    boton.classList.add("fab");
    boton.style.position = "fixed";
    boton.style.bottom = "20px";
    boton.style.right = "20px";
    boton.style.width = "66px";
    boton.style.height = "66px";
    boton.style.backgroundColor = "#D29CF4";
    boton.style.borderRadius = "50%";
    boton.style.boxShadow = "2px 5px 10px rgba(0, 0, 0, 0.3)";
    boton.style.display = "flex";
    boton.style.alignItems = "center";
    boton.style.justifyContent = "center";
    boton.style.zIndex = "9999";
    boton.style.border = "none";
    boton.style.cursor = "pointer";
    boton.style.transition = "transform 0.3s ease";
  
    // Crear la imagen
    const img = document.createElement("img");
    img.src = "/static/images/logo.png"; 
    img.alt = "Botón de chat";
    img.style.width = "30px";
    img.style.height = "30px";
    img.style.objectFit = "contain";
  
    // Insertar imagen dentro del botón
    boton.appendChild(img);
    
    // Efecto hover
    boton.addEventListener("mouseover", function() {
        this.style.transform = "scale(1.1)";
    });
    
    boton.addEventListener("mouseout", function() {
        this.style.transform = "scale(1)";
    });
    
    // Agregar evento de clic para abrir el chatbot
    boton.addEventListener("click", function() {
        abrirChatbot();
    });
  
    // Agregar el botón al body
    document.body.appendChild(boton);
}

// Función para abrir el chatbot en un popup
function abrirChatbot() {
    // Crear el contenedor del popup
    const popupContainer = document.createElement("div");
    popupContainer.id = "popupContainer";
    popupContainer.style.position = "fixed";
    popupContainer.style.top = "0";
    popupContainer.style.left = "0";
    popupContainer.style.width = "100%";
    popupContainer.style.height = "100%";
    popupContainer.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
    popupContainer.style.display = "flex";
    popupContainer.style.justifyContent = "center";
    popupContainer.style.alignItems = "center";
    popupContainer.style.zIndex = "10000";

    // Crear el iframe para cargar el chatbot
    const iframe = document.createElement("iframe");
    iframe.src = "/chatbot";
    iframe.style.width = "90%";
    iframe.style.maxWidth = "400px";
    iframe.style.height = "80%";
    iframe.style.maxHeight = "600px";
    iframe.style.border = "none";
    iframe.style.borderRadius = "15px";
    iframe.style.boxShadow = "0 5px 15px rgba(0, 0, 0, 0.3)";

    // Agregar el iframe al contenedor
    popupContainer.appendChild(iframe);

    // Agregar evento para cerrar el popup al hacer clic fuera del iframe
    popupContainer.addEventListener("click", function(event) {
        if (event.target === popupContainer) {
            document.body.removeChild(popupContainer);
        }
    });

    // Agregar el contenedor al body
    document.body.appendChild(popupContainer);
}

document.addEventListener("DOMContentLoaded", () => {
    crearBotonFlotante();
})