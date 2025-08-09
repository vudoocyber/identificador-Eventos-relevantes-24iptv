import requests
import google.generativeai as genai
import os
import json
from datetime import datetime
from ftplib import FTP

# --- Configuración ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Inicializa el modelo
model = genai.GenerativeModel('gemini-1.5-flash')

# Variables ocultas en GitHub Secrets
URL_FUENTE = os.environ.get("URL_FUENTE")
FTP_HOST = os.environ.get("FTP_HOST")
FTP_USER = os.environ.get("FTP_USUARIO")
FTP_PASS = os.environ.get("FTP_CONTRASENA")
NOMBRE_ARCHIVO_MENSAJE = os.environ.get("NOMBRE_ARCHIVO_MENSAJE", "eventos-relevantes.html")
FTP_DIR = os.environ.get("FTP_DIR", "/")

# --- Funciones de obtención y análisis ---

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
    Envía los datos de eventos a Gemini para su análisis y filtra los 3 más importantes.
    """
    prompt = (
        "Analiza el siguiente JSON con eventos deportivos y especiales. "
        "Basándote en la popularidad de las ligas, la cobertura mediática en la web y la relevancia de los competidores, "
        "identifica los 3 eventos más importantes del día. "
        "Devuelve solo un array de JSON, donde cada objeto tenga las llaves 'evento_principal', 'descripcion' y 'horarios'. "
        "**NO incluyas texto adicional ni explicaciones, solo el JSON.** "
        "JSON de eventos: " + json.dumps(eventos_data)
    )

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace("```json\n", "").replace("\n```", "")
        return json.loads(response_text)
    except Exception as e:
        print(f"Error al comunicarse con Gemini o decodificar la respuesta: {e}")
        return None

# --- Funciones de generación y subida de archivos ---

def generar_html(eventos, filename):
    """
    Genera un archivo HTML con los eventos importantes.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Eventos Importantes del Día</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; color: #333; }}
            .container {{ max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #0056b3; text-align: center; }}
            .evento {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
            .evento:last-child {{ border-bottom: none; }}
            h2 {{ margin: 0 0 5px; color: #333; font-size: 1.2em; }}
            p {{ margin: 0; color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Eventos Importantes del Día</h1>
            <p style="text-align: center; color: #999;">Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    """

    for evento in eventos:
        html_content += f"""
        <div class="evento">
            <h2>{evento.get("evento_principal", "")}</h2>
            <p><strong>Descripción:</strong> {evento.get("descripcion", "")}</p>
            <p><strong>Horario:</strong> {evento.get("horarios", "")}</p>
        </div>
        """

    html_content += """
        </div>
    </body>
    </html>
    """

    with open(filename, "w") as f:
        f.write(html_content)

    print(f"Archivo '{filename}' generado.")

def generar_texto_whatsapp(eventos):
    """
    Genera el texto formateado para WhatsApp y estados.
    """
    whatsapp_text = "¡Hola! Estos son los eventos más importantes de hoy:\n\n"

    for evento in eventos:
        whatsapp_text += f"*{evento.get('evento_principal', '')}*\n"
        whatsapp_text += f"📅 {evento.get('descripcion', '')}\n"
        whatsapp_text += f"⏰ {evento.get('horarios', '')}\n\n"

    print("\nTexto para WhatsApp y estados generado:")
    print("---------------------------------------")
    print(whatsapp_text)
    print("---------------------------------------")

def subir_por_ftp(filename, remote_dir):
    """
    Sube un archivo al servidor FTP.
    """
    try:
        with FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
            ftp.cwd(remote_dir)
            with open(filename, "rb") as file:
                ftp.storbinary(f"STOR {os.path.basename(filename)}", file)
            print(f"Archivo '{filename}' subido exitosamente a '{FTP_HOST}{remote_dir}'.")
    except Exception as e:
        print(f"Error al subir el archivo por FTP: {e}")

# --- Proceso principal ---

def main():
    if not URL_FUENTE or not FTP_HOST or not FTP_USER or not FTP_PASS:
        print("Error: Las variables de entorno de configuración no están establecidas.")
        return

    eventos_data = obtener_eventos_json(URL_FUENTE)

    if eventos_data:
        print("Datos de eventos obtenidos exitosamente. Enviando a Gemini para su análisis...")
        eventos_filtrados = analizar_con_gemini(eventos_data)

        if eventos_filtrados:
            print("\nAnálisis de Gemini recibido. Generando contenido...")
            generar_html(eventos_filtrados, NOMBRE_ARCHIVO_MENSAJE)
            generar_texto_whatsapp(eventos_filtrados)

            subir_por_ftp(NOMBRE_ARCHIVO_MENSAJE, FTP_DIR)
        else:
            print("No se pudo obtener una respuesta de Gemini.")
    else:
        print("No se pudo iniciar el proceso.")

if __name__ == "__main__":
    main()
