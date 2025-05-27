-- === USERS ===
CREATE TABLE chatbot_schema.app_user (
    idAppUser SERIAL PRIMARY KEY,
    txUsername VARCHAR(50) UNIQUE NOT NULL,
    txEmail VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === ROLES ===
CREATE TABLE chatbot_schema.role (
    idRole SERIAL PRIMARY KEY,
    txName VARCHAR(50) UNIQUE NOT NULL,
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === USER_ROLE ===
CREATE TABLE chatbot_schema.user_role (
    idUserRole SERIAL PRIMARY KEY,
    idAppUser INTEGER NOT NULL REFERENCES chatbot_schema.app_user(idAppUser) ON DELETE CASCADE,
    idRole INTEGER NOT NULL REFERENCES chatbot_schema.role(idRole) ON DELETE CASCADE,
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === DEFAULT ROLES ===
INSERT INTO chatbot_schema.role (txName) VALUES ('Admin'), ('User');

-- === PROJECTS ===
CREATE TABLE chatbot_schema.project (
    idProject SERIAL PRIMARY KEY,
    txName VARCHAR(100) UNIQUE NOT NULL,
    txDescription TEXT,
    idAppUser INTEGER NOT NULL REFERENCES chatbot_schema.app_user(idAppUser) ON DELETE CASCADE,
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === LLM MODELS ===
CREATE TABLE chatbot_schema.llm (
    idLLM SERIAL PRIMARY KEY,
    txName VARCHAR(100) UNIQUE NOT NULL,
    txShortName VARCHAR(50) UNIQUE NOT NULL,
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO chatbot_schema.llm (txName, txShortName) VALUES ('deepseek-r1', 'R1'), ('deepseek-coder', 'Coder');


-- === CHATS ===
CREATE TABLE chatbot_schema.chat (
    idChat SERIAL PRIMARY KEY,
    idAppUser INTEGER NOT NULL REFERENCES chatbot_schema.app_user(idAppUser),
    idProject INTEGER REFERENCES chatbot_schema.project(idProject) ON DELETE CASCADE,
    idLLM INTEGER NOT NULL REFERENCES chatbot_schema.llm(idLLM) ON DELETE RESTRICT,
    txName VARCHAR(100),
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === MESSAGES ===
CREATE TABLE chatbot_schema.message (
    idMessage SERIAL PRIMARY KEY,
    idChat INTEGER NOT NULL REFERENCES chatbot_schema.chat(idChat) ON DELETE CASCADE,
    idLLM INTEGER REFERENCES chatbot_schema.llm(idLLM) ON DELETE RESTRICT,
    txContent TEXT NOT NULL,
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- === RESPONSES ===
CREATE TABLE chatbot_schema.response (
    idResponse SERIAL PRIMARY KEY,
    idChat INTEGER NOT NULL REFERENCES chatbot_schema.chat(idChat) ON DELETE CASCADE,
    idMessage INTEGER NOT NULL REFERENCES chatbot_schema.message(idMessage) ON DELETE CASCADE,
    idLLM INTEGER NOT NULL REFERENCES chatbot_schema.llm(idLLM) ON DELETE RESTRICT,
    txContent TEXT NOT NULL,
    txMarkdown TEXT NOT NULL,
    dtCreated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    idAnswer INTEGER DEFAULT 0
);

-- === INDEXES ===

-- User Role Lookup
CREATE INDEX idx_user_role_user ON chatbot_schema.user_role (idAppUser);
CREATE INDEX idx_user_role_role ON chatbot_schema.user_role (idRole);

-- Project Access
CREATE INDEX idx_project_user ON chatbot_schema.project (idAppUser);

-- Chat Access
CREATE INDEX idx_chat_user ON chatbot_schema.chat (idAppUser);
CREATE INDEX idx_chat_project ON chatbot_schema.chat (idProject);
CREATE INDEX idx_chat_llm ON chatbot_schema.chat (idLLM);

-- Messages
CREATE INDEX idx_message_chat ON chatbot_schema.message (idChat);
CREATE INDEX idx_message_timestamp ON chatbot_schema.message (dtCreated);

-- Responses
CREATE INDEX idx_response_chat ON chatbot_schema.response (idChat);
CREATE INDEX idx_response_message ON chatbot_schema.response (idMessage);
CREATE INDEX idx_response_llm ON chatbot_schema.response (idLLM);
CREATE INDEX idx_response_timestamp ON chatbot_schema.response (dtCreated);