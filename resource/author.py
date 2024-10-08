from flask.views import MethodView
from flask_smorest import Blueprint, abort
from uuid import uuid4
from my_schemas import AuthorSchema
from flask_jwt_extended import jwt_required
#
from db import db
from models.book import BookModel
from models.author import AuthorModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


# Blueprint (Authors)
blp = Blueprint("authors", __name__, description="Book Database System.")

@blp.route("/authors/<int:author_id>")
class AuthorDesc(MethodView):
    @blp.response(200, AuthorSchema)
    def get(self, author_id):
        author = AuthorModel.query.get_or_404(author_id)
        return author
    
    @jwt_required()
    def delete(self, author_id):
        author = AuthorModel.query.get_or_404(author_id)

        db.session.delete(author)
        db.session.commit()

        return {"message": "Author Deleted."}, 200
    
@blp.route("/authors")
class AuthorList(MethodView):
    @blp.response(200, AuthorSchema(many=True))
    def get(self):
        return AuthorModel.query.all()
    
    @jwt_required()
    @blp.arguments(AuthorSchema)
    @blp.response(201, AuthorSchema)
    def post(self, new_author_info):
        author = AuthorModel(
            name=new_author_info["name"]
        )

        try:
            db.session.add(author)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while adding the author.")
        except IntegrityError:
            abort(400, message="Author name already exists.")
    
        return author
