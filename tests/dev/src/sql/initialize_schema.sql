-- Creates all chatbot tables in one go

-- === USER TABLE ===
CREATE TABLE chatbot_schema.app_user (
    idappuser SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === ROLE & USER_ROLE ===
CREATE TABLE chatbot_schema.role (
    idrole SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE chatbot_schema.user_role (
    iduserrole SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES chatbot_schema.app_user(idappuser) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES chatbot_schema.role(idrole) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster role lookup
CREATE INDEX idx_user_role_user ON chatbot_schema.user_role (user_id);
CREATE INDEX idx_user_role_role ON chatbot_schema.user_role (role_id);

-- === PROJECTS ===
CREATE TABLE chatbot_schema.project (
    idproject SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL REFERENCES chatbot_schema.app_user(idappuser) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === CHATS ===
CREATE TABLE chatbot_schema.chat (
    idchat SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES chatbot_schema.app_user(idappuser),
    project_id INTEGER REFERENCES chatbot_schema.project(idproject),
    name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === MESSAGES ===
CREATE TABLE chatbot_schema.message (
    idmessage SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES chatbot_schema.chat(idchat),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === DEFAULT ROLES ===
INSERT INTO chatbot_schema.role (name) VALUES ('Admin'), ('User');
