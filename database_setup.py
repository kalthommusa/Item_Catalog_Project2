from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class WeddingVenues(Base):
    __tablename__ = 'wedding_venues'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class VenueItem(Base):
    __tablename__ = 'venue_item'

    location = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    price = Column(String(10))
    contact_number = Column(String(15))
    capacity = Column(String(50))
    picture = Column(String(250))
    weddingvenues_id = Column(Integer, ForeignKey('wedding_venues.id'))
    weddingvenues = relationship(WeddingVenues)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return{
            'location': self.location,
            'price': self.price,
            'contact_number': self.contact_number,
            'capacity': self.capacity,
            'id': self.id,
        }


engine = create_engine('sqlite:///weddingvenuesappwithusers.db')


Base.metadata.create_all(engine)
