import datetime

from flask import current_app
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Table, event
from sqlalchemy.orm import relationship, backref

from project import db
from flask_security import UserMixin, RoleMixin
from flask_admin.contrib import sqla
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields

association = db.Table('association',
    db.Column('question_id', db.Integer, ForeignKey('question.id')),
    db.Column('user_id', db.Integer, ForeignKey('user.id'))
)

class Book(db.Model):

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean(), default=False, nullable=False)

    def __init__(self, title, author, read):
        self.title = title
        self.author = author
        self.read = read

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'read': self.read
        }

class User(UserMixin, db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    minimum_price = db.Column(db.Integer)
    followers = db.Column(db.Integer)
    snippet = db.Column(db.String(120))
    cover_photo = db.Column(db.String(120), unique=True)
    profile_photo = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    date = db.Column(db.DateTime, default=datetime.utcnow())

    # active = db.Column(db.Boolean())
    # confirmed_at = db.Column(db.DateTime())
    #
    # roles = db.relationship('Role', secondary=roles_users,
    #                         backref=db.backref('users', lazy='dynamic'))

    questions = db.relationship('Question',
                secondary=association,
                backref="users")
    # likes = relationship("Like", back_populates="user")
    activity = relationship("Activity", back_populates="actor")
    # bounty = relationship("Bounty", back_populates="user")

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.followers = 0
        self.minimum_price = 0
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {0}>'.format(self.email)

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asker_id = db.Column(db.Integer, ForeignKey('user.id'))
    responder_id = db.Column(db.Integer, ForeignKey('user.id'))
    state = db.Column(db.String(20))
    text = db.Column(db.Text)
    num_likes = db.Column(db.Integer)
    question_link = db.Column(db.String(256))
    date = db.Column(db.DateTime, default=datetime.utcnow())
    question_thumbnail = db.Column(db.String(256))

    activity = relationship("Activity", back_populates="question")

    def __init__(self, asker_id, responder_id, text, question_link):
        self.asker_id = asker_id
        self.responder_id = responder_id
        self.text = text
        self.state = "Unanswered"
        self.num_likes = 0
        self.question_link = question_link

    def __repr__(self):
        return '<Question %r>' % self.id

class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity':'activity',
        'polymorphic_on':type
    }

    question_id = db.Column(db.Integer, ForeignKey('question.id'))
    tbn = db.Column(db.Integer)
    actor_id = db.Column(db.Integer, ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow())

    question = relationship("Question", back_populates="activity")
    actor = relationship("User", back_populates="activity")

    def __init__(self, tbn, actor_id, question_id):
        self.tbn = tbn
        self.actor_id = actor_id
        self.question_id = question_id

class Answer(Activity):
    __tablename__ = 'answer'
    __mapper_args__ = {'polymorphic_identity': 'answer'}
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)
    answer_link = db.Column(db.String(256))
    answer_thumbnail = db.Column(db.String(256))

    def __init__(self, tbn, actor_id, question_id):
        super(Answer, self).__init__(tbn, actor_id, question_id)

    def __repr__(self):
        return '<Answer %r>' % self.id

class Like(Activity):
    __tablename__ = 'like'
    __mapper_args__ = {'polymorphic_identity':'like'}
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)

    def __init__(self, tbn, actor_id, question_id):
        super(Like, self).__init__(tbn, actor_id, question_id)

    def __repr__(self):
        return '<Like %r>' % self.id

class Bounty(Activity):
    __tablename__ = 'bounty'
    __mapper_args__ = {'polymorphic_identity':'bounty'}
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)

    def __init__(self, tbn, actor_id, question_id):
        super(Bounty, self).__init__(tbn, actor_id, question_id)

    def __repr__(self):
        return '<Bounty %r>' % self.id

class Follow(Activity):
    __tablename__ = 'follow'
    __mapper_args__ = {'polymorphic_identity':'follow'}
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)

    def __init__(self, tbn, actor_id, question_id):
        super(Follow, self).__init__(tbn, actor_id, question_id)

    def __repr__(self):
        return '<Follow %r>' % self.id

class View(Activity):
    __tablename__ = 'view'
    __mapper_args__ = {'polymorphic_identity':'view'}
    id = db.Column(db.Integer, db.ForeignKey('activity.id'), primary_key=True)

    def __init__(self, tbn, actor_id, question_id):
        super(View, self).__init__(tbn, actor_id, question_id)

    def __repr__(self):
        return '<View %r>' % self.id

# import flask_admin as admin
# from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters, ModelView

# Customized User model admin
class UserAdmin(sqla.ModelView):
    column_display_pk = True
    column_exclude_list = ['password_hash', 'cover_photo']

class QuestionAdmin(sqla.ModelView):
    column_display_pk = True
    can_delete = False

class AnswerAdmin(sqla.ModelView):
    column_display_pk = True
    can_delete = False

################################
####        EVENTS          ####
################################

