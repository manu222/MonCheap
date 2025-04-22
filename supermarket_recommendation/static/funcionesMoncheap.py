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
    productos_features = productos.drop(["id"], axis=1)
    p1_index = productos[productos['id'] == id].index[0]
    p1_values = productos_features.iloc[p1_index].values.reshape(1, -1)
    # Calcular la similitud de coseno con todos los productos
    similitudes = cosine_similarity(p1_values, productos_features)[0]
 
    # Crear DataFrame con los resultados
    resultados = pd.DataFrame({
        'id': productos['id'],
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
def busqueda(palabra,corpus,umbral=40):
    lista_nombres = corpus['nombre'].values.tolist()
    coincidencias = process.extract(palabra, lista_nombres, limit=5)  # Encuentra las 5 mejores coincidencias
 
    # Filtra resultados según el umbral de similitud
    resultados_filtrados = [match for match, score in coincidencias if score >= umbral]
 
    resultados_dict = corpus[corpus['nombre'].isin(resultados_filtrados)].to_dict(orient="records")
 
    return resultados_dict




