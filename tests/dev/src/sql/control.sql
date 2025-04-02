SELECT a.username, r.name 
FROM chatbot_schema.app_user a
JOIN chatbot_schema.user_role ur ON ur.user_id = a.idappuser
JOIN chatbot_schema.role r ON ur.role_id = r.idrole;
