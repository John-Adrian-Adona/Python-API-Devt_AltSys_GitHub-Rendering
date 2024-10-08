from db import db

class BookModel(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)    

    book_title = db.Column(db.String(80), nullable=False, unique=True)

    genre = db.Column(db.String(80))
    
    published_year = db.Column(db.Integer)

    description = db.Column(db.String(250), nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), unique=False, nullable=False)

    author = db.relationship("AuthorModel", back_populates="books")

    tags = db.relationship("TagModel", back_populates="books", secondary="books_tags")
