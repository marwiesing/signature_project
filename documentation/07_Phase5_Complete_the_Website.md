### 🧭 Next Steps (Phase 3 Preview?)
Would you like to:
- Start **LLM integration**?
- Add **Markdown export**, **chat memory**, or **RBAC**?
- Set up **ArgoCD auto-sync** for deployments?

----


Perfect — let’s organize everything for your **LLM integration Phase 4** into a detailed checklist ✅

---

## ✅ **LLM Integration Checklist for Phase 4**

### 🗄️ DATABASE

- [✅] **Create a new `llm_model` table**  
  Stores model info like `deepseek-r1`, `deepseek-coder`.

- [✅] **Add `llm_model_id` FK column to the `chat` table**  
  Links each chat to a specific LLM.

- [✅] **Backfill existing chats** (optional)  
  Assign `deepseek-r1` as the default for old chats.

---

### ⚙️ WORKFLOW + BACKEND

- [✅] **Update chat creation logic**  -- ** Created a default chat LLM option**
  Require user to **select an LLM model** when creating a new chat (in routes and forms).

- [✅] **Update `chat.py` and `project.py` routes**  
  Ensure model selection is passed and stored with new chat.

- [ ] **Update `query_ollama(prompt, model)` function**  
  Fetch model name from the chat (`chat.llm_model.name`) and use it to run `ollama`.

- [ ] **Update the chat page to show model in the header**  
  Display something like:
  ```html
  <h3>Chat (Model: DeepSeek-R1)</h3>
  ```

---

### 🧠 UI / FRONTEND

- [ ] **Update chat creation modal in `base.html`**
  - Add dropdown/select for `Model: deepseek-r1 / deepseek-coder`.

- [ ] **Update chat creation on `project_details.html`**
  - Same model dropdown as above.

- [ ] **(Optional)** Add an icon or tag next to each chat in the sidebar showing which model it uses.

---

### 📦 OPTIONAL EXTRAS

- [ ] (Optional) Allow model switching in an existing chat  
  (Requires updating the `llm_model_id` for the chat)

- [ ] (Optional) Add a new page to manage available LLM models  
  Just like project management, for future expandability.

---

### 🔚 Final Integration

- [ ] **Test message submission and response routing**
  - Make sure messages go to correct LLM.
  - Make sure UI behaves accordingly (no hardcoding model names).

- [ ] **Sync to GitLab and ArgoCD**  
  Confirm new database structure and model handling are deployed correctly.

---

Would you like me to generate:
- The `llm_model` table and `chat` update SQL?
- The HTML `<select>` dropdown for model selection?
- The backend logic for saving/using the selected model?

Let’s knock it out step-by-step 🔨

---
---

## **Status Update:**
---


✅ **Yes! Your updated code is clean, correct, and fully functional.**  
Let’s do a quick final checklist:

You're making **amazing progress** — your checklist is super well-organized 🔥  
Let's keep that momentum going.

---

## ✅ ✅ Updated LLM Integration Checklist – Phase 4 Progress

### ✅ COMPLETED

#### 🗄️ **DATABASE**
- ✅ `llm` table created (`deepseek-r1`, `deepseek-coder`)
- ✅ `chat.idllm` FK added
- ✅ Existing chat creation logic backfilled with default LLM (`deepseek-r1`)
- ✅ Indexes and schema applied in `initialize_schema.sql`

#### ⚙️ **WORKFLOW / BACKEND**
- ✅ `/chat/new` assigns default model
- ✅ `/chat/<id>/set_model` updates model
- ✅ `chat_view()` renders current model name + list
- ✅ `chat.html` header and switch form added

---

## 🔜 NEXT TASKS

### ⚙️ **LLM Query Integration**

| Task | Status | Notes |
|------|--------|-------|
| 🧠 `query_ollama(prompt, model)` | ⏳ **To Do** | Not implemented yet — this function will call your local Ollama CLI (`ollama run model`) using `subprocess`, or via REST if needed |
| 💾 Save LLM response in `response` table | ⏳ **To Do** | After the LLM call, save the result linked to the `message` ID |

### Add `.env` or K8s secret

In development (`.env` or exported manually):
```env
OLLAMA_HOST=http://localhost:11434
```

In production (`values.yaml`, Secret, or Deployment env):
```env
OLLAMA_HOST=http://192.168.0.42:11434

---

---

### 🧠 UI / FRONTEND – Chat Creation

| Task | Status | Notes |
|------|--------|-------|
| 🎨 Add model selection to `base.html` `+ New Chat` | ⏳ **To Do** | Add `<select>` to the form or popup |
| 🎨 Add model selection to `project_detail.html` | ⏳ **To Do** | Also dropdown to select LLM on creation |
| 🏷️ (Optional) Add icon/tag in sidebar chats | ⏳ **To Do** | E.g. show `🤖` or model name next to chat |

---

### 📦 OPTIONAL EXTRAS

| Task | Status |
|------|--------|
| 🔁 Switch model per message (advanced) | Optional |
| ⚙️ Manage LLM models in a separate admin UI | Optional |

---

### ✅ DEPLOYMENT / FINAL STEPS

| Task | Status |
|------|--------|
| 🧪 Test message submission + model routing | ⏳ |
| 🔁 Ensure response generation works end-to-end | ⏳ |
| 🧑‍💻 Push to GitLab + ArgoCD sync | ⏳ |

---

## 🔜 **Your Next Logical Step**

### 🧠 Implement `query_ollama(prompt, model)` in `utils/llm.py`

This will:
- Accept `prompt`, `model_name`
- Run `ollama run model_name`, send prompt, return response


