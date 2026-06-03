import os
import requests
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class SupabaseMediaStorage(Storage):
    def __init__(self):
        self.project_url = os.environ.get('SUPABASE_URL')
        self.service_key = os.environ.get('SUPABASE_KEY')
        self.bucket = os.environ.get('SUPABASE_STORAGE_BUCKET', 'media')

    def _open(self, name, mode='rb'):
        url = self.url(name)
        response = requests.get(url)
        if response.status_code == 200:
            from io import BytesIO
            from django.core.files.base import File
            return File(BytesIO(response.content), name=name)
        raise FileNotFoundError(f"File not found on Supabase Storage: {name}")

    def _save(self, name, content):
        # name es el path relativo del archivo (ej: perfil/foto.webp)
        url = f"{self.project_url}/storage/v1/object/{self.bucket}/{name}"
        headers = {
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": getattr(content, 'content_type', 'application/octet-stream')
        }
        
        # Leemos los datos del contenido
        file_data = content.read()
        
        # Intentamos subir con POST (crear nuevo objeto)
        response = requests.post(url, headers=headers, data=file_data)
        
        # Si ya existe (status 400 o similar), intentamos un PUT para sobrescribir
        if response.status_code != 200:
            response = requests.put(url, headers=headers, data=file_data)
            if response.status_code != 200:
                raise Exception(f"Failed to upload to Supabase Storage: {response.text}")
                
        return name

    def url(self, name):
        # Retorna la URL pública de la imagen
        return f"{self.project_url}/storage/v1/object/public/{self.bucket}/{name}"

    def exists(self, name):
        url = f"{self.project_url}/storage/v1/object/info/{self.bucket}/{name}"
        headers = {"Authorization": f"Bearer {self.service_key}"}
        response = requests.get(url, headers=headers)
        return response.status_code == 200

    def delete(self, name):
        url = f"{self.project_url}/storage/v1/object/{self.bucket}/{name}"
        headers = {"Authorization": f"Bearer {self.service_key}"}
        requests.delete(url, headers=headers)
