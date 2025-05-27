# starting of the app
from flask import Flask
from backend.models import db
from flask_login import LoginManager

app=None
login_manager = None
def setup_app():
    global app, login_manager
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///vehicle_parking.sqlite3" # having db file
    app.config["SECRET_KEY"] = "my-secret-key"
    db.init_app(app) # flask app connected to db(SQL alchemy)
    app.app_context().push()# direct access to other modules
    app.debug=True

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "signin"  
    login_manager.init_app(app)

    # Define user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    print("Vehicle parking app is started...")

# call the setup
setup_app()


from backend.controllers import *


if __name__ == "__main__":
    app.run()