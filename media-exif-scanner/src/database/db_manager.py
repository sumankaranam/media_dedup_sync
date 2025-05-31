from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class MediaFile(Base):
    __tablename__ = 'media_files'
    
    id = Column(Integer, primary_key=True)
    disk_name = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    exif_data = Column(JSON, nullable=True)
    hash_value = Column(String, nullable=False)

class DBManager:
    def __init__(self, db_url='sqlite:///media_files.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_media_file(self, disk_name, file_name, file_path, exif_data, hash_value):
        session = self.Session()
        media_file = MediaFile(
            disk_name=disk_name,
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