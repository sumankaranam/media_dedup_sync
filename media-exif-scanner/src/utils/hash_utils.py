import hashlib

def generate_hash(file_path, algorithm='sha256'):
    """Generate a hash for the given file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    return hash_func.hexdigest()

def hash_image(file_path):
    """Generate a SHA256 hash for an image file."""
    return generate_hash(file_path, 'sha256')

def hash_video(file_path):
    """Generate a SHA256 hash for a video file."""
    return generate_hash(file_path, 'sha256')