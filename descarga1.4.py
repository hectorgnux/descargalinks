import requests
import os
from urllib.parse import urlparse
import time
import mimetypes
import magic

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

# Diccionario de firmas de archivo para verificar cabeceras
FILE_SIGNATURES = {
    b'\xFF\xD8\xFF': 'image/jpeg',  # JPEG
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',  # PNG
    b'\x47\x49\x46\x38': 'image/gif',  # GIF
    b'\x42\x4D': 'image/bmp',  # BMP
    b'\x52\x49\x46\x46....\x57\x45\x42\x50': 'image/webp',  # WebP
    b'\x25\x50\x44\x46': 'application/pdf',  # PDF
    b'\x50\x4B\x03\x04': 'application/zip',  # ZIP
    b'\x1F\x8B': 'application/gzip',  # GZIP
    b'\x4D\x5A': 'application/x-msdownload',  # EXE
}

def check_file_header(file_path):
    """Verifica la cabecera del archivo para determinar su tipo real."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)  # Leer los primeros 8 bytes
            for signature, mime_type in FILE_SIGNATURES.items():
                if header.startswith(signature[:len(header)]):
                    return mime_type
        # Si no se encuentra una coincidencia, usar python-magic para una verificación más profunda
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception as e:
        print(f"Error al verificar la cabecera de {file_path}: {str(e)}")
        return 'application/octet-stream'

def get_file_extension(headers, file_path=None):
    """Determina la extensión del archivo basada en el encabezado Content-Type o la cabecera del archivo."""
    content_type = headers.get('Content-Type', '').split(';')[0].strip()
    
    # Si es un archivo binario o no hay extensión, verificar la cabecera si tenemos la ruta del archivo
    if (content_type == 'application/octet-stream' or not content_type) and file_path:
        real_mime = check_file_header(file_path)
        return MIME_TO_EXTENSION.get(real_mime, '.bin')
    
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
            
            # Verificar si es un archivo binario o sin extensión y analizar su cabecera
            name, ext = os.path.splitext(filename)
            if ext in ['.bin', '']:  # Verificar tanto .bin como archivos sin extensión
                new_ext = get_file_extension(response.headers, file_path)
                if new_ext != '.bin':
                    new_filename = f"{name}{new_ext}"
                    new_file_path = os.path.join(download_path, new_filename)
                    # Verificar si el nuevo nombre ya existe
                    counter = 1
                    while os.path.exists(new_file_path):
                        new_filename = f"{name}_{counter}{new_ext}"
                        new_file_path = os.path.join(download_path, new_filename)
                        counter += 1
                    os.rename(file_path, new_file_path)
                    file_path = new_file_path
                    filename = new_filename
            
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