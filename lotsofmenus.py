from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, MenuItem, User

engine = create_engine('sqlite:///categorymenuwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

category1 = Category(user_id=1, name="Sci-Fi")

session.add(category1)
session.commit()

category2 = Category(user_id=1, name="Action")

session.add(category2)
session.commit()


category3 = Category(user_id=1, name="Romance")

session.add(category3)
session.commit()


menuItem2 = MenuItem(user_id=1, name="Avengers", description="Earth's mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity.",
                    category=category1)

session.add(menuItem2)
session.commit()


menuItem3 = MenuItem(user_id=1, name="Die Hard", description="An NYPD officer tries to save his wife and several others taken hostage by German terrorists during a Christmas party at the Nakatomi Plaza in Los Angeles.",
                     category=category2)

session.add(menuItem3)
session.commit()


menuItem5 = MenuItem(user_id=1, name="Sweet November", description="A workaholic executive, and an unconventional woman agree to a personal relationship for a short period. In this short period she changes his life.",
                    category=category3)

session.add(menuItem5)
session.commit()

print "added menu items!"
