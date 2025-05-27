import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import process

'''
Función que calcula la similitud entre items

Productos: Dataframe de nombre vectorizados
ID: identificador del producto que queremos comparar con el resto.

Devuelve un diccionario con el id del producto con su similitud.
'''
def similitud(productos, id):
    productos_features = productos.drop(["id_producto"], axis=1)
    p1_index = productos[productos['id_producto'] == id].index[0]
    p1_values = productos_features.iloc[p1_index].values.reshape(1, -1)
    # Calcular la similitud de coseno con todos los productos
    similitudes = cosine_similarity(p1_values, productos_features)[0]
 
    # Crear DataFrame con los resultados
    resultados = pd.DataFrame({
        'id': productos['id_producto'],
        'sim': similitudes
    })
 
    # Eliminar el producto consultado y ordenar de mayor a menor similitud
    resultados = resultados[resultados['id'] != id].sort_values(by='sim', ascending=False)
 
    return resultados.to_dict('records')  # Convertir a lista de diccionarios si se desea mantener el formato original
"""
Función que busca las 5 coincidencias más cercanas a un termino en un corpus (un dataframe)
palabra = String, es el termino de búsqueda
corpus = colección de datos entre las que queremos buscar
umbral = umbral de similitud que queremos usar (con 40 funciona bastante bien, pero se puede cambiar)

Devuelve un diccionario con los id y los nombres de los productos más similares.
"""
def busqueda(palabra, corpus, umbral=40):
    """
    Función que busca coincidencias de un término en un corpus (dataframe)
    
    Args:
        palabra: String, término de búsqueda
        corpus: DataFrame, colección de datos entre las que queremos buscar
        umbral: Umbral de similitud (default: 40)
    
    Returns:
        Diccionario con los productos más similares
    """
    import unicodedata
    import re
    
    # Verificar que el corpus tenga la columna 'nombre'
    if 'nombre' not in corpus.columns:
        return []
    
    # Si la palabra está vacía, devolver lista vacía
    if not palabra or palabra.strip() == '':
        return []
    
    # Función para normalizar texto (eliminar acentos, convertir a minúsculas, etc.)
    def normalizar_texto(texto):
        if not isinstance(texto, str):
            return ''
        # Convertir a minúsculas
        texto = texto.lower()
        # Eliminar acentos
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        # Eliminar caracteres especiales y dejar solo letras, números y espacios
        texto = re.sub(r'[^\w\s]', ' ', texto)
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    # Normalizar la palabra de búsqueda
    palabra_norm = normalizar_texto(palabra)
    
    # Tokenizar la palabra de búsqueda (dividir en palabras individuales)
    tokens_busqueda = set(palabra_norm.split())
    
    # Para búsquedas muy cortas o de una sola palabra
    if len(palabra) <= 2 or len(tokens_busqueda) == 1:
        # Preparar listas normalizadas
        nombres_norm = corpus['nombre'].apply(normalizar_texto).tolist()
        
        # Buscar por prefijo para palabras cortas
        if len(palabra) <= 2:
            resultados_prefijo = []
            for i, nombre in enumerate(nombres_norm):
                if any(palabra in nombre.split() or nombre.startswith(palabra) for palabra in tokens_busqueda):
                    resultados_prefijo.append(corpus.iloc[i]['nombre'])
            
            if resultados_prefijo:
                resultados_dict = corpus[corpus['nombre'].isin(resultados_prefijo)].to_dict(orient="records")
                return resultados_dict
    
    # Preparar datos normalizados para búsqueda
    corpus_temp = corpus.copy()
    corpus_temp['nombre_norm'] = corpus['nombre'].apply(normalizar_texto)
    if 'marca' in corpus.columns:
        corpus_temp['marca_norm'] = corpus['marca'].apply(normalizar_texto)
    if 'categoria' in corpus.columns:
        corpus_temp['categoria_norm'] = corpus['categoria'].apply(normalizar_texto)
    
    # Calcular puntuación por coincidencia de tokens
    resultados_score = []
    
    for idx, row in corpus_temp.iterrows():
        score = 0
        max_score = 0
        
        # Tokenizar campos
        tokens_nombre = set(row['nombre_norm'].split())
        tokens_marca = set(row['marca_norm'].split()) if 'marca_norm' in row else set()
        tokens_categoria = set(row['categoria_norm'].split()) if 'categoria_norm' in row else set()
        
        # Calcular coincidencias por tokens
        coincidencias_nombre = tokens_busqueda.intersection(tokens_nombre)
        coincidencias_marca = tokens_busqueda.intersection(tokens_marca)
        coincidencias_categoria = tokens_busqueda.intersection(tokens_categoria)
        
        # Ponderación: nombre (3x), marca (2x), categoría (1x)
        score = (len(coincidencias_nombre) * 3) + (len(coincidencias_marca) * 2) + len(coincidencias_categoria)
        max_possible = (len(tokens_busqueda) * 3)  # Máxima puntuación posible (si todas las palabras coinciden en nombre)
        
        # Normalizar score a porcentaje
        normalized_score = (score / max_possible * 100) if max_possible > 0 else 0
        
        # Añadir a resultados si supera el umbral
        if normalized_score >= umbral:
            resultados_score.append((idx, normalized_score))
    
    # Ordenar por puntuación descendente
    resultados_score.sort(key=lambda x: x[1], reverse=True)
    
    # Si no hay resultados con el umbral actual, intentar con umbral reducido
    if not resultados_score and umbral > 20:
        umbral_reducido = max(20, umbral - 20)
        
        # Repetir búsqueda con umbral reducido
        for idx, row in corpus_temp.iterrows():
            score = 0
            max_score = 0
            
            # Tokenizar campos
            tokens_nombre = set(row['nombre_norm'].split())
            tokens_marca = set(row['marca_norm'].split()) if 'marca_norm' in row else set()
            tokens_categoria = set(row['categoria_norm'].split()) if 'categoria_norm' in row else set()
            
            # Calcular coincidencias por tokens
            coincidencias_nombre = tokens_busqueda.intersection(tokens_nombre)
            coincidencias_marca = tokens_busqueda.intersection(tokens_marca)
            coincidencias_categoria = tokens_busqueda.intersection(tokens_categoria)
            
            # Ponderación: nombre (3x), marca (2x), categoría (1x)
            score = (len(coincidencias_nombre) * 3) + (len(coincidencias_marca) * 2) + len(coincidencias_categoria)
            max_possible = (len(tokens_busqueda) * 3)  # Máxima puntuación posible
            
            # Normalizar score a porcentaje
            normalized_score = (score / max_possible * 100) if max_possible > 0 else 0
            
            # Añadir a resultados si supera el umbral reducido
            if normalized_score >= umbral_reducido:
                resultados_score.append((idx, normalized_score))
        
        # Ordenar por puntuación descendente
        resultados_score.sort(key=lambda x: x[1], reverse=True)
    
    # Si aún no hay resultados, usar fuzzy matching como respaldo
    if not resultados_score:
        # Usar fuzzy matching con process.extract
        lista_nombres = corpus['nombre'].values.tolist()
        coincidencias_nombre = process.extract(palabra, lista_nombres, limit=50)
        resultados_filtrados_nombre = [match for match, score in coincidencias_nombre if score >= umbral]
        
        # Obtener índices de los resultados
        indices = corpus[corpus['nombre'].isin(resultados_filtrados_nombre)].index.tolist()
        resultados_score = [(idx, 0) for idx in indices]  # Score 0 porque ya pasaron el umbral de fuzzy
    
    # Limitar a los 50 mejores resultados
    indices_seleccionados = [idx for idx, _ in resultados_score[:50]]
    
    # Obtener los registros completos
    resultados_dict = corpus.iloc[indices_seleccionados].to_dict(orient="records")
    
    return resultados_dict




