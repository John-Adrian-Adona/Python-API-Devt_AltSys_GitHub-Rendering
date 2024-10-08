from marshmallow import Schema, fields

class NormalAuthorSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)

class NormalBookSchema(Schema):
    book_id = fields.Integer(dump_only=True)
    book_title = fields.Str(required=True)
    genre = fields.Str(required=True)
    published_year = fields.Integer(required=True)
    description = fields.Str(required=True)

class NormalTagSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)

class BookUpdateSchema(Schema):
    book_id = fields.Integer(dump_only=True)
    book_title = fields.Str()
    genre = fields.Str()
    published_year = fields.Integer()

    author_id = fields.Integer()

class AuthorSchema(NormalAuthorSchema):
    books = fields.List(fields.Nested(NormalBookSchema), dump_only=True)
    tags = fields.List(fields.Nested(NormalTagSchema), dump_only=True)

class BookSchema(NormalBookSchema):
    author_id = fields.Int(required=True)
    author = fields.Nested(NormalAuthorSchema, dump_only=True)
    tags = fields.List(fields.Nested(NormalTagSchema), dump_only=True)


class TagSchema(NormalTagSchema):
    author_id = fields.Int(load_only=True)
    author = fields.Nested(NormalBookSchema, dump_only=True)
    books = fields.List(fields.Nested(NormalBookSchema), dump_only=True)


class TagAndBookSchema(Schema):
    message = fields.Str()
    book = fields.Nested(BookSchema)
    tag = fields.Nested(TagSchema)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)