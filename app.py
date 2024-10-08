from flask import Flask, request, jsonify
from resource.book import blp as BookBlueprint
from resource.author import blp as AuthorBlueprint
from resource.tag import blp as TagBlueprint
from resource.user import blp as UserBlueprint
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST

#
from models.book_tags import BooksTags
from models.book import BookModel
from models.author import AuthorModel
from models.tag import TagModel
from models.user import UserModel

from db import db
from flask_migrate import Migrate

# Create a web server using flask
app = Flask(__name__)

# Setup the Blueprints and the API Documentation
app.config["PROPAGATE_EXCEPTIONS"] = True

# Title that would show up in the documentation
app.config["API_TITLE"] = "Book Database Inventory"
app.config["API_VERSION"] = "v1"

# OPENAPI Setup
app.config["OPENAPI_VERSION"] = "3.1.0"
app.config["OPENAPI_URL_PREFIX"] = "/"

# Documentation Website Setup
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

# Connect flask app to the database
db.init_app(app)
migrate = Migrate(app, db)

# Create the tables based on the models
#with app.app_context():
#    db.create_all()

api = Api(app)
api.register_blueprint(BookBlueprint)
api.register_blueprint(AuthorBlueprint)
api.register_blueprint(TagBlueprint)
api.register_blueprint(UserBlueprint)

app.config["JWT_SECRET_KEY"] = "132354456734573457754335648563456"
jwt = JWTManager(app)

## Checks if every JWT that goes inside our system/api is in the blocklist
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST

# If it is in the blocklist, return this error.
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "The access token has been revoked.", 
                "error": "token_revoked"}, 401
        )
    )

# Run the flask web app
if __name__ == '__main__':
    app.run(debug=True)