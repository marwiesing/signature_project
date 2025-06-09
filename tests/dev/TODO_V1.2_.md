## 🔐 Google OAuth Login

**Goal:** Let users sign in via Google, auto‐create an account (with “User” role) if their email isn’t yet in `app_user`.

### 1. Register a Google OAuth app

1. In Google Cloud Console → APIs & Services → Credentials, create an OAuth 2.0 Client ID (Web application).
2. Set the Authorized redirect URI to something like

   ```
   http://localhost:5000/login/google/authorized
   ```
3. Copy the **Client ID** and **Client Secret**.

### 2. Install and configure Flask-Dance

```bash
pip install Flask-Dance[sqla]
```

(We’ll ignore the SQLAlchemy bits and just use the OAuth flow.)

In your app’s entry‐point (e.g. `app.py`), add:

```python
from flask import Flask, redirect, url_for, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection

app = Flask(__name__)
app.secret_key = "your‐long‐random‐secret"

# Configure OAuth blueprint
google_bp = make_google_blueprint(
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    scope=["profile", "email"],
    redirect_url="/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

db = PostgresDatabaseConnection()
```

### 3. Create a “login” route

```python
@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch your Google profile.", "danger")
        return redirect("/")

    user_info = resp.json()
    email = user_info["email"]
    username = user_info.get("name", email.split("@")[0])

    # 4. Look up or create user in app_user
    result = db.read_sql_query(
        "SELECT idappuser FROM chatbot_schema.app_user WHERE txemail = %s",
        (email,)
    )
    if result:
        user_id = result[0][0]
    else:
        # Insert new user with a random password (they’ll never use it)
        db.execute_query(
            "INSERT INTO chatbot_schema.app_user (txusername, txemail, password) VALUES (%s, %s, %s)",
            (username, email, "")  # empty password or a placeholder
        )
        # Fetch their new id
        fetch = db.read_sql_query(
            "SELECT idappuser FROM chatbot_schema.app_user WHERE txemail = %s",
            (email,)
        )
        user_id = fetch[0][0]

        # Assign default “User” role (idRole = 2, assuming Admin=1, User=2)
        db.execute_query(
            "INSERT INTO chatbot_schema.user_role (idappuser, idrole) VALUES (%s, %s)",
            (user_id, 2)
        )

    # 5. Log them in via session
    session["user_id"] = user_id
    session["username"] = username
    flash(f"Logged in as {username}", "success")
    return redirect("/chat")
```

Now visiting `GET /login/google` will redirect to Google’s consent screen; on success, you’re back at `/login/google` which creates/looks up the user and logs them in.

You may want to remove or disable your old email/password login form so users default to Google. If you still allow local login, keep both.

---

## ⚙️ User Management UI

**Goal:** Let an Admin user see a list of all users, promote/demote roles, and deactivate/reactivate accounts.

### 1. Schema adjustments

We already have:

* `app_user`
* `role` (contains “Admin” and “User”)
* `user_role` (mapping)

To support “deactivated” accounts, add a boolean flag:

```sql
ALTER TABLE chatbot_schema.app_user
  ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
```

### 2. Flask route for “Manage Users”

Only Admins should see this. In `routes/admin.py` (or wherever you group admin endpoints):

