-- 1. Check Database-Level Privileges
SELECT datname, unnest(datacl)::text 
FROM pg_database 
WHERE datname = 'chatbot_db';

-- 2. Check Database Ownership
SELECT datname, pg_database.datdba::regrole AS owner 
FROM pg_database 
WHERE datname = 'chatbot_db';

-- 3. Check Schema-Level Privileges (public)
SELECT nspname, unnest(nspacl)::text 
FROM pg_namespace 
WHERE nspname = 'public';

-- 4. Check Schema Ownership (public)
SELECT schema_name, schema_owner 
FROM information_schema.schemata 
WHERE schema_name = 'public';

-- 5. Check Table Privileges
SELECT grantee, table_schema, table_name, privilege_type 
FROM information_schema.role_table_grants 
WHERE grantee = 'chatbot_user';

-- 6. Correct Sequence Privilege Check (PostgreSQL 16)
SELECT n.nspname AS schema_name, 
       c.relname AS sequence_name, 
       c.relkind, 
       c.relowner::regrole
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'S';

-- 7. Check Role-Level Permissions
SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolcanlogin 
FROM pg_roles 
WHERE rolname = 'chatbot_user';

-- 8. Check chatbot_user Has Required Schema Privileges on chatbot_schema
SELECT has_schema_privilege('chatbot_user', 'chatbot_schema', 'USAGE');
SELECT has_schema_privilege('chatbot_user', 'chatbot_schema', 'CREATE');

-- 9. Verify chatbot_schema Privileges
SELECT nspname, unnest(nspacl)::text 
FROM pg_namespace 
WHERE nspname = 'chatbot_schema';

-- 10. Check Current User (to be run inside Python or manually if needed)
SELECT current_user;

-- 11. List All Roles
SELECT rolname, rolsuper, rolcreatedb, rolcanlogin FROM pg_roles;

-- 12. List Available Databases
SELECT datname FROM pg_database WHERE datistemplate = false;

-- 13. List Tables in 'public' Schema
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
