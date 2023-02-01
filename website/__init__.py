from flask import Flask

UPLOAD_FOLDER = 'website/static/uploads/'

def create_app():

    app=Flask(__name__)
    #app.config['SECRET KEY']="asas"
    app.secret_key = "secret key"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 120 * 1024 * 1024


    from .views import views

    app.register_blueprint(views, url_prefix='/')
    

    return app