from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_caching import Cache



app = Flask(__name__)
cors = CORS(app)
app.config['SECRET_KEY'] = "e3b7c7bb09ba4de899b127b43ac9a4a7"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = "redis://localhost:6379/0"


db = SQLAlchemy(app)
bcrypt = Bcrypt()
cache = Cache(app)




from OGS import routes