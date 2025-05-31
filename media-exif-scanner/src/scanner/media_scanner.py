import os
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS
import mimetypes

class MediaScanner:
    def __init__(self, paths):
        self.paths = paths
        self.media_files = []

    def scan_media(self):
        for path in self.paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.is_image(file_path) or self.is_video(file_path):
                            exif_data = self.extract_exif(file_path) if self.is_image(file_path) else {}
                            hash_value = self.calculate_hash(file_path)
                            self.media_files.append({
                                'disk_name': os.path.splitdrive(path)[0],
                                'file_name': file,
                                'file_path': file_path,
                                'exif_data': exif_data,
                                'hash_value': hash_value
                            })

    def is_image(self, file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type and mime_type.startswith('image/')

    def is_video(self, file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type and mime_type.startswith('video/')

    def extract_exif(self, file_path):
        exif_data = {}
        try:
            image = Image.open(file_path)
            if hasattr(image, '_getexif'):
                exif = image._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
        except Exception as e:
            print(f"Error extracting EXIF data from {file_path}: {e}")
        return exif_data

    def calculate_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()