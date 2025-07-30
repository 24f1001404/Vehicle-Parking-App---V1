import os

class config:
    BASE_PATH = os.path.abspath( os.path.dirname( __file__ ) )
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.abspath( os.path.join( BASE_PATH , "../models/app.sqlite3" ) )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    