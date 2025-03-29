-- Schema: chatbot_schema

--- #  psql -h $PSQL_HOST -U $PSQL_USER -d $PSQL_DB -f src/sql/initialize_schema.sql  -W

CREATE TABLE chatbot_schema.app_user (
    idappuser SERIAL NOT NULL, 
    username VARCHAR(50) NOT NULL, 
    password VARCHAR(50) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (idappuser), 
    UNIQUE (username)
);

CREATE TABLE chatbot_schema.project (
    idproject SERIAL NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    description TEXT, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (idproject), 
    UNIQUE (name)
);

CREATE TABLE chatbot_schema.chat (
    idchat SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    project_id INTEGER, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (idchat), 
    FOREIGN KEY(project_id) REFERENCES chatbot_schema.project (idproject), 
    FOREIGN KEY(user_id) REFERENCES chatbot_schema.app_user (idappuser)
);

CREATE TABLE chatbot_schema.message (
    idmessage SERIAL NOT NULL, 
    chat_id INTEGER NOT NULL, 
    sender VARCHAR(10), 
    content TEXT NOT NULL, 
    timestamp TIMESTAMP WITHOUT TIME ZONE, 
    PRIMARY KEY (idmessage), 
    FOREIGN KEY(chat_id) REFERENCES chatbot_schema.chat (idchat)
);
