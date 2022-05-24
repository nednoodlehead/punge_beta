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
















'''
class testing():
    def __init__(self, title, author, saveloc, saveloc_thumb, album, uniqueid):
        self.title = title
        self.author = author
        self.saveloc = saveloc
        self.saveloc_thumb = saveloc_thumb
        self.album = album
        self.uniqueid = uniqueid
x = testing("title1", "author1", "F:/", "F:/thumbnails", "album1", "12381273")
listwtuple = [("title1", "author1","f:/downloads", "f:/downloads/thumbnail", "album1", "123" ),
              ("title2", "author2","f:/downloads", "f:/downloads/thumbnail", "album2", "456" )]
attempt = []
for item in listwtuple:
    obj_name = (item[0] + " - " + item[1])
    print(obj_name)
    attempt.append(obj_name)
    obj_name = testing(item[0], item[1], item[2], item[3], item[4], item[5])
    attempt.append(obj_name)



print(attempt)
'''