```python
from flask import Blueprint, render_template, request, redirect, flash, session, g
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection

admin_bp = Blueprint("admin", __name__)
db = PostgresDatabaseConnection()

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            flash("Please log in", "danger")
            return redirect("/")
        # Check role = Admin
        res = db.read_sql_query("""
            SELECT 1 FROM chatbot_schema.user_role ur
            JOIN chatbot_schema.role r ON ur.idrole = r.idrole
            WHERE ur.idappuser = %s AND r.txname = 'Admin';
        """, (user_id,))
        if not res:
            flash("Admin access required", "danger")
            return redirect("/chat")
        return f(*args, **kwargs)
    return wrapper

@admin_bp.route("/admin/users")
@admin_required
def manage_users():
    rows = db.read_sql_query("""
        SELECT
          u.idappuser,
          u.txusername,
          u.txemail,
          u.is_active,
          ARRAY_AGG(r.txname) AS roles
        FROM chatbot_schema.app_user u
        LEFT JOIN chatbot_schema.user_role ur ON u.idappuser = ur.idappuser
        LEFT JOIN chatbot_schema.role r ON ur.idrole = r.idrole
        GROUP BY u.idappuser, u.txusername, u.txemail, u.is_active
        ORDER BY u.txusername;
    """)
    # rows is a list of tuples or DataFrame, but each row will be (id, username, email, is_active, [roles])
    users = []
    for row in rows:
        users.append({
            "id":         row[0],
            "username":   row[1],
            "email":      row[2],
            "is_active":  row[3],
            "roles":      row[4]  # e.g. ['Admin', 'User']
        })
    return render_template("admin_users.html", users=users)
```

#### 3. `templates/admin_users.html`

```jinja
{% extends "base.html" %}
{% block title %}User Management{% endblock %}
{% block content %}

<h3>User Management</h3>
<hr>

<table class="table table-striped table-dark">
  <thead>
    <tr>
      <th>Username</th>
      <th>Email</th>
      <th>Roles</th>
      <th>Active</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for u in users %}
    <tr>
      <td>{{ u.username }}</td>
      <td>{{ u.email }}</td>
      <td>{{ u.roles|join(", ") }}</td>
      <td>{{ "Yes" if u.is_active else "No" }}</td>
      <td class="d-flex gap-1">
        {# Toggle Admin/User role #}
        {% if "Admin" in u.roles %}
          <form method="POST" action="/admin/users/{{ u.id }}/demote" style="display:inline;">
            <button class="btn btn-sm btn-warning">Demote Admin</button>
          </form>
        {% else %}
          <form method="POST" action="/admin/users/{{ u.id }}/promote" style="display:inline;">
            <button class="btn btn-sm btn-success">Promote Admin</button>
          </form>
        {% endif %}

        {# Toggle activation #}
        {% if u.is_active %}
          <form method="POST" action="/admin/users/{{ u.id }}/deactivate" style="display:inline;">
            <button class="btn btn-sm btn-danger">Deactivate</button>
          </form>
        {% else %}
          <form method="POST" action="/admin/users/{{ u.id }}/reactivate" style="display:inline;">
            <button class="btn btn-sm btn-secondary">Reactivate</button>
          </form>
        {% endif %}
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

{% endblock %}
```

#### 4. Routes to promote/demote/deactivate/reactivate

```python
@admin_bp.route("/admin/users/<int:user_id>/promote", methods=["POST"])
@admin_required
def promote_user(user_id):
    # assign “Admin” role if not already present
    db.execute_query("""
        INSERT INTO chatbot_schema.user_role (idappuser, idrole)
        SELECT %s, r.idrole
        FROM chatbot_schema.role r
        WHERE r.txname = 'Admin'
        ON CONFLICT (idappuser, idrole) DO NOTHING;
    """, (user_id,))
    flash("User promoted to Admin.", "success")
    return redirect("/admin/users")

@admin_bp.route("/admin/users/<int:user_id>/demote", methods=["POST"])
@admin_required
def demote_user(user_id):
    # remove “Admin” role, but don’t delete if they have only one role left (optional safeguard)
    db.execute_query("""
        DELETE FROM chatbot_schema.user_role ur
        USING chatbot_schema.role r
        WHERE ur.idappuser = %s AND ur.idrole = r.idrole AND r.txname = 'Admin';
    """, (user_id,))
    flash("Admin role removed.", "warning")
    return redirect("/admin/users")

@admin_bp.route("/admin/users/<int:user_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_user(user_id):
    db.execute_query("""
        UPDATE chatbot_schema.app_user
        SET is_active = FALSE
        WHERE idappuser = %s;
    """, (user_id,))
    flash("User deactivated.", "warning")
    return redirect("/admin/users")

@admin_bp.route("/admin/users/<int:user_id>/reactivate", methods=["POST"])
@admin_required
def reactivate_user(user_id):
    db.execute_query("""
        UPDATE chatbot_schema.app_user
        SET is_active = TRUE
        WHERE idappuser = %s;
    """, (user_id,))
    flash("User reactivated.", "success")
    return redirect("/admin/users")
```

