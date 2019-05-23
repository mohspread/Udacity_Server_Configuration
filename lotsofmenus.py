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

menuItem2 = MenuItem(user_id=1, name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                    category=category1)

session.add(menuItem2)
session.commit()


menuItem1 = MenuItem(user_id=1, name="French Fries", description="with garlic and parmesan",category=category1)

session.add(menuItem1)
session.commit()

menuItem2 = MenuItem(user_id=1, name="Chicken Burger", description="Juicy grilled chicken patty with tomato mayo and lettuce",category=category1)

session.add(menuItem2)
session.commit()

menuItem3 = MenuItem(user_id=1, name="Chocolate Cake", description="fresh baked and served with ice cream",
                     category=category1)

session.add(menuItem3)
session.commit()

menuItem4 = MenuItem(user_id=1, name="Sirloin Burger", description="Made with grade A beef",
                    category=category1)

session.add(menuItem4)
session.commit()

menuItem5 = MenuItem(user_id=1, name="Root Beer", description="16oz of refreshing goodness",
                    category=category1)

session.add(menuItem5)
session.commit()

menuItem6 = MenuItem(user_id=1, name="Iced Tea", description="with Lemon",
                    category=category1)

session.add(menuItem6)
session.commit()

menuItem7 = MenuItem(user_id=1, name="Grilled Cheese Sandwich",
                     description="On texas toast with American Cheese", category=category1)

session.add(menuItem7)
session.commit()

menuItem8 = MenuItem(user_id=1, name="Veggie Burger", description="Made with freshest of ingredients and home grown spices",
                    category=category1)

session.add(menuItem8)
session.commit()

print "added menu items!"