###    USER_EVENTS     ###
# @event.listens_for(User, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     activity_table = Activity.__table__
#     connection.execute(
#         activity_table.insert().
#             values(actor_id=target.id,
#                 activity_type='User')
#     )
#
# ###    BOUNTY_EVENTS     ###
# @event.listens_for(Bounty, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     activity_table = Activity.__table__
#     connection.execute(
#         activity_table.insert().
#             values(actor_id=target.user_id,
#                 activity_type='Bounty')
#     )

###     QUESTION_EVENTS     ###
# @event.listens_for(Question, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     activity_table = Activity.__table__
#     connection.execute(
#         activity_table.insert().
#             values(to_be_notified=target.responder_id,
#                 actor=target.asker_id,
#                 question_id=target.id,
#                 activity_type='Question_Added')
#     )

### FOLLOW EVENTS ####

# NEW FOLLOWER #
# - increments followed user's follower count
# @event.listens_for(Follow, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     user_table = User.__table__
#     connection.execute(
#         user_table.update().
#             where(user_table.c.id == target.followed_id).
#             values(followers=user_table.c.followers + 1)
#     )
#     activity_table = Activity.__table__
#     connection.execute(
#         activity_table.insert().
#             values(actor_id=target.follower_id,
#                 to_be_notified=target.followed_id,
#                 activity_type='Follow')
#     )

# UNFOLLOW  #
# - decrements unfollowed user's follower count
# @event.listens_for(Follow, 'before_delete')
# def receive_before_delete(mapper, connection, target):
#     user = db.session.query(User).get(followed_id)
#     num_followers = user.followers
#     user.followers = num_followers - 1
#     db.session.commit()

###     ANSWER EVENTS   ###
# @event.listens_for(Answer, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     activity_table = Activity.__table__
#     connection.execute(
#         activity_table.insert().
#             values(to_be_notified=target.question.asker_id,
#                 actor=target.question.responder_id,
#                 question_id=target.question_id,
#                 activity_type='Answer_Added')
#     )

###     LIKE EVENTS   ###
# @event.listens_for(Like, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     question_table = Question.__table__
#     connection.execute(
#         question_table.update().
#             where(question_table.c.id == target.question_id).
#             values(num_likes=question_table.c.num_likes + 1)
#     )

################################
####        SCHEMAS         ####
################################

class UserProfileSchema(Schema):
    id = fields.Integer(dump_only=True)
    profile_photo = fields.String()
    cover_photo = fields.String()
    name = fields.Method("full_name")
    followers = fields.Integer(attributes='followers')
    minimum_price = fields.Integer(dump_only=True)
    snippet = fields.String()

    def full_name(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

class UserMiniSchema(Schema):
    id = fields.Integer(dump_only=True)
    profile_photo = fields.String()
    name = fields.Method("full_name")
    def full_name(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

class UserExploreSchema(Schema):
    id = fields.Integer(dump_only=True)
    profile_photo = fields.String()
    cover_photo = fields.String()
    name = fields.Method("full_name")
    snippet = fields.String()

    def full_name(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Method("full_name")
    def full_name(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

# # Used when getting questions asked by user
# class QuestionsAskedByUserSchema(Schema):
#     id = fields.Integer(dump_only=True)
#     responder_id = fields.Integer(dump_only=True)
#     text = fields.String()
#
class QuestionSchema(Schema):
    id = fields.Integer(dump_only=True)
    text = fields.String()
    question_link = fields.String()
    num_likes = fields.Integer(dump_only=True)
    asker = fields.Method("get_asker")
    responder = fields.Method("get_responder")
    def get_asker(self, obj):
        return UserMiniSchema().dump(User.query.get(obj.asker_id))[0]

    def get_responder(self, obj):
        return UserMiniSchema().dump(User.query.get(obj.responder_id))[0]

class QuestionVCSchema(Schema):
    id = fields.Integer(dump_only=True)
    text = fields.String()
    asker = fields.Method("get_asker")
    def get_asker(self, obj):
        return UserMiniSchema().dump(User.query.get(obj.asker_id))[0]

class AnswerSchema(Schema):
    # answer_link = fields.String()
    answer_thumbnail = fields.String()

class QuestionAnswerSchema(Schema):
    text = fields.String()
    num_likes = fields.Integer(dump_only=True)
    question_link = fields.String()
    answer = fields.Nested(AnswerSchema())
    asker = fields.Method("get_asker")
    responder = fields.Method("get_responder")
    def get_asker(self, obj):
        return UserMiniSchema().dump(User.query.get(obj.asker_id))[0]

    def get_responder(self, obj):
        return UserMiniSchema().dump(User.query.get(obj.responder_id))[0]

class QuestionMiniSchema(Schema):
    id = fields.Integer(dump_only=True)
    text = fields.String()

class FollowSchema(Schema):
    follower_id = fields.Integer(dump_only=True)
    followed_id = fields.Integer(dump_only=True)

class ActivitySchema(Schema):
    actor = fields.Nested(UserMiniSchema())
    type = fields.String(dump_only=True)

class MixedActivitySchema(Schema):
    actor = fields.Nested(UserMiniSchema())
    question = fields.Nested(QuestionMiniSchema())
    type = fields.String(dump_only=True)
