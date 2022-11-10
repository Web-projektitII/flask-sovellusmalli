from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import Role,User

def users(count=25):
    fake = Faker(['fi_FI'])
    i = 0
    while i < count:
        u = User(email=fake.email(),
            username=fake.user_name(),
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            about_me=fake.text(),
            member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

