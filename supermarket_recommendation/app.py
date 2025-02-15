from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import base64

app = Flask(__name__)

# Configuración de la base de datos MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',  # Cambia esto por tu usuario de MySQL
    'password': '',  # Cambia esto por tu contraseña de MySQL
    'database': 'supermarket'
}

# Función para obtener los productos de la base de datos
def get_products():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name, category, image FROM products")
    products = cursor.fetchall()

    # Convertir BLOB a base64 para mostrar en HTML
    for product in products:
        if product['image']:
            product['image'] = base64.b64encode(product['image']).decode('utf-8')

    cursor.close()
    connection.close()
    return products

def checkLogin(mail, password):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE mail = %s AND password = %s", (mail, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['mail']
        password = request.form['password']
        # chekc if the user exists
        user = checkLogin(username, password)
        if user:
            return redirect(url_for('likes'))
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')


def get_likes():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("Select * from products")
    likes = cursor.fetchall()

    # Convertir BLOB a base64 para mostrar en HTML
    for like in likes:
        if like['image']:
            like['image'] = base64.b64encode(like['image']).decode('utf-8')

    cursor.close()
    connection.close()
    return likes

@app.route('/likes')
def likes():
    user_likes = get_likes()
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
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO products (name, category, image) VALUES (%s, %s, %s)", (name, category, image))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,port=8080)
