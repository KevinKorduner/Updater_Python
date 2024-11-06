import requests
import os
import zipfile
import sys
import ctypes

def get_executable_dir():
    """Obtiene el directorio del ejecutable o del script si se ejecuta desde un script"""
    if getattr(sys, 'frozen', False):
        # Si se está ejecutando desde un ejecutable generado por PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Si se está ejecutando desde un script Python
        return os.path.dirname(os.path.abspath(__file__))

def get_current_version(version_file_path):
    """Obtiene la versión actual del archivo VGEx.ini"""
    if not os.path.isfile(version_file_path):
        print(f'Error: El archivo {version_file_path} no existe.')
        return None
    try:
        with open(version_file_path, 'r') as file:
            return file.readline().strip()  # Leer la primera línea y eliminar espacios en blanco
    except Exception as e:
        print(f'Error al leer el archivo {version_file_path}: {e}')
        return None

def download_patch(url, dest_folder, filename):
    """Descarga un parche y muestra una barra de progreso"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx/5xx
        total_size = int(response.headers.get('content-length', 0))
        file_path = os.path.join(dest_folder, filename)
        
        with open(file_path, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                done = int(50 * file.tell() / total_size)
                sys.stdout.write(f'\r[{"=" * done}{" " * (50 - done)}] {int(100 * file.tell() / total_size)}%')
                sys.stdout.flush()
        print('\nParche descargado exitosamente.')
    except requests.RequestException as e:
        print(f'Error al descargar el parche: {e}')
    except Exception as e:
        print(f'Error al guardar el parche: {e}')

def apply_patch(patch_path, game_folder):
    """Aplica el parche (extrae el archivo zip)"""
    if not os.path.isfile(patch_path):
        print(f'Error: El archivo {patch_path} no existe.')
        return
    try:
        with zipfile.ZipFile(patch_path, 'r') as zip_ref:
            zip_ref.extractall(game_folder)
        print('Parche aplicado exitosamente.')
    except zipfile.BadZipFile:
        print(f'Error: El archivo {patch_path} no es un archivo zip válido.')
    except Exception as e:
        print(f'Error al aplicar el parche: {e}')

def update_version_file(version_file_path, new_version):
    """Actualiza el número de versión en VGEx.ini"""
    try:
        with open(version_file_path, 'w') as file:
            file.write(f'{new_version}\n')  # Solo el número de versión
        print('Número de versión actualizado exitosamente.')
    except Exception as e:
        print(f'Error al actualizar el archivo {version_file_path}: {e}')

def get_current_version_from_response(response_text):
    """Obtiene la versión del servidor desde el contenido de VGEx.ini"""
    return response_text.strip()  # Suponiendo que solo hay un número en el archivo

def main():
    # Obtener el directorio del ejecutable o del script
    base_dir = get_executable_dir()
    
    # Archivos y URLs
    init_folder = os.path.join(base_dir, 'DATA')
    version_file_path = os.path.join(init_folder, 'DATA.ini')
    version_url = 'https://servidor-ftp.com/VGEx.ini'
    base_url = 'https://servidor-ftp.com/updater/'
    
    # Verificar y mostrar la ruta del archivo de versión
    print(f'Ruta del archivo de versión: {version_file_path}')
    
    # Obtener la versión actual
    current_version = get_current_version(version_file_path)
    if not current_version:
        print('No se pudo obtener la versión actual.')
        return
    
    # Obtener la versión del servidor
    try:
        response = requests.get(version_url)
        response.raise_for_status()
        server_version = get_current_version_from_response(response.text)
        if not server_version:
            print('No se pudo obtener la versión del servidor.')
            return
    except requests.RequestException as e:
        print(f'Error al obtener la versión del servidor: {e}')
        return

    # Comparar versiones y actualizar si es necesario
    if current_version != server_version:
        patch_filename = f'Ejecutable{server_version}.zip'
        patch_url = f'{base_url}{patch_filename}'
        
        print(f'Actualizando de versión {current_version} a {server_version}...')
        
        # Descargar y aplicar el parche
        download_patch(patch_url, base_dir, 'patch.zip')
        apply_patch(os.path.join(base_dir, 'patch.zip'), base_dir)
        
        # Actualizar archivo de versión
        update_version_file(version_file_path, server_version)
    else:
        print('El cliente ya está actualizado.')

if __name__ == '__main__':
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Si no es administrador, vuelve a ejecutar el script con permisos de administrador
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        main()
