from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
SCHEMA = "chatbot_schema"

class AppUser(db.Model):
    __tablename__ = "app_user"
    __table_args__ = {"schema": SCHEMA}
    idappuser = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    chats = db.relationship('Chat', backref='app_user', lazy=True)


class Project(db.Model):
    __tablename__ = "project"
    __table_args__ = {"schema": SCHEMA}
    idproject = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    chats = db.relationship('Chat', backref='project', lazy=True)


class Chat(db.Model):
    __tablename__ = "chat"
    __table_args__ = {"schema": SCHEMA}
    idchat = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.app_user.idappuser"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.project.idproject"), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    messages = db.relationship('Message', backref='chat', lazy=True)


class Message(db.Model):
    __tablename__ = "message"
    __table_args__ = {"schema": SCHEMA}
    idmessage = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.chat.idchat"), nullable=False)
    sender = db.Column(db.String(10))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
