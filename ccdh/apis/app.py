from flask import Flask

from ccdh.apis.api import api
from ccdh.apis.schemas import ma

app = Flask(__name__)
api.init_app(app)
ma.init_app(app)

if __name__ == '__main__':
    app.run()
