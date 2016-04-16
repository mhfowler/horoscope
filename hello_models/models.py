from sqlalchemy import Column, Integer, String
from hello_models.database import Base


class TestObject(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    key = Column(String(100))
    value = Column(String(100))

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<TestObject {}:{}>'.format(self.key, self.value)


class FbAlert(Base):
    __tablename__ = 'fb_alert'
    id = Column(Integer, primary_key=True)
    fb_id = Column(String(200))
    phone_number = Column(String(200))

    def __init__(self, fb_id=None, phone_number=None):
        self.fb_id = fb_id
        self.phone_number = phone_number


class KeyVal(Base):
    __tablename__ = 'keyval'
    id = Column(Integer, primary_key=True)
    key = Column(String(200))
    value = Column(String(200))

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
