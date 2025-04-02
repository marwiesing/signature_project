-- 1. ROLES TABLE
CREATE TABLE chatbot_schema.role (
    idrole SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- 2. USER_ROLE ASSOCIATION TABLE
CREATE TABLE chatbot_schema.user_role (
    iduserrole SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES chatbot_schema.app_user(idappuser) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES chatbot_schema.role(idrole) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add an index for faster joins
CREATE INDEX idx_user_role_user ON chatbot_schema.user_role (user_id);
CREATE INDEX idx_user_role_role ON chatbot_schema.user_role (role_id);


-- Alter Message table to set default timestamp
ALTER TABLE chatbot_schema.message
ALTER COLUMN timestamp SET DEFAULT current_timestamp;

-- Insert default roles
INSERT INTO chatbot_schema.role (name) VALUES ('Admin'), ('User');
INSERT INTO chatbot_schema.user_role (user_id, role_id) VALUES (1, 1);
