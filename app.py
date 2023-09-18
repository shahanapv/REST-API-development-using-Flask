from flask import Flask,jsonify
from flask_smorest import Api
from resources.item import blp as ItemBluePrint
from resources.store import blp as StoreBluePrint
from resources.tag import blp as TagBluePrint
from resources.user import blp as UserBluePrint
import secrets
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

import os
from db import db
import models
from blocklist import BLOCKLIST


def create_app(db_url=None):

    app=Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"]=db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
    db.init_app(app)

    

    migrate = Migrate(app, db)
    api=Api(app)
    app.config["JWT_SECRET_KEY"]="shahana"
    jwt=JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoke_if_token_in_blocklist(jwt_header,jwt_payload):
        return (jsonify({"message":"You are already logged out","error":"Token revoked"}),401)
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header,jwt_payload):
        return (jsonify({"descrption":"Thetoken is not fresh"}),401)

    @jwt.additional_claims_loader
    def only_admin_deletes(identity):
        if identity==1:
            return {"isadmin":True}
        return {"isadmin":False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        return (jsonify({"message":"The token has expired","error":"token expired"}),401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (jsonify({"message":"The token is invalid","error":"Invalid token"}),401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"message":"The token is missing"},401


    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBluePrint)
    return app














    
