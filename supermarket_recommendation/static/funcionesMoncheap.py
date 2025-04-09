import pandas as pd
from .df_tokens import TokenProcessor

# Inicializar el procesador de tokens
token_processor = TokenProcessor()

'''
Función que calcula la similitud entre items

Productos: Dataframe de nombre vectorizados
ID: identificador del producto que queremos comparar con el resto.

Devuelve un diccionario con el id del producto con su similitud.
'''
def similitud(productos, id):
    # Cargar y procesar los datos si aún no se ha hecho
    if token_processor._df is None:
        token_processor.load_and_process_data(productos)
    
    # Obtener productos similares usando el procesador de tokens
    resultados = token_processor.get_similar_products(id)
    
    # Convertir los resultados al formato esperado
    return [{'id': r['id_producto'], 'sim': r['similarity_score']} for r in resultados]  # Convertir a lista de diccionarios si se desea mantener el formato original

"""
Función que busca las 5 coincidencias más cercanas a un termino en un corpus (un dataframe)
palabra = String, es el termino de búsqueda
corpus = colección de datos entre las que queremos buscar
umbral = umbral de similitud que queremos usar (con 40 funciona bastante bien, pero se puede cambiar)

Devuelve un diccionario con los id y los nombres de los productos más similares.
"""
def busqueda(palabra, corpus, umbral=0.3):
    # Cargar y procesar los datos si aún no se ha hecho
    if token_processor._df is None:
        token_processor.load_and_process_data(corpus)
    
    # Realizar la búsqueda usando el procesador de tokens
    resultados = token_processor.search_products(palabra, threshold=umbral)
    
    return resultados




