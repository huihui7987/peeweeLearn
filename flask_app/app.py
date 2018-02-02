#-*- coding:utf-8 -*-
from peewee import *
from datetime import date
import datetime

from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
from functools import wraps
from hashlib import md5
from peewee import *
#config

DATABASE = 'ftweepee.db'
DEBUG = True
SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'

app = Flask(__name__)
app.config.from_object(__name__)


database = SqliteDatabase(DATABASE,threadlocals=True)

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    username = CharField()
    password = CharField()
    email = CharField()

    join_date = DateTimeField()

    def following(self):
        return (User.select().join(Relationship,on=Relationship.to_user)
                .where(Relationship.from_user == self))
    def follower(self):
        return (User.select().join(Relationship,on=Relationship.from_user)
                .where(Relationship.to_user == self))

    def is_following(self,user):
        return (User.select()
                .where(
                (Relationship.from_user == self) &
                (Relationship.to_user == user))
                .exists()
                )

    class Meta:
        order_by = ('username',)


class Relationship(BaseModel):
    from_user = ForeignKeyField(User,related_name='relationships')
    to_user = ForeignKeyField(User,related_name='related_to')

    class Meta:
        indexes = (
            (('from_user','to_user'),True),
        )

class Message(BaseModel):
    user = ForeignKeyField(User)
    content = TextField()
    pub_date = DateTimeField()

    class Meta:
        order_by = ('-pub_date')


def create_table():
    database.connect()
    database.create_tables([User,Relationship,Message],True)

def auth_user(user):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username
    flash('You are logged in as %s' % (user.username))

def get_current_user():
    if session.get('logged_in'):
        return User.get(User.id == session['user_id'])


@app.before_request
def before_request():
    database.connect()

@app.after_request
def after_request(response):
    database.close()
    return response