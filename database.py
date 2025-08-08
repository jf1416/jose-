from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database setup
engine = create_engine('sqlite:///crm.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(50))
    status = Column(String(20))
    created_at = Column(DateTime)
    last_activity = Column(DateTime)

    comments = relationship('Comment', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return (
            f"<User(id={self.id}, name='{self.name}', email='{self.email}', phone='{self.phone}', "
            f"status='{self.status}', created_at={self.created_at}, last_activity={self.last_activity})>"
        )

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'))
    text = Column(String)
    timestamp = Column(DateTime)
    author = Column(String)

    user = relationship('User', back_populates='comments')

    def __repr__(self):
        return (
            f"<Comment(id={self.id}, user_id='{self.user_id}', author='{self.author}', "
            f"timestamp={self.timestamp}, text='{self.text}')>"
        )

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
    print('Tables created successfully.')
