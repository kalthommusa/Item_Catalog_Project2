from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import WeddingVenues, Base, VenueItem, User

engine = create_engine('sqlite:///weddingvenuesappwithusers.db')
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


# Create dummy user1
User1 = User(
    name="Rehab",
    email="rehab@example.com",
    picture='https://i1.wp.com/blog.udacity.com\
    /wp-content/uploads/2016/09/VRDeveloperNanodegreeProgram.png')
session.add(User1)
session.commit()


weddingVenues1 = WeddingVenues(user_id=1, name="Movenpick", user=User1)

session.add(weddingVenues1)
session.commit()

itemDetails1_1 = VenueItem(
    user_id=1,
    location="Saudi Arabia, Riyadh, King Fahad Road,\
    opposite the Ministry of Interior",
    price="",
    contact_number="+96611457999",
    capacity="",
    picture="https://www.movenpick.com\
    /fileadmin/files/Hotels/Saudi_Arabia/Riyadh/Images/Banquest_-_Riyadh.jpg",
    weddingvenues=weddingVenues1,
    user=User1)

session.add(itemDetails1_1)
session.commit()


itemDetails2_1 = VenueItem(
    user_id=1,
    location="Saudi Arabia, Jeddah, Al-Madinah Al-Munawarah Rd,\
    adjacent to Mohammed Al-Taweel St.",
    price="",
    contact_number="+966126676655",
    capacity="",
    picture="https://www.movenpick.com\
    /fileadmin/_processed_/b/8/csm_Jeddah_xxxxxxxx_i115344_01_8c98003211.jpg",
    weddingvenues=weddingVenues1,
    user=User1)

session.add(itemDetails2_1)
session.commit()


itemDetails3_1 = VenueItem(
    user_id=1,
    location="Saudi Arabia, Al Khobar, Prince Turkey St.",
    price="",
    contact_number="+966138984999",
    capacity="",
    picture="https://www.movenpick.com\
    /fileadmin/files/Hotels/Saudi_Arabia/Al_Khobar/Meeting_Rooms\
    /Al_Maha_ballroom_485x235.JPG",
    weddingvenues=weddingVenues1,
    user=User1)

session.add(itemDetails3_1)
session.commit()


# Create dummy user2
User2 = User(
    name="Raghad",
    email="raghad@example.com",
    picture='http://www.livehoppy.com\
    /wp-content/uploads/2016/09/hoppy-computer.jpg')
session.add(User2)
session.commit()


weddingVenues2 = WeddingVenues(user_id=2, name="Sheraton", user=User2)

session.add(weddingVenues2)
session.commit()

itemDetails1_2 = VenueItem(
    user_id=2,
    location="Saudi Arabia, Dammam, 1St Street King Abdulaziz Road",
    price="",
    contact_number="+966138345555",
    capacity="",
    picture="https://www.arabiaweddings.com\
    /sites/default/files/styles/400x400/public\
    /companies/images/2016/11/sheraton-dammam-hotel.jpg",
    weddingvenues=weddingVenues2,
    user=User2)

session.add(itemDetails1_2)
session.commit()


weddingVenues3 = WeddingVenues(user_id=2, name="Majesty", user=User2)

session.add(weddingVenues3)
session.commit()


itemDetails1_3 = VenueItem(
    user_id=2,
    location="Saudi Arabia, Jeddah, Al Nuzha Dist.",
    price="60000 SAR",
    contact_number="+966509677883",
    capacity="+500",
    picture="https://www.arabiaweddings.com\
    /sites/default/files/resize/uploads/2016/11/08/majesty-500x317.png",
    weddingvenues=weddingVenues3,
    user=User2)

session.add(itemDetails1_3)
session.commit()


# Create dummy user3
User3 = User(name="Maryam", email="maryam@example.com",
             picture='https://robohash.org/udacity-1048258566.png')
session.add(User3)
session.commit()


weddingVenues4 = WeddingVenues(user_id=3, name="Alqamarain", user=User3)

session.add(weddingVenues4)
session.commit()

itemDetails1_4 = VenueItem(
    user_id=3,
    location="Saudi Arabia, Makkah, Al Zaidy St.",
    price="30000 SAR",
    contact_number="+966505771212",
    capacity="+600",
    picture="https://i.zafaf.net/providers/44561/preview_\
    qlcfkvbnexgjivbpydhtqnqfg.jpg",
    weddingvenues=weddingVenues4,
    user=User3)

session.add(itemDetails1_4)
session.commit()

print "added menu items!"
