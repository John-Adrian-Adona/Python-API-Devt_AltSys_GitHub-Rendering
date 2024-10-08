from db import db

class BooksTags(db.Model):
    __tablename__ = "books_tags"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)