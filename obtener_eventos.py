import requests
import google.generativeai as genai
import os
import json

# Configura tu clave de API de Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Inicializa el modelo
model = genai.GenerativeModel('gemini-1.5-flash')

def obtener_eventos_json(url):
    """
    Obtiene el contenido de un archivo JSON desde una URL.
    """
    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return datos
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los datos de la URL: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON: {e}")
        return None

def analizar_con_gemini(eventos_data):
    """
    Envía los datos de eventos a Gemini para su análisis.
    """
    prompt = (
        "Analiza el siguiente JSON con eventos deportivos y especiales. "
        "Basándote en la popularidad de las ligas, la cobertura mediática en la web y la relevancia de los competidores, "
        "identifica los 3 eventos más importantes del día. "
        "Devuelve la información de estos 3 eventos en formato JSON. "
        f"JSON de eventos: {json.dumps(eventos_data)}"
    )
    
    try:
        response = model.generate_content(prompt)
        # La respuesta de Gemini contendrá el JSON con los eventos filtrados.
        return response.text
    except Exception as e:
        print(f"Error al comunicarse con Gemini: {e}")
        return None

# URL de la que obtendremos los datos
url_eventos = "https://24hometv.xyz/events.json"

# Proceso principal
eventos_data = obtener_eventos_json(url_eventos)

if eventos_data:
    print("Datos de eventos obtenidos exitosamente. Enviando a Gemini para su análisis...")
    eventos_filtrados_json = analizar_con_gemini(eventos_data)
    
    if eventos_filtrados_json:
        print("\nAnálisis de Gemini recibido. Estos son los eventos más importantes:")
        print(eventos_filtrados_json)
        
        # Aquí iría el código para generar el HTML y los mensajes de WhatsApp
        # y para subirlos por FTP.
        # Por ahora, solo lo imprimiremos.
    else:
        print("No se pudo obtener una respuesta de Gemini.")
else:
    print("No se pudo iniciar el proceso.")
