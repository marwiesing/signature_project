from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    iduser = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    chats = db.relationship('Chat', backref='user', lazy=True)

class Project(db.Model):
    idproject = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    chats = db.relationship('Chat', backref='project', lazy=True)


class Chat(db.Model):
    idchat = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.iduser'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.idproject'), nullable=True)  # A chat can belong to a project
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    messages = db.relationship('Message', backref='chat', lazy=True)


class Message(db.Model):
    idmessage = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.idchat'), nullable=False)
    sender = db.Column(db.String(10))  # "user" or "bot"
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())    

