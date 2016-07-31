from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    email = Column(String(255), nullable = False)
    picture = Column(String(255))


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    owner = Column(Integer, ForeignKey('user.id'))


class MenuItem(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False)
    description = Column(String(255))
    price = Column(String(8))
    course = Column(String(255))
    restaurant = Column(Integer, ForeignKey('restaurant.id'))


engine = create_engine('sqlite:///menu.db')
Base.metadata.create_all(engine)
