from flask.views import MethodView
from flask_smorest import Blueprint, abort
from my_schemas import AuthorSchema, TagSchema, TagAndBookSchema

# Use SQLAlchemy
from db import db
from models.author import AuthorModel
from models.tag import TagModel
from models.book import BookModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Create a blueprint
blp = Blueprint("tags", __name__, description="Book Database System.")

@blp.route("/books/<int:book_id>/tag/<int:tag_id>")
class LinkTags(MethodView):
    def post(self, book_id, tag_id):
        book = BookModel.query.get_or_404(book_id) 
        tag = TagModel.query.get_or_404(tag_id)

        # Before linkig, we have to make sure that the book and the tag is inside of the same author
        if book.author_id != tag.author_id:
            abort(400, message="Make sure that book and tags belong to the same author before linking.")
        
        book.tags.append(tag)

        try:
            db.session.add(book)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while linking the tag and the book")
        
        return {"message": "Tag and Book are succesfully linked."}, 200

    @blp.response(200, TagAndBookSchema)
    def delete(self, book_id, tag_id):
        book = BookModel.query.get_or_404(book_id) 
        tag = TagModel.query.get_or_404(tag_id)  

        book.tags.remove(tag)

        try:
            db.session.add(book)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while unlinking the book and the tag.")

        return {"message": "Tag removed from the book", "book": book, "tag": tag}
        

@blp.route("/authors/<int:author_id>/tag")
class TagsInAuthor(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, author_id):
        author = AuthorModel.query.get_or_404(author_id)
        return author.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, req_body, author_id):
        if TagModel.query.filter(
            TagModel.author_id == author_id,
            TagModel.name == req_body["name"]
        ).first():
            abort(400, message="A tag with that name already exists in the same author.")

        # Created a new row/record
        tag = TagModel(name=req_body["name"], author_id=author_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while creating a tag.")
        
        return tag


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if tag.books:
            abort(400, message="Could not delete tag, please unlink all books to this tag before deleting.")
        
        db.session.delete(tag)
        db.session.commit()

        return {"message": "Tag Deleted"}, 200 