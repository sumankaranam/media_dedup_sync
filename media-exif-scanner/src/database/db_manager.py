from sqlalchemy import create_engine, Column, String, Integer, JSON, distinct
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class MediaFile(Base):
    __tablename__ = 'media_files'
    
    id = Column(Integer, primary_key=True)
    disk_name = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    exif_data = Column(JSON, nullable=True)
    hash_value = Column(String, nullable=False)
    is_duplicate = Column(Integer, default=0)  # 0: No, 1: Yes

    def to_dict(self):
        return {
            "disk_name": self.disk_name,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "exif_data": self.exif_data,
            "hash_value": self.hash_value,
            "is_duplicate": self.is_duplicate
        }

class DBManager:
    def __init__(self, db_url='sqlite:///media_files.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_media_file(self, disk_name, file_name, file_path, exif_data, hash_value):
        session = self.Session()
        media_file = MediaFile(
            disk_name=os.path.splitdrive(file_path)[0],
            file_name=file_name,
            file_path=file_path,
            exif_data=exif_data,
            hash_value=hash_value
        )
        session.add(media_file)
        session.commit()
        session.close()

    def get_all_media_files(self):
        session = self.Session()
        media_files = session.query(MediaFile).all()
        session.close()
        return media_files

    def clear_database(self):
        session = self.Session()
        session.query(MediaFile).delete()
        session.commit()
        session.close()

    def get_all_paths(self):
        """
        Returns a list of all unique file paths (folders) that have been scanned.
        """
        session = self.Session()
        try:
            paths = session.query(distinct(MediaFile.file_path)).all()
            # Extract folder part from file_path
            folders = set(os.path.dirname(row[0]) for row in paths)
            return list(folders)
        finally:
            session.close()

    def get_all_files(self):
        """
        Returns all file metadata as a list of dicts.
        """
        session = self.Session()
        try:
            files = session.query(MediaFile).all()
            return [f.to_dict() for f in files]
        finally:
            session.close()

    def get_files_by_path(self, path):
        """
        Returns all file metadata for a given folder path.
        """
        session = self.Session()
        try:
            files = session.query(MediaFile).filter(MediaFile.file_path.like(f"{path}%")).all()
            return [f.to_dict() for f in files]
        finally:
            session.close()

    def add_file_with_exif(self, disk_name, file_name, file_path, mime_type, hash_value):
        """
        Adds a media file to the database, extracting and cleaning EXIF data if the file is an image.
        """
        session = self.Session()
        try:
            # Only extract EXIF data for image files
            exif_data = extract_exif_data(file_path) if mime_type and mime_type.startswith('image/') else {}
            exif_data = clean_exif_data(exif_data)
            
            media_file = MediaFile(
                disk_name=os.path.splitdrive(file_path)[0],
                file_name=file_name,
                file_path=file_path,
                exif_data=exif_data,
                hash_value=hash_value
            )
            session.add(media_file)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding file {file_name}: {e}")
        finally:
            session.close()

    def mark_as_duplicate(self, file_path):
        session = self.Session()
        try:
            file = session.query(MediaFile).filter_by(file_path=file_path).first()
            if file:
                file.is_duplicate = True
                session.commit()
        finally:
            session.close()

    def file_exists(self, file_path, hash_value):
        session = self.Session()
        try:
            # Check by file_path or hash_value (choose one or both as needed)
            exists = session.query(MediaFile).filter_by(file_path=file_path).first() is not None
            # Or, to check by hash: (uncomment if you want to skip by hash too)
            # exists = session.query(MediaFile).filter_by(hash_value=hash_value).first() is not None
            return exists
        finally:
            session.close()