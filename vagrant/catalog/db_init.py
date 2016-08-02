# (re)Initialize database with categories.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import *

engine = create_engine('sqlite:///catalog.db')
DBSession = sessionmaker(bind = engine)
session = DBSession()

session.query(Category).delete()
session.query(Item).delete()

session.add_all([Category(name = "Soccer"),
    Category(name = "Basketball"),
    Category(name = "Baseball"),
    Category(name = "Snowboarding"),
    Category(name = "Football"),
    Category(name = "Hockey")])
session.commit()

print "Reset database and added categories."
