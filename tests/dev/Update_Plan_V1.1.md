## 1. Branching & Git Flow

1. **Develop on a feature branch**

   * Instead of working directly in `tests/dev/src`, create a branch like `release/v1.1` or `feature/v1.1-bugfixes`.
   * Keep your `main` (or `master`) branch strictly in sync with production’s `src/`.

2. **Merge workflow**

   * When v1.1 dev work is done and tested locally against `tests/dev/src`, open a Pull Request from `feature/v1.1` into `main`.
   * In that PR:

     * Move the code from `tests/dev/src/` into `src/` (overwriting or augmenting existing files).
     * Remove or archive old test‐specific boilerplate.
     * Bump your version number (e.g. in a `VERSION` file, `setup.py`, or `pyproject.toml`) to `1.1.0`.

3. **Tag the release**

   * As part of the merge, tag the merge commit on `main` as `v1.1.0`.

---

## 2. Repository Layout

After the merge, you’ll want:

```
/
├── src/                   ← production code
│   ├── routes/
│   ├── utils/
│   └── templates/
├── tests/                 ← automated tests only
│   ├── unit/              ← pytest/unit tests
│   └── integration/       ← end‐to‐end tests
├── migrations/            ← SQL migration scripts
├── VERSION                ← e.g. “1.1.0”
└── .github/ or .gitlab-ci.yml  ← CI/CD pipelines
```

* **Move** everything under `tests/dev/src/` into `src/`.
* **Retire** the old “dev” folder once you’ve merged and ensured tests run against `src/`.
* Keep `tests/` for your real test suite—this makes CI config simpler (`pytest tests/`).

---

## 3. CI/CD Pipeline

1. **Continuous Integration**

   * On every PR into `main`, run:

     1. `flake8` / `black` / `isort`
     2. `pytest tests/` (unit & integration)
     3. Lint your SQL migrations (if applicable)

2. **Staging deployment**

   * On merge into a `develop` or `staging` branch:

     1. Build a Docker image tagged `v1.1.0-rc`
     2. Deploy to a staging environment automatically
     3. Run smoke‐tests (e.g. hit `/chat` and `/projects`)

3. **Production deployment**

   * On Git tag `v1.1.0`:

     1. Build and push a Docker image `registry/.../signature_project:v1.1.0`
     2. Apply migrations in production (using your `migrations/` folder)
     3. Deploy/update your service (e.g. rolling restart, Kubernetes rollout)
     4. Run a final smoke‐test and monitor logs/metrics

---

## 4. Database Migrations

* Keep all schema changes (adding `txshortname`, new columns for stats, etc.) as **versioned SQL scripts** in `migrations/`.
* Use a simple tool (Flyway, Alembic, or even a shell script that applies `01_`, `02_`, … in order).
* In prod, your deploy step must run something like:

  ```bash
  psql -U chatbot_user -d chatbot_db -f migrations/01_add_txshortname.sql
  psql -U chatbot_user -d chatbot_db -f migrations/02_add_timing_columns.sql
  # etc.
  ```

That way the schema upgrade is repeatable, reversible (with down‐scripts), and tracked in Git.

---

## 5. Versioning & Releases

* Keep a top‐level `VERSION` (or in `setup.py`) so your container image and your app know their own version.
* After merging v1.1 into `main`, run:

  ```bash
  git checkout main
  git pull
  git tag v1.1.0
  git push origin v1.1.0
  ```
* Let your CI detect that tag and kick off the production build/deploy pipeline.

---

## 6. Rollback Plan

* **Code**: roll back by deploying the previous Docker tag (e.g. `v1.0.0`).
* **DB**: if you’ve only added columns, those are usually backward‐compatible; if you drop columns or change types, write corresponding “down” scripts to reverse your migrations.

---

### In a nutshell

1. **Branch** off `main` into `feature/v1.1`.
2. **Merge** your dev directory into `src/`, delete leftover dev scaffolding.
3. **Commit** a `VERSION` bump and add/rename migrations.
4. **CI**: test → staging → tag → production.
5. **Tag** `v1.1.0` and let your pipeline build & deploy.
6. **Monitor** and rollback if needed.

This keeps your dev and prod code cleanly separated, makes your releases predictable, and automates as much of the pain out of cutovers as possible.
