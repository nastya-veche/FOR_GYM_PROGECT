import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Survey(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'surveys'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    birthplace = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    nationality = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    disability = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    f1 = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    f2 = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    f3 = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    f4 = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    f5 = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)