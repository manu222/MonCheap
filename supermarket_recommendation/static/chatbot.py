import os
import requests
import json

class ChatbotBase:
    """Clase base para implementaciones de chatbot"""
    def __init__(self):
        self.conversation_history = []
    
    def add_to_history(self, role, content):
        """Añade un mensaje al historial de conversación"""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_response(self, message):
        """Método que debe ser implementado por las clases hijas"""
        raise NotImplementedError("Las subclases deben implementar este método")

class LocalChatbot(ChatbotBase):
    """Implementación local del chatbot que simula respuestas"""
    def __init__(self):
        super().__init__()
        self.responses = {
            "hola": "¡Hola! Soy el asistente de MonCheap. ¿En qué puedo ayudarte?",
            "ayuda": "Puedo ayudarte a encontrar productos, comparar precios o darte información sobre supermercados.",
            "productos": "En MonCheap puedes encontrar una gran variedad de productos de diferentes supermercados.",
            "precios": "Compara precios de productos en diferentes supermercados para encontrar las mejores ofertas.",
            "supermercados": "Trabajamos con varios supermercados para ofrecerte los mejores precios."
        }
    
    def get_response(self, message):
        """Genera una respuesta basada en palabras clave simples"""
        self.add_to_history("user", message)
        
        message_lower = message.lower()
        
        # Buscar coincidencias en las palabras clave
        for key, response in self.responses.items():
            if key in message_lower:
                self.add_to_history("assistant", response)
                return response
        
        # Respuesta por defecto si no hay coincidencias
        default_response = "Lo siento, no puedo responder a eso en este momento. Estoy en modo local sin conexión a Ollama."
        self.add_to_history("assistant", default_response)
        return default_response

class OllamaChatbot(ChatbotBase):
    """Implementación del chatbot que usa Ollama en el servidor"""
    def __init__(self, model="llama2", api_url="http://localhost:11434"):
        super().__init__()
        self.model = model
        self.api_url = api_url
    
    def get_response(self, message):
        """Obtiene una respuesta de Ollama API"""
        self.add_to_history("user", message)
        
        try:
            # Preparar el prompt con el contexto de la conversación
            system_prompt = "Eres un asistente de MonCheap, una aplicación para comparar precios de productos en supermercados. Responde de manera concisa y útil."
            
            # Construir el historial de conversación para Ollama
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history)
            
            # Hacer la solicitud a la API de Ollama
            response = requests.post(
                f"{self.api_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_response = result.get("message", {}).get("content", "")
                self.add_to_history("assistant", assistant_response)
                return assistant_response
            else:
                error_msg = f"Error al comunicarse con Ollama: {response.status_code}"
                self.add_to_history("assistant", error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error al comunicarse con Ollama: {str(e)}"
            self.add_to_history("assistant", error_msg)
            return error_msg

def get_chatbot_instance():
    """Factory function que devuelve la implementación adecuada según el entorno"""
    # Verificar si estamos en un entorno que tiene Ollama disponible
    # Esto podría ser una variable de entorno o una comprobación de conectividad
    try:
        # Intentar hacer una solicitud simple a Ollama para ver si está disponible
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            print("Ollama detectado, usando OllamaChatbot")
            return OllamaChatbot()
    except:
        # Si hay cualquier error, asumimos que Ollama no está disponible
        pass
    
    print("Ollama no detectado, usando LocalChatbot")
    return LocalChatbot()