import os

STORAGE_SERVICE_UPLOAD_URL = f"http://{os.environ.get('STORAGE_SERVICE_HOST')}:8080/upload"
STORAGE_SERVICE_SAVE_URL = f"http://{os.environ.get('STORAGE_SERVICE_HOST')}:8080/save"
STORAGE_SERVICE_FILES_URL = f'http://{os.environ.get('STORAGE_SERVICE_HOST')}:8080/files/'