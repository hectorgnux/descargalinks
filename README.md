# Descargador de Archivos desde URLs

Este script en Python permite descargar archivos desde una lista de URLs especificadas en un archivo de texto. El script detecta automáticamente la extensión de los archivos (por ejemplo, `.jpg`, `.png`, `.obj`) utilizando el encabezado `Content-Type` de las respuestas HTTP y genera nombres únicos para evitar sobrescritura. Además, solicita al usuario el nombre del archivo que contiene los enlaces.

**Créditos**: Telegram @Gandalf775

## Características
- Lee URLs desde un archivo de texto especificado por el usuario.
- Descarga archivos uno por uno a una carpeta `downloads`.
- Detecta extensiones de archivo (incluyendo `.obj`) mediante el encabezado `Content-Type`.
- Genera nombres únicos para los archivos descargados (por ejemplo, `downloaded_file_1.obj`, `downloaded_file_2.jpg`).
- Evita sobrescritura añadiendo contadores (por ejemplo, `downloaded_file_1_1.obj`).
- Maneja errores como URLs inválidas o archivos de entrada no encontrados.

## Requisitos
- **Python**: Versión 3.6 o superior.
- **Librería `requests`**:
  ```bash
  pip install requests
  ```
Las librerías estándar os, urllib.parse, y time están incluidas en Python.


  
