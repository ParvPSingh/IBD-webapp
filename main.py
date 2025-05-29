from flask import Flask
from flask_cors import CORS
from application.models import db, User, Role
from config import DevelopmentConfig
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from application.sec import datastore
from werkzeug.security import generate_password_hash

def init_database(app):
    with app.app_context():
        # Create database and tables
        db.create_all()
        
        # Create roles
        datastore.find_or_create_role(name='administrator', description='Administrator role found/created')
        datastore.find_or_create_role(name='user', description='User role found/created')
        db.session.commit()
        
        # Create default users if they don't exist
        if not datastore.find_user(email='admin@gmail.com'):
            datastore.create_user(
                name='Administrator',
                email='admin@gmail.com',
                password=generate_password_hash('admin', method='pbkdf2:sha256'),  # Changed hash method
                roles=['administrator']
            )
        
        if not datastore.find_user(email='rahul@gmail.com'):
            datastore.create_user(
                name='Rahul',
                email='rahul@gmail.com',
                password=generate_password_hash('rahul', method='pbkdf2:sha256'),  # Changed hash method
                roles=['user']
            )
        
        db.session.commit()
def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    CORS(app, resources={r"/*":{'origins': "*"}})
    #CORS(app, resources={r"/*":{'origins': 'http://127.0.0.1:8080', "allow_headers":"Access-Control-Allow-Origin"}})
    db.init_app(app)
    app.security = Security(app, datastore=datastore)
    with app.app_context():
        import application.controllers
    return app

app = create_app()
init_database(app)
user_vector_dbs = {}

if __name__ == '__main__':
    app.run(debug=True)