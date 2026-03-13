from app.store.database.models import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    user_code = db.Column(db.String, nullable=False)