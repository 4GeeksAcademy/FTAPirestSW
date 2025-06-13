import os
from flask_admin import Admin
#en la sguiente lina importamos modelos 
from models import db, Person, Favorite, Character, Planet, Vehicle
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    
    # Add your models here, for example this is how we add a the User model to the admin
    #migracion de modelos
    admin.add_view(ModelView(Person, db.session))
    admin.add_view(ModelView(Favorite, db.session))
    admin.add_view(ModelView(Character, db.session))
    admin.add_view(ModelView(Vehicle, db.session))
    admin.add_view(ModelView(Planet, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))