You’ll need to register `admin_bp` in your main app and ensure there’s a link/button “User Management” only visible to Admins (e.g. in your navbar).

---

## 📈 Model Usage Stats

**Goal:** Count how many prompts each user has sent, and display average inference time per LLM (or per chat).

### 1. Schema changes (optional)

Right now you store messages and responses in separate tables, but no timestamps for “start of LLM call” vs “end.” To measure inference duration, you could:

1. Add a column to `response` called `tstart TIMESTAMPTZ` or `tinf_start`.
2. When you insert the placeholder “🧠 Thinking…” row, set `tinf_start = NOW()`.
3. When you `UPDATE … SET txcontent=…, txmarkdown=…`, also set `tinf_end = NOW()`.
   Then `duration = tinf_end – tinf_start` is your inference time.

For example, run migrations:

```sql
ALTER TABLE chatbot_schema.response
  ADD COLUMN tinf_start TIMESTAMPTZ,
  ADD COLUMN tinf_end   TIMESTAMPTZ;
```

Modify your placeholder‐insert in `chat_view`:

```python
db.execute_query("""
  INSERT INTO chatbot_schema.response (idchat, idmessage, idllm, txcontent, txmarkdown, tinf_start)
  VALUES (
    %s, %s,
    (SELECT idllm FROM chatbot_schema.chat WHERE idchat = %s),
    '🧠 Thinking...', '🧠 Thinking...', NOW()
  );
""", (chat_id, id_message, chat_id))
```

And your update in `update_response_async`:

```python
db.execute_query("""
  UPDATE chatbot_schema.response
  SET txcontent   = %s,
      txmarkdown  = %s,
      tinf_end    = NOW()
  WHERE idmessage = %s AND idchat = %s;
""", (response_html, markdown_text, id_message, chat_id))
```

### 2. Logging total prompts per user

Each time a user submits a message, just increment a counter. Easiest is to derive it on‐the‐fly:

```sql
SELECT u.txusername,
       COUNT(m.idmessage) AS total_prompts
FROM chatbot_schema.app_user u
JOIN chatbot_schema.chat c ON c.idappuser = u.idappuser
JOIN chatbot_schema.message m ON m.idchat = c.idchat
GROUP BY u.txusername
ORDER BY total_prompts DESC;
```

### 3. Create an admin stats page

In `admin_bp` (or a new `stats_bp`), add:

```python
@admin_bp.route("/admin/stats")
@admin_required
def model_stats():
    # 1. Total prompts per user
    usage = db.read_sql_query("""
        SELECT
          u.txusername,
          COUNT(m.idmessage) AS total_prompts
        FROM chatbot_schema.app_user u
        JOIN chatbot_schema.chat c ON c.idappuser = u.idappuser
        JOIN chatbot_schema.message m ON m.idchat = c.idchat
        GROUP BY u.txusername
        ORDER BY total_prompts DESC;
    """)
    # 2. Average inference time per LLM model
    timing = db.read_sql_query("""
        SELECT
          l.txshortname AS model_short,
          ROUND(AVG(EXTRACT(EPOCH FROM (r.tinf_end - r.tinf_start)))::numeric, 3) AS avg_seconds
        FROM chatbot_schema.response r
        JOIN chatbot_schema.llm l ON r.idllm = l.idllm
        WHERE r.tinf_start IS NOT NULL AND r.tinf_end IS NOT NULL
        GROUP BY l.txshortname
        ORDER BY avg_seconds ASC;
    """)
    # Convert to Python lists for Jinja
    prompts = [dict(row) for row in (usage.to_dict("records") if hasattr(usage, "to_dict") else usage)]
    times   = [dict(row) for row in (timing.to_dict("records") if hasattr(timing, "to_dict") else timing)]

    return render_template("admin_stats.html", prompt_stats=prompts, timing_stats=times)
```

