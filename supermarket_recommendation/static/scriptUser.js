function enableEdit() {
    document.getElementById('nombre').removeAttribute('readonly');
    document.getElementById('guardarBtn').style.display = 'inline-block';
    document.getElementById('editarBtn').style.display = 'none';
}

function saveName() {
    document.getElementById('nombre').setAttribute('readonly', true);
    document.getElementById('guardarBtn').style.display = 'none';
    document.getElementById('editarBtn').style.display = 'inline-block';
}

function validatePassword() {
    var newPass = document.getElementById('new_password').value;
    var confirmPass = document.getElementById('confirm_password').value;
    if (newPass !== confirmPass) {
        alert('Las contraseñas no coinciden');
        return false;
    }
    return true;
}