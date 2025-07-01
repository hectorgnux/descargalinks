# Script para descargar archivos desde URLs listadas en un archivo
# Créditos: Telegram @Gandalf775
# Modificado para aceptar solo archivos .txt,preguntar por directorio de almacenamiento 
# Créditos: Telegram @hinakawa

import requests
import os
from urllib.parse import urlparse
import time
import mimetypes

# Diccionario para mapear tipos MIME a extensiones comunes
MIME_TO_EXTENSION = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/bmp': '.bmp',
    'image/webp': '.webp',
    'application/pdf': '.pdf',
    'application/zip': '.zip',
    'text/plain': '.txt',  # Puede usarse para .obj, ya que .obj es texto
    'text/html': '.html',
    'video/mp4': '.mp4',
    'audio/mpeg': '.mp3',
    'application/octet-stream': '.obj',  # Usado para .obj en algunos servidores
    'model/obj': '.obj'  # Tipo MIME específico para .obj, si el servidor lo usa
}

def get_file_extension(headers):
    """Determina la extensión del archivo basada en el encabezado Content-Type."""
    content_type = headers.get('Content-Type', '').split(';')[0].strip()
    return MIME_TO_EXTENSION.get(content_type, '.bin')

def download_file(url, download_path, index):
    try:
        # Obtener el nombre del archivo desde la URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # Si no hay nombre de archivo o es muy largo, usar un nombre por defecto
        if not filename or len(filename) > 50:  # Evitar nombres largos o hash
            filename = f'downloaded_file_{index}'
        else:
            # Obtener la extensión del archivo (si existe)
            name, ext = os.path.splitext(filename)
            if not ext:  # Si no hay extensión en la URL
                filename = f"{name}_{index}"
            else:
                filename = f"{name}_{index}{ext}"
        
        # Realizar una solicitud HEAD para obtener los encabezados
        head_response = requests.head(url, allow_redirects=True)
        if head_response.status_code == 200:
            # Obtener la extensión desde el Content-Type si no hay extensión en la URL
            name, ext = os.path.splitext(filename)
            if not ext:  # Si no hay extensión, usar Content-Type
                ext = get_file_extension(head_response.headers)
                filename = f"{name}{ext}"
        
        # Crear la ruta completa del archivo
        file_path = os.path.join(download_path, filename)
        
        # Verificar si el archivo ya existe
        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(filename)
            # Quitar el índice anterior si existe
            name = name.rsplit('_', 1)[0]
            # Añadir un nuevo contador
            filename = f"{name}_{index}_{counter}{ext}"
            file_path = os.path.join(download_path, filename)
            counter += 1
        
        # Realizar la solicitud HTTP para descargar el archivo
        response = requests.get(url, stream=True)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Escribir el contenido en el archivo
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Descargado: {filename}")
            return True
        else:
            print(f"Error al descargar {url}: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error al descargar {url}: {str(e)}")
        return False

def main():
    # Preguntar al usuario el nombre del archivo con las URLs
    input_file = input("Ingrese el nombre del archivo que contiene los enlaces (por ejemplo, urls.txt): ").strip()
    
    # Verificar que el archivo de entrada sea de texto plano
    mime_type, _ = mimetypes.guess_type(input_file)
    if mime_type != 'text/plain':
        print(f"Error: El archivo {input_file} no es un archivo de texto plano.")
        return
    
    # Preguntar al usuario el directorio de salida
    download_path = input("Ingrese el directorio donde se guardarán los archivos descargados: ").strip()
    
    # Crear el directorio si no existe
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    try:
        # Leer el archivo con las URLs
        with open(input_file, 'r', encoding='utf-8') as file:
            urls = file.readlines()
        
        # Procesar cada URL con un índice
        for index, url in enumerate(urls, start=1):
            url = url.strip()  # Eliminar espacios y saltos de línea
            if url:  # Verificar que la URL no esté vacía
                download_file(url, download_path, index)
                
    except FileNotFoundError:
        print(f"No se encontró el archivo {input_file}")
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")

if __name__ == "__main__":
    main()
