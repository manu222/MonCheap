from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from langchain_core.messages.content_blocks import BaseDataContentBlock
import mysql.connector
import base64
import bcrypt
import pandas as pd
from static.funcionesMoncheap import busqueda,similitud
import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os
from flask import Response
import re

BaseDir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = 'supersecretkey'
model = OllamaLLM(model="llama3")
productos_df = pd.read_csv(os.path.join(BaseDir, 'static', 'productos_info_nuevo.csv'))

# Configuración de la base de datos MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'moncheap'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def procesar_imagen(img):
    if not img:
        return url_for('static', filename='images/placeholder.png')
    try:
        if isinstance(img, bytes):
            return f"data:image/jpeg;base64,{base64.b64encode(img).decode('utf-8')}"
        elif not img.startswith(('http', 'https', 'data:', '/static')):
            return url_for('static', filename='images/placeholder.png')
    except:
        return url_for('static', filename='images/placeholder.png')
    return img

def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.marca, p.categoria, p.img, p.kcal,
               p.grasas, p.grasas_saturadas, p.proteinas, p.hidratos_carbono,
               p.azucares, p.sal, p.visitas, pr.supermercado, pr.link,
               pr.precio, pr.precio_oferta, pr.precio_unidad
        FROM producto p
        LEFT JOIN precios pr ON p.id_producto = pr.id_producto
        ORDER BY p.nombre, pr.supermercado;
    """)
    products = cursor.fetchall()

    for p in products:
       # p['img'] = procesar_imagen(p['img'])
        p['img'] = 'https://dx7csy7aghu7b.cloudfront.net/prods/'+str(p['id_producto'])+'.webp'

    cursor.close()
    connection.close()
    return products

def get_likes(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.marca, p.categoria, p.img,
               COALESCE(MIN(pr.precio), 0) AS precio
        FROM likes l
        JOIN producto p ON l.id_producto = p.id_producto
        LEFT JOIN precios pr ON p.id_producto = pr.id_producto
        WHERE l.id_user = %s
        GROUP BY p.id_producto, p.nombre, p.marca, p.categoria, p.img
    """, (user_id,))
    likes = cursor.fetchall()
    for like in likes:
        like['img'] = 'https://dx7csy7aghu7b.cloudfront.net/prods/'+str(like['id_producto'])+'.webp'
    cursor.close()
    connection.close()
    return likes

