class MediaFile:
    def __init__(self, disk_name, file_name, file_path, exif_data, hash_value):
        self.disk_name = disk_name
        self.file_name = file_name
        self.file_path = file_path
        self.exif_data = exif_data
        self.hash_value = hash_value

    def __repr__(self):
        return f"MediaFile(disk_name={self.disk_name}, file_name={self.file_name}, file_path={self.file_path}, exif_data={self.exif_data}, hash_value={self.hash_value})"