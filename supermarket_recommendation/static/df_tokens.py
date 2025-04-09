import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from unidecode import unidecode
import re
from typing import List, Dict, Any

class TokenProcessor:
    def __init__(self):
        self._search_cache = {}
        self._vectorizer = None
        self._df_vectorized = None
        self._df = None

    def preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para la búsqueda."""
        # Convertir a minúsculas y eliminar acentos
        text = text.lower()
        text = unidecode(text)
        # Eliminar caracteres especiales y números
        text = re.sub(r'[^a-z\s]', ' ', text)
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def load_and_process_data(self, df: pd.DataFrame) -> None:
        """Carga y procesa el DataFrame de productos."""
        self._df = df.copy()
        # Preprocesar nombres de productos
        processed_names = self._df['nombre'].apply(self.preprocess_text)
        
        # Vectorizar los nombres procesados
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self._df_vectorized = self._vectorizer.fit_transform(processed_names)

    def search_products(self, query: str, threshold: float = 0.3, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca productos basándose en la consulta del usuario."""
        # Verificar si la búsqueda está en caché
        cache_key = f"{query}_{threshold}_{limit}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        # Preprocesar la consulta
        processed_query = self.preprocess_text(query)
        if not processed_query:
            return []

        # Vectorizar la consulta
        query_vector = self._vectorizer.transform([processed_query])

        # Calcular similitudes
        similarities = np.dot(self._df_vectorized, query_vector.T).toarray().flatten()

        # Obtener los índices de los productos más similares
        top_indices = np.argsort(similarities)[::-1][:limit]
        top_similarities = similarities[top_indices]

        # Filtrar por umbral y crear resultados
        results = []
        for idx, sim in zip(top_indices, top_similarities):
            if sim >= threshold:
                product = self._df.iloc[idx].to_dict()
                product['similarity_score'] = float(sim)
                results.append(product)

        # Guardar en caché
        self._search_cache[cache_key] = results
        return results

    def clear_cache(self) -> None:
        """Limpia el caché de búsquedas."""
        self._search_cache.clear()

    def get_similar_products(self, product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Encuentra productos similares basándose en un ID de producto."""
        if product_id not in self._df['id_producto'].values:
            return []

        # Obtener el índice del producto
        product_idx = self._df[self._df['id_producto'] == product_id].index[0]
        product_vector = self._df_vectorized[product_idx]

        # Calcular similitudes
        similarities = np.dot(self._df_vectorized, product_vector.T).toarray().flatten()

        # Obtener los índices de los productos más similares (excluyendo el producto mismo)
        top_indices = np.argsort(similarities)[::-1]
        top_indices = top_indices[top_indices != product_idx][:limit]

        # Crear resultados
        results = []
        for idx in top_indices:
            product = self._df.iloc[idx].to_dict()
            product['similarity_score'] = float(similarities[idx])
            results.append(product)

        return results