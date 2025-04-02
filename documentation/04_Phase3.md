# **Phase 3: Creating the Website**

### 🎯 **Goal:**
Transform your minimal functional Flask app into a polished, full-featured web application — styled with Bootstrap 5, connected to PostgreSQL (via raw SQL), and fully managed through GitLab CI/CD and ArgoCD in your Kubernetes cluster.

---

## 🧱 **Current Status**
✔️ Basic site running in Kubernetes  
✔️ Flask connected to PostgreSQL  
✔️ GitLab CI/CD builds & pushes Docker image  
✔️ ArgoCD deploys the app  
✔️ Minimal HTML (`index.html`) in place  
✔️ App structure copied from production for offline development

---

## 🗺️ **Phase 3 Roadmap**

### 🔹 Step 1: **Project Structure & Cleanup**
- Refactor the current `src/` layout to be modular and scalable
- Clean up unused files (e.g. `models.py` if switching to raw SQL)
- Separate routes into logical groups (`auth`, `main`, `admin`, `chat`)
- Create `db_utils.py` for clean SQL interaction using `psycopg2`

### 🔹 Step 2: **Database Design**
- Convert SQLAlchemy models to real PostgreSQL schema
- Write `create_schema.sql` + `initialize_schema.sql`
- Add helpers for `SELECT`, `INSERT`, `UPDATE`, etc.
- Replace ORM with raw queries throughout your routes

### 🔹 Step 3: **User System**
- Create working register/login/logout routes using raw SQL
- Use `Flask-Login` for session/auth management
- Create admin flag + restricted views
- Add flash messages for feedback (e.g. “Login failed”, “User created”)

### 🔹 Step 4: **Base HTML + Styling**
- Build `base.html` with Bootstrap 5: header, footer, flash message block
- Add navigation links based on user role (e.g. show Admin only for admins)
- Create placeholder pages: `login.html`, `register.html`, `main.html`, etc.

### 🔹 Step 5: **Admin Panel**
- List all users, promote/delete/edit as admin
- View per-user chat/posts if needed
- Protect with route guards and role checks

### 🔹 Step 6: **Chat Integration**
- Create a `chat.html` page with:
  - Message input
  - Scrollable message history
  - Route that sends messages to Ollama (POST/streaming)
- Store chat history in DB (PostgreSQL)

### 🔹 Step 7: **CI/CD & ArgoCD Polishing**
- Create production-ready Docker image
- Adjust entrypoint if needed (`gunicorn`, `wait-for-it`, etc.)
- Test full pipeline: code → GitLab → ArgoCD → cluster
- Add health probes, `revisionHistoryLimit`, etc.

---

## ✅ **Phase 3: Checklist**

| Task                                                                 | Status |
|----------------------------------------------------------------------|--------|
| ✅ Clean dev structure (`src`, `04_main.py`, etc.)                   | ✅ Done |
| ✅ Create `db_utils.py` for raw SQL helpers                          | ✅ Done |
| ⬜️ Convert `register/login` to use raw SQL (`db.execute_query`)      | 🔜 Next |
| ✅ Write final `create_schema.sql` + `initialize_schema.sql`         | ✅ Done |
| ⬜️ Implement user session & role logic (`is_admin`)                 | 🔜 Next |
| ⬜️ Build `base.html` with Bootstrap header/footer                   | ⬜️ Todo |
| ⬜️ Create templates for `login.html`, `register.html`, `main.html`  | ⬜️ Todo |
| ⬜️ Add admin panel: list, edit, delete users                        | ⬜️ Todo |
| ⬜️ Implement chat UI (`chat.html`) + connect to Ollama              | ⬜️ Todo |
| ✅ Store chat messages in Postgres                                  | ✅ Done |
| ⬜️ Polish Dockerfile for production deployment                      | ⬜️ Todo |
| ⬜️ Confirm CI/CD pipeline auto-deploys updated app via ArgoCD       | ⬜️ Todo |

---

## 📍 **Current Status:**

✔️ **Database layer**: ✅ Fully working  
✔️ **Postgres connection class**: ✅ Clean + flexible  
✔️ **SQL file execution**: ✅ Robust + tested  
✔️ **Basic site rendering**: ✅ Flask loads, can post messages  
✔️ **RBAC schema**: ✅ Designed + patchable  
✔️ **Dev structure**: ✅ Modular and scalable

---