def get_most_liked():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""SELECT p.id_producto, p.nombre, p.marca, p.categoria, p.img, COUNT(l.id_producto) AS cantidad_likes 
                   FROM producto p JOIN likes l ON p.id_producto = l.id_producto 
                   GROUP BY p.id_producto 
                   ORDER BY cantidad_likes DESC LIMIT 5; """)
    most_liked = cursor.fetchall()
    for like in most_liked:
        #like['img'] = procesar_imagen(like['img'])
        like['img'] = 'https://dx7csy7aghu7b.cloudfront.net/prods/'+str(like['id_producto'])+'.webp'
    cursor.close()
    connection.close()
    return most_liked

def get_most_viewed():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM producto p ORDER BY p.visitas DESC LIMIT 5;")
    most_viewed = cursor.fetchall()
    for item in most_viewed:
        #item['img'] = procesar_imagen(item['img'])
        item['img'] = 'https://dx7csy7aghu7b.cloudfront.net/prods/'+str(item['id_producto'])+'.webp'
    cursor.close()
    conn.close()
    return most_viewed

def check_login(mail, password):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario WHERE gmail = %s", (mail,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['contraseña'].encode('utf-8')):
        return user
    return None

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 1) Traigo todos los productos (con posibles duplicados por cada precio)
    all_products = get_products()

    # 2) Elimino duplicados por id_producto, conservando la primera aparición
    unique_products = {}
    for p in all_products:
        if p['id_producto'] not in unique_products:
            unique_products[p['id_producto']] = p
    productos = list(unique_products.values())

    # 3) Traigo los más gustados y los más vistos
    most_liked = get_most_liked()
    most_viewed = get_most_viewed()

    # 4) Recupero la lista de favoritos del usuario
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id_producto FROM likes WHERE id_user = %s",
        (session['user_id'],)
    )
    favoritos = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()

    # 5) Renderizo el template con la lista filtrada
    return render_template(
        'index.html',
        productos=productos,
        favoritos=favoritos,
        most_liked=most_liked,
        most_viewed=most_viewed
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = check_login(request.form['mail'], request.form['password'])
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            session['user_mail'] = user['gmail']
            return redirect(url_for('index'))
        return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['gmail']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM usuario WHERE gmail = %s", (correo,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return render_template('register.html', error='Este correo ya está registrado')
        cursor.execute("INSERT INTO usuario (nombre, gmail, contraseña) VALUES (%s, %s, %s)",
                       (nombre, correo, password.decode('utf-8')))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/user', methods=['GET', 'POST'])
def user():
    success = request.args.get('success', '')
    error = request.args.get('error', '')
    return render_template('user.html', success=success, error=error)

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT contraseña FROM usuario WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    if not user or not bcrypt.checkpw(current_password.encode('utf-8'), user['contraseña'].encode('utf-8')):
        cursor.close()
        connection.close()
        return redirect(url_for('user', error='La contraseña actual es incorrecta'))
    
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("UPDATE usuario SET contraseña = %s WHERE id = %s", 
                  (hashed_password.decode('utf-8'), session['user_id']))
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('user', success='Contraseña actualizada correctamente'))

@app.route('/user_update', methods=['POST'])
def user_update():
    nombre = request.form['nombre']
    id = session.get("user_id")
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE usuario SET nombre = %s WHERE id = %s", (nombre, id))
    connection.commit()
    cursor.close()
    connection.close()
    session['user_name'] = nombre
    return redirect(url_for('user'))

@app.route('/likes')
def likes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_likes = get_likes(session['user_id'])
    return render_template('likes.html', user_likes=user_likes)

@app.route('/toggle_favorite/<int:product_id>', methods=['POST'])
def toggle_favorite(product_id):
    if 'user_id' not in session:
        return jsonify(success=False, error="Usuario no autenticado"), 401
    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM likes WHERE id_user = %s AND id_producto = %s", (user_id, product_id))
    like = cursor.fetchone()
    if like:
        cursor.execute("DELETE FROM likes WHERE id_user = %s AND id_producto = %s", (user_id, product_id))
        action = "removed"
    else:
        cursor.execute("INSERT INTO likes (id_user, id_producto) VALUES (%s, %s)", (user_id, product_id))
        action = "added"
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(success=True, action=action)

@app.route('/producto/<int:producto_id>')
def producto(producto_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # 1) Incrementar visitas
    cur.execute(
        "UPDATE producto SET visitas = visitas + 1 WHERE id_producto = %s",
        (producto_id,)
    )
    conn.commit()

    # 2) Obtener datos básicos del producto
    cur.execute("""
        SELECT p.id_producto, p.nombre, p.marca, p.categoria, p.img,
               p.kcal, p.grasas, p.grasas_saturadas, p.proteinas,
               p.hidratos_carbono, p.azucares, p.sal, p.visitas
        FROM producto p
        WHERE p.id_producto = %s
    """, (producto_id,))
    producto = cur.fetchone()
    if not producto:
        cur.close()
        conn.close()
        abort(404)

    # 3) Obtener **todos** los precios de ese producto
    cur.execute("""
        SELECT supermercado, link, precio, precio_oferta, precio_unidad
        FROM precios
        WHERE id_producto = %s
        ORDER BY supermercado
    """, (producto_id,))
    precios = cur.fetchall()

    cur.close()
    conn.close()

    # 4) Productos similares (igual que antes)
    all_products = get_products()
    df_productos = pd.read_csv(os.path.join(BaseDir, 'static', 'df_tokens.csv'))
    similares_data = similitud(df_productos, producto_id)

    # Extraemos solo IDs, quitamos el mismo producto y duplicados
    seen = set()
    similares_ids = []
    for item in similares_data:
        pid = item['id']
        if pid != producto_id and pid not in seen:
            seen.add(pid)
            similares_ids.append(pid)
        if len(similares_ids) >= 4:
            break

    productos_similares = [
        p for p in all_products if p['id_producto'] in similares_ids
    ]

    # 5) Eliminar posibles duplicados en productos_similares
    unique_similares = {}
    for p in productos_similares:
        if p['id_producto'] not in unique_similares:
            unique_similares[p['id_producto']] = p
    productos_similares = list(unique_similares.values())

    return render_template(
        'producto.html',
        producto=producto,
        precios=precios,
        productos_similares=productos_similares
    )


@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    category = request.form['category']
    image = request.files['image'].read()
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO producto (nombre, categoria, img) VALUES (%s, %s, %s)", (name, category, image))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    # Obtener todos los productos
    productos = get_products()
    df = pd.DataFrame(productos)

    # Realizar búsqueda con similitud/tokenización personalizada
    resultados = busqueda(query, df)

    # Eliminar duplicados por id_producto (conservando el primero encontrado)
    seen_ids = set()
    resultados_filtrados = []
    for r in resultados:
        if r['id_producto'] not in seen_ids:
            seen_ids.add(r['id_producto'])
            resultados_filtrados.append(r)

    return jsonify(resultados_filtrados)

@app.route('/mapa', )
def mapa():
    return render_template('mapa.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot_popup.html')

@app.route('/chatbot/answer', methods=['POST'])
def chat_api():
    # Recoger la pregunta del usuario
    user_message = request.get_data(as_text=True)

    # Tratar la pregunta del usuario para obtener palabras clave
    user_words = set(re.findall(r'\w+', user_message.lower()))

    # Obtener los productos de la base de datos
    products = get_products()
    
    # Filtrar productos relevantes basados en la consulta del usuario
    filtered_products = []
    for p in products:
        # Crear una copia del producto sin campos innecesarios
        product_info = {
            'nombre': p['nombre'],
            'marca': p['marca'],
            'categoria': p['categoria'],
            'supermercado': p.get('supermercado', ''),
            'precio': p.get('precio', 0)
        }
        
        # Buscar coincidencias en nombre, marca y categoría
        nombre_words = set(re.findall(r'\w+', p['nombre'].lower()))
        marca_words = set(re.findall(r'\w+', p['marca'].lower()))
        categoria_words = set(re.findall(r'\w+', p['categoria'].lower()))
        
        # Si hay coincidencia en alguno de los campos, añadir el producto
        if user_words & (nombre_words | marca_words | categoria_words):
            filtered_products.append(product_info)
    
    # Si no hay productos filtrados, usar los 5 productos más visitados
    if not filtered_products:
        most_viewed = get_most_viewed()
        for p in most_viewed[:5]:
            product_info = {
                'nombre': p['nombre'],
                'marca': p['marca'],
                'categoria': p['categoria']
            }
            filtered_products.append(product_info)

    # Formamos el mensaje para el modelo
    prompt = f"""
    Eres un asistente virtual que habla en español para una página de comparación de precios, llamada Moncheap.
    Pregunta del usuario: {user_message}
    Información sobre los productos del catálogo: {filtered_products}
    
    Quiero que respondas a la pregunta del usuario teniendo en cuenta los productos del catálogo.
    Si el usuario pregunta por un producto específico, menciona los productos relevantes que tenemos en el catálogo.
    Si no hay productos relevantes, sugiere categorías de productos disponibles.
    Sé amable, conciso y útil en tu respuesta.
    """
    chain = ChatPromptTemplate.from_template("{prompt}") | model
    result = chain.invoke({"prompt": prompt})
    return Response("Moncheap: " + result, content_type='text/plain; charset=utf-8')

@app.route('/get_all_products')
def get_all_products():
    products = get_products()
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
