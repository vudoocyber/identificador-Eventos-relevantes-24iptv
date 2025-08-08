import requests
import json

def obtener_eventos_json(url):
    """
    Obtiene el contenido de un archivo JSON desde una URL.
    """
    try:
        # Realiza una petición GET a la URL
        respuesta = requests.get(url)
        # Lanza una excepción si la petición no fue exitosa
        respuesta.raise_for_status()

        # Carga el contenido JSON de la respuesta
        datos = respuesta.json()
        return datos

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los datos de la URL: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON: {e}")
        return None

# URL de la que obtendremos los datos
url_eventos = "https://24hometv.xyz/events.json"

# Llama a la función para obtener los eventos
eventos_data = obtener_eventos_json(url_eventos)

if eventos_data:
    # Si la obtención fue exitosa, imprimimos los datos para verificarlos
    print("Datos de eventos obtenidos exitosamente:")
    print(json.dumps(eventos_data, indent=2))
else:
    print("No se pudieron obtener los datos.")
