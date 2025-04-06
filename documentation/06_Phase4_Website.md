Perfect — here's the **updated Markdown version** of your chatbot app workflow, reflecting the clarified user and chat behavior. I've also included an updated image you can embed into your docs.

---

## ✅ **Chatbot Web App — Updated Workflow (2025)**

### 👤 Step 1: User Flow

```text
[ Visit App ]
   ↓
[ Not Logged In? ]
   ├──→ [ Register ]
   └──→ [ Login ] → [ Redirect to Chat View (/chat) ]
```

- New users register first
- Logged-in users are redirected to their last chat
- If no chats exist → prompt to create a chat

---

### 💬 Step 2: Chat Flow

```text
[ User Logged In ]
      ↓
  [ Chat View ]
      ├── No chats? → [ Create New Chat ] → [ Enter Chat View ]
      ├── Has chats? → [ Sidebar ] → [ Select Chat ]
      └── Inside Chat View:
            • View messages (latest at bottom)
            • Scroll through history
            • Send new message
            • Optionally assign chat to a project
```

---

### 📁 Step 3: Project Flow (Folders)

```text
[ Optional at Any Time ]
     ↓
[ + Create Project ]
     ↓
[ Projects show as collapsible folders in sidebar ]
     ↓
[ Assign chat to a project (or leave unassigned) ]
```

---

### 🧱 **Database Relationships**

```text
app_user
   │
   └───┬───< chat >────┬────> project
       │               │
       └────< message  │
```

- `app_user.idappuser` → `chat.user_id`
- `chat.idchat` → `message.chat_id`
- `chat.project_id` → `project.idproject` (nullable)

---

## ✅ Functional Checklist

| Feature                     | Status        | Description                            |
|----------------------------|---------------|----------------------------------------|
| Register & Login           | ✅ Done       | With redirect logic                    |
| Create Chat                | ✅ Done       | Required before messaging              |
| View & Send Messages       | ✅ Done       | Scrollable area, newest at bottom      |
| Create Project             | ✅ Done       | Optional folder for organizing chats   |
| Assign Chat to Project     | ✅ Done       | At creation or later                   |
| Sidebar Project View       | ✅ Done       | Collapsible folders                    |
| Unassigned Chat Section    | ✅ Done       | Under 🗂 *Others*                       |
| Switch Between Chats       | ✅ Done       | Click on a chat name                   |
| Chat Auto-Scroll           | ✅ Done       | Scrolls to newest message              |

---

## 📊 Visual Layout (Text Preview)

```
┌────────────────────────────┐
│        🔐 Navbar           │ ← Logged in as <username> | Logout
└────────────────────────────┘
┌────────────┬───────────────┐
│  📁 Sidebar │ 💬 Chat Area   │
│            │               │
│ + Chat     │   Chat title  │
│ + Project  │   Messages... │
│ ───────────│   [form box]  │
│ 📁 Project │               │
│   💬 Chat  │               │
│   💬 Chat  │               │
│ 📁 Project │               │
│   💬 Chat  │               │
│ 🗂 Others  │               │
│   💬 Chat  │               │
└────────────┴───────────────┘
```

---

### 📌 Edge Cases

| Case                         | Behavior                                    |
|-----------------------------|---------------------------------------------|
| No user logged in           | Redirect to login                           |
| New user with no chats      | Auto-create or prompt to start new chat     |
| No projects created         | Show "+ New Project" and empty folders      |
| Unassigned chats            | Listed under "🗂 Others"                    |
| Future features             | Chat rename, deletion, message editing      |

---

## 🖼️ Embed Diagram (PNG)

![Chatbot Workflow](assets/chatbot_workflow_2025.png)

---
---

## **Step-by-step to implement the **full workflow**:**



## 🔧 Implementation Plan Based on Workflow

### ✅ 1. **Redirect Behavior**
- [x] After login, redirect user to `/chat`
- [x] If user has no chat → auto-create or prompt to create one

### ✅ 2. **Sidebar: Projects & Chats**
- [x] Sidebar loads on `/chat/*`
- [x] Shows:
  - `+ New Chat`
  - `+ New Project`
  - 📁 Folders (projects)
  - 🗂 Others (unassigned chats)

### ✅ 3. **Chat View**
- [x] `/chat/<int:chat_id>` shows messages
- [x] User can send message
- [x] Scrolls to bottom automatically

### ✅ 4. **New Chat**
- [x] Route: `/chat/new`
- [x] Creates chat (optional project_id) → redirects to `/chat/<id>`

### ✅ 5. **Project Creation**
- [x] Route: `/projects`
- [x] Form to create new project (name + optional desc)

### 🧠 6. **Optional: Assign Chat to Project**
- [ ] UI or dropdown to move chat to a project (coming soon)

---

## 🚀 Next Up: What We'll Do Now

We'll:
1. Clean up remaining TODOs
2. Ensure **chat creation → message sending → chat switching** works
3. Validate that the **sidebar loads dynamically per user**
4. Start adding **project assignment logic** into chat creation or editing

---

Shall we begin with:
- ✅ Making sure the sidebar loads correctly for new users and matches the layout?
- ➕ Or start implementing "Assign chat to project" functionality?