#### `templates/admin_stats.html`

```jinja
{% extends "base.html" %}
{% block title %}Usage &amp; Timing Stats{% endblock %}
{% block content %}

<h3>Model Usage &amp; Inference Times</h3>
<hr>

<h5>Total Prompts per User</h5>
<table class="table table-sm table-dark">
  <thead><tr>
    <th>User</th>
    <th># Prompts</th>
  </tr></thead>
  <tbody>
    {% for row in prompt_stats %}
    <tr>
      <td>{{ row.txusername }}</td>
      <td>{{ row.total_prompts }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<h5 class="mt-4">Average Inference Time per Model (seconds)</h5>
<table class="table table-sm table-dark">
  <thead><tr>
    <th>Model</th>
    <th>Avg. Time (s)</th>
  </tr></thead>
  <tbody>
    {% for row in timing_stats %}
    <tr>
      <td>{{ row.model_short }}</td>
      <td>{{ row.avg_seconds }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

{% endblock %}
```

You’ll need to link to `/admin/stats` from your Admin dashboard or sidebar.

---

## 🔐 Two‐Factor Authentication (TOTP)

**Goal:** Let users set up a Time‐based One‐Time Password (TOTP) for logging in (only for local‐login flows, not Google).

### 1. Install dependencies

```bash
pip install pyotp qrcode[pil]
```

### 2. Schema changes

Add columns to store each user’s TOTP secret and whether 2FA is enabled:

```sql
ALTER TABLE chatbot_schema.app_user
  ADD COLUMN totp_secret VARCHAR(32),
  ADD COLUMN is_2fa_enabled BOOLEAN DEFAULT FALSE;
```

### 3. Enable 2FA in user settings

1. Create a route `/settings/2fa` where a logged‐in user can:

   * Generate a new TOTP secret
   * Display a QR code (so they can scan it in Google Authenticator)
   * Enter their next OTP code to confirm.

```python
import pyotp, qrcode
from io import BytesIO
from flask import send_file

@app.route("/settings/2fa", methods=["GET", "POST"])
@login_required
def settings_2fa():
    user_id = session["user_id"]
    # Fetch current secret (if any)
    row = db.read_sql_query(
        "SELECT totp_secret, is_2fa_enabled FROM chatbot_schema.app_user WHERE idappuser = %s;",
        (user_id,)
    )
    if row:
        if hasattr(row, "iloc"):
            secret = row.iloc[0]["totp_secret"]
            enabled = row.iloc[0]["is_2fa_enabled"]
        else:
            secret, enabled = row[0]
    else:
        secret, enabled = None, False

    if request.method == "POST":
        # User clicked “Enable 2FA” or “Confirm code”
        action = request.form.get("action")
        if action == "generate":
            # Create a new 16‐character base32 secret
            new_secret = pyotp.random_base32()
            db.execute_query("""
                UPDATE chatbot_schema.app_user SET totp_secret = %s WHERE idappuser = %s;
            """, (new_secret, user_id))
            secret = new_secret
            enabled = False
            flash("Scan the QR code below with your Authenticator app, then enter the code to confirm.", "info")

        elif action == "confirm":
            code = request.form.get("otp_code", "")
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                db.execute_query("""
                    UPDATE chatbot_schema.app_user SET is_2fa_enabled = TRUE WHERE idappuser = %s;
                """, (user_id,))
                enabled = True
                flash("2FA enabled successfully!", "success")
            else:
                flash("Invalid code; please try again.", "danger")

        elif action == "disable":
            db.execute_query("""
                UPDATE chatbot_schema.app_user
                SET is_2fa_enabled = FALSE, totp_secret = NULL
                WHERE idappuser = %s;
            """, (user_id,))
            secret = None
            enabled = False
            flash("2FA disabled.", "warning")

    # Render template, passing secret & enabled
    return render_template("settings_2fa.html", secret=secret, enabled=enabled)
```

