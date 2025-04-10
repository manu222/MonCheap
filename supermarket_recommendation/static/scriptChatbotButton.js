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

function abrirChatbot() {
    // Ocultar el botón flotante
    const boton = document.querySelector(".fab");
    if (boton) boton.style.display = "none";

    // Crear el contenedor del popup
    const popupContainer = document.createElement("div");
    popupContainer.id = "popupContainer";
    popupContainer.style.position = "fixed";
    popupContainer.style.bottom = "20px"; // Misma distancia que tenía el botón
    popupContainer.style.right = "20px";
    popupContainer.style.zIndex = "10000";

    // Crear el iframe para cargar el chatbot
    const iframe = document.createElement("iframe");
    iframe.src = "/chatbot";
    iframe.style.width = "90vw";
    iframe.style.maxWidth = "400px";
    iframe.style.height = "80vh";
    iframe.style.maxHeight = "600px";
    iframe.style.border = "none";
    iframe.style.borderRadius = "15px";
    iframe.style.boxShadow = "0 5px 15px rgba(0, 0, 0, 0.3)";
    iframe.style.backgroundColor = "white";

    // Agregar el iframe al contenedor
    popupContainer.appendChild(iframe);

    // Agregar el contenedor al body
    document.body.appendChild(popupContainer);
}

document.addEventListener("DOMContentLoaded", () => {
    crearBotonFlotante();

    window.addEventListener("message", function(event) {
        if (event.data === "cerrarChatbot") {
            const popup = document.getElementById("popupContainer");
            if (popup) popup.remove();
    
            // Mostrar el botón flotante otra vez
            const boton = document.querySelector(".fab");
            if (boton) boton.style.display = "flex"; // o "block", pero "flex" mantiene el centrado del icono
        }
    });    
})