from db import db

class AuthorModel(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    books = db.relationship("BookModel", back_populates="author", lazy="dynamic", cascade="all, delete")

    tags = db.relationship("TagModel", back_populates="author")