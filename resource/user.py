from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token

from db import db
from blocklist import BLOCKLIST
from models.user import UserModel
from my_schemas import UserSchema
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("users", __name__, description="Operations on users endpoint.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        # GET JTI
        jwt = get_jwt()
        jti = jwt["jti"]

        # Add the JTI to the blocklist
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}, 200

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, req_body):
        user = UserModel.query.filter(
            UserModel.username == req_body["username"]
        ).first()

        if user:
            if pbkdf2_sha256.verify(req_body["password"], user.password):

                ## Claim 
                if user.id == 1:
                    claim = {
                        "admin": True
                    }
                    access_token = create_access_token(identity=user.id, additional_claims=claim, fresh=True)
                    refresh_token = create_refresh_token(identity=user.id, additional_claims=claim)
                else:
                    access_token = create_access_token(identity=user.id, fresh=True)
                    refresh_token = create_refresh_token(identity=user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}
            else:
                abort(400, message="Wrong password.")
        else:
            abort(400, message="User does not exist yet.")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        jwt = get_jwt()
        user_id = jwt["sub"]

        # New token
        if jwt.get("admin") == True:
            access_token = create_access_token(identity=user_id, additional_claims={"admin": True}, fresh=False)
        else:
            access_token = create_access_token(identity=user_id, fresh=False)

        return {"access_token": access_token}

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_req_body):
        if UserModel.query.filter(UserModel.username == user_req_body["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username=user_req_body["username"], 
            password=pbkdf2_sha256.hash(user_req_body["password"])
        )
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while creating a new user.")
        
        return {"message": "User registered successfully."}, 201

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted"}, 200
    
@blp.route("/my-info")
class UserInfo(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        user = UserModel.query.get_or_404(get_jwt()["sub"])
        return user


# LOGIN -> JWT -> Identity/Subject 
# ID FROM JWT
# facebook.com/home

'Login Access Toekn Attempt'
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyODIwOTc2NCwianRpIjoiMjNkN2IwNWEtNGUxMS00M2RjLTkzMDYtODkyMTM1ZTQ0MmYzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzI4MjA5NzY0LCJjc3JmIjoiZWJiMWY2MjItNWZkYi00MjA3LWFlYjUtYzFhN2Y5NGM0YjlmIiwiZXhwIjoxNzI4MjEwNjY0fQ.9L0pF5o_810NbIF41LWDjCpoPl_lHRNR2wq9bBmhCfg"