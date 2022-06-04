from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker
#connect with database
engine = create_engine('sqlite:///MAINPLAYLIST.sqlite') #echo=True
#Manage tables
base = declarative_base()

class import_info123(base):
    __tablename__ = 'main'
    Title = Column(String)
    Author = Column(String)
    Savelocation = Column(String)
    SavelocationThumb = Column(String)
    Album = Column(String)
    Uniqueid = Column(String, primary_key=True)
    def __init__(self, Title, Author, Savelocation, SavelocationThumb, Album, Uniqueid):
        self.Title = Title
        self.Author = Author
        self.Savelocation = Savelocation
        self.SavelocationThumb = SavelocationThumb
        self.Album = Album
        self.Uniqueid = Uniqueid
base.metadata.create_all(engine)
