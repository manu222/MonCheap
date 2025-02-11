document.addEventListener("DOMContentLoaded", () => {
    const loginContainer = document.querySelector(".login-container");
    
    // Animación de entrada
    loginContainer.style.opacity = "0";
    loginContainer.style.transform = "translateY(-20px)";
    
    setTimeout(() => {
        loginContainer.style.transition = "opacity 0.8s ease-out, transform 0.8s ease-out";
        loginContainer.style.opacity = "1";
        loginContainer.style.transform = "translateY(0)";
    }, 200);
});
