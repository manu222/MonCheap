from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import base64
import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Añade una clave secreta para manejar las sesiones

# Configuración de la base de datos MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'moncheap'
}

# Función para obtener la conexión a la base de datos
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# Función para obtener los productos de la base de datos
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM producto")
    products = cursor.fetchall()

    # Convertir BLOB a base64 para mostrar en HTML
    for product in products:
        if not product['img']:
            product['img'] = "No image available"

    cursor.close()
    connection.close()
    return products

def check_login(mail, password):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Para obtener los resultados como diccionario
    cursor.execute("SELECT * FROM usuario WHERE gmail = %s", (mail,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    # Si el usuario existe y la contraseña coincide
    if user and bcrypt.checkpw(password.encode('utf-8'), user['contraseña'].encode('utf-8')):
        return user
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['mail']
        password = request.form['password']

        user = check_login(username, password)
        if user:
            session['user_id'] = user['id']  # Guardar el user_id en la sesión
            session['user_name'] = user['nombre']
            session['user_mail'] = user['gmail']
            return redirect(url_for('likes', user_id=user['id']))
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['gmail']
        password = request.form['password']

        #Hashear la contraseña
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT * FROM usuario WHERE gmail = %s", (correo,))

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            connection.close()
            return render_template('register.html', error='Este correo ya está registrado')

        # Insertar el nuevo usuario en la base de datos
        cursor.execute("INSERT INTO usuario (nombre, gmail, contraseña) VALUES (%s, %s, %s)",
                       (nombre, correo, hashed_password.decode('utf-8')))
        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for('login'))  # Redirigir al login después del registro

    return render_template('register.html')

#Función para cargar la página de usuarios
@app.route('/user', methods=['GET', 'POST'])
def user():
   return render_template('user.html')

#Función para actualizar el nombre del usuario
@app.route('/user_update', methods=['GET', 'POST'])
def user_update():
    if request.method == 'POST':
        #Sacar el nombre del usuario y su gmail
        nombre = request.form['nombre']
        id = session["user_id"]

        #Conectarse a la DB
        connection = get_db_connection()
        cursor = connection.cursor()


        cursor.execute("UPDATE usuario SET nombre = %s WHERE id = %s", (nombre, id))

        cursor.close()
        connection.close()
        # Actualizar la sesión con el nuevo nombre
        session['user_name'] = nombre

# Función para obtener los productos que el usuario tiene como "me gusta"
def get_likes(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT p.id_producto, p.nombre, p.marca, p.categoria, p.img, COALESCE(MIN(pr.precio), 0) AS precio
    FROM likes l
    JOIN producto p ON l.id_producto = p.id_producto
    LEFT JOIN precios pr ON p.id_producto = pr.id_producto
    WHERE l.id_user = %s
    GROUP BY p.id_producto, p.nombre, p.marca, p.categoria, p.img
    """
    
    cursor.execute(query, (user_id,))
    likes = cursor.fetchall()

    for like in likes:
        if not like['img']:
            like['img'] = "../static/images/placeholder.png"

    cursor.close()
    connection.close()
    return likes


@app.route('/likes/<int:user_id>')
def likes(user_id):
    user_likes = get_likes(user_id)
    return render_template('likes.html', user_likes=user_likes)


@app.route('/')
def index():
    products = get_products()
    return render_template('index.html', products=products)


@app.route('/upload', methods=['POST'])
def upload():
    # Obtener los datos del formulario
    name = request.form['name']
    category = request.form['category']
    
    # Leer la imagen como BLOB
    image = request.files['image'].read()

    # Conectar a la base de datos y guardar los datos
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO producto (nombre, categoria, img) VALUES (%s, %s, %s)", (name, category, image))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('index'))


@app.route('/toggle_favorite/<int:product_id>', methods=['POST'])
def toggle_favorite(product_id):
    # Verifica si el usuario está autenticado
    if 'user_id' not in session:
        return jsonify(success=False, error="Usuario no autenticado"), 401

    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Verificar si el registro ya existe en la tabla likes
    query = "SELECT * FROM likes WHERE id_user = %s AND id_producto = %s"
    cursor.execute(query, (user_id, product_id))
    like = cursor.fetchone()
    
    if like:
        # Si ya existe, eliminarlo (quitar de favoritos)
        delete_query = "DELETE FROM likes WHERE id_user = %s AND id_producto = %s"
        cursor.execute(delete_query, (user_id, product_id))
        connection.commit()
        action = "removed"
    else:
        # Si no existe, insertarlo (añadir a favoritos)
        insert_query = "INSERT INTO likes (id_user, id_producto) VALUES (%s, %s)"
        cursor.execute(insert_query, (user_id, product_id))
        connection.commit()
        action = "added"
    
    cursor.close()
    connection.close()
    
    return jsonify(success=True, action=action)


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Eliminar el user_id de la sesión
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
    