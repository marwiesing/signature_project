-- Creates schema and assigns required privileges

CREATE SCHEMA IF NOT EXISTS chatbot_schema;

GRANT ALL ON SCHEMA chatbot_schema TO chatbot_user;
GRANT CREATE, USAGE ON SCHEMA chatbot_schema TO chatbot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA chatbot_schema TO chatbot_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA chatbot_schema GRANT ALL ON TABLES TO chatbot_user;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA chatbot_schema TO chatbot_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA chatbot_schema GRANT ALL ON SEQUENCES TO chatbot_user;