#### 4. Route to serve QR code image

```python
@app.route("/2fa/qrcode.png")
@login_required
def twofa_qrcode():
    user_id = session["user_id"]
    row = db.read_sql_query(
        "SELECT totp_secret, txemail FROM chatbot_schema.app_user WHERE idappuser = %s;",
        (user_id,)
    )
    if row:
        if hasattr(row, "iloc"):
            secret = row.iloc[0]["totp_secret"]
            email  = row.iloc[0]["txemail"]
        else:
            secret, email = row[0]
    else:
        return ("Not found", 404)

    if not secret:
        return ("No 2FA secret", 404)

    # Create provisioning URI for Google Authenticator
    issuer = "MyChatApp"
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)

    # Generate QR code as PNG
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
```

#### 5. `templates/settings_2fa.html`

```jinja
{% extends "base.html" %}
{% block title %}Two‐Factor Authentication{% endblock %}
{% block content %}

<h3>Two‐Factor Authentication Settings</h3>
<hr>

{% if not secret %}
  <p>You don’t have 2FA configured. Click below to generate a new secret and QR code.</p>
  <form method="POST">
    <button type="submit" name="action" value="generate" class="btn btn-primary">Enable 2FA</button>
  </form>
{% else %}
  {% if not enabled %}
    <p>Scan this QR code in Google Authenticator (or any TOTP app), then enter the code below to confirm.</p>
    <img src="/2fa/qrcode.png" alt="QR Code for 2FA">
    <form method="POST" class="mt-3">
      <div class="mb-2">
        <label for="otp_code" class="form-label">Enter code from app</label>
        <input type="text" name="otp_code" id="otp_code" class="form-control" maxlength="6" required>
      </div>
      <button type="submit" name="action" value="confirm" class="btn btn-success">Confirm</button>
    </form>
  {% else %}
    <p>2FA is <strong>enabled</strong> on your account.</p>
    <form method="POST">
      <button type="submit" name="action" value="disable" class="btn btn-danger">Disable 2FA</button>
    </form>
  {% endif %}
{% endif %}

{% endblock %}
```

#### 6. Enforce 2FA at login

* If a user logs in via **local username/password**, after verifying their password, check `is_2fa_enabled`.

  1. If not enabled, proceed as normal.
  2. If enabled, redirect to a `/login/2fa` page where you prompt them to enter their OTP code.
  3. In that `/login/2fa` handler, verify `pyotp.TOTP(secret).verify(code)`. If valid, finalize `session["user_id"]` and redirect to `/chat`. If invalid, show an error.

Because you also support **Google OAuth**, you can choose to let Google‐logged‐in users bypass 2FA or require it. (You might only enable 2FA for local accounts.)

---

## Putting It All Together

* **Google OAuth** → lets new/existing users sign in with a Google email and auto‐assign “User” role.
* **User Management UI** → a protected `/admin/users` page where Admins can promote/demote and activate/deactivate.
* **Model Usage Stats** → a protected `/admin/stats` page showing prompt counts and average inference time (after adding `tinf_start`/`tinf_end`).
* **2FA (TOTP)** → an optional per‐user security layer: “Enable 2FA” generates a QR, user scans+confirms, then on each login they must enter the OTP.

Once you wire all of these routes into your Flask top‐level app, add links in your navigation (visible only to Admins for management/stats, visible to all for 2FA/settings), and write a few unit tests around the SQL queries, you’ll have a robust v1.1 feature set.