from flask.views import MethodView
from flask_smorest import Blueprint, abort
from uuid import uuid4
from my_schemas import BookSchema, BookUpdateSchema
from flask_jwt_extended import jwt_required, get_jwt
#
from db import db
from models.book import BookModel
from models.author import AuthorModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


# Blueprint (Books)
blp = Blueprint("books", __name__, description="Book Database System.")

@blp.route("/books")
class BookList(MethodView):
    @blp.response(200, BookSchema(many=True))
    def get(self):
        return BookModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def post(self, new_book_info):
        book = BookModel(
            book_title = new_book_info["book_title"],
            genre = new_book_info["genre"],
            published_year = new_book_info["published_year"],
            author_id = new_book_info["author_id"]
        )
        
        try:
            db.session.add(book)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured when creating an Item.")

        return book
    

@blp.route("/books/<int:book_id>")
class Book(MethodView):
    @blp.response(200, BookSchema)
    def get(self, book_id):
        # Model.query.get() - always refer to pk
        book = BookModel.query.get_or_404(book_id)
        return book
    
    @jwt_required(refresh=True)
    def delete(self, book_id):
        jwt = get_jwt()

        try:
            if jwt["admin"] == True:
                book = BookModel.query.get(book_id)

                db.session.delete(book)
                db.session.commit()

                return {"message": "Book deleted."}, 200
        except:
            abort(400, message="You are not an admin.")

    @jwt_required(fresh=True)
    @blp.arguments(BookUpdateSchema)
    @blp.response(200, BookUpdateSchema)
    def put(self, book_info_update, book_id):
        book = BookModel.query.get(book_id)

        if book:
            book.book_title = book_info_update["book_title"]
            book.genre = book_info_update["genre"]
            book.published_year = book_info_update["genre"]
        else:
            book = BookModel(
                book_title = book_info_update["book_title"],
                genre = book_info_update["genre"],
                published_year = book_info_update["published_year"],
                author_id = book_info_update["author_id"]
            ) 

        try:
            db.session.add(book)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while editing the book.")

        return book