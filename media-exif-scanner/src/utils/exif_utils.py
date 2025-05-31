import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def extract_exif_data(image_path):
    exif_data = {}
    try:
        image = Image.open(image_path)
        if hasattr(image, '_getexif'):
            exif = image._getexif()
            if exif is not None:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
    except Exception as e:
        print(f"Error extracting EXIF data from {image_path}: {e}")
    return exif_data

def get_gps_info(exif_data):
    gps_info = {}
    if 'GPSInfo' in exif_data:
        for key in exif_data['GPSInfo']:
            decoded_key = GPSTAGS.get(key, key)
            gps_info[decoded_key] = exif_data['GPSInfo'][key]
    return gps_info

def extract_all_exif(image_paths):
    all_exif_data = {}
    for path in image_paths:
        all_exif_data[path] = extract_exif_data(path)
    return all_exif_data