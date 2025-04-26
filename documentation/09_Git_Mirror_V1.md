## 📁 Git Mirroring & Version Tagging

### 🔁 GitLab to GitHub Mirroring (CI-Driven)

To ensure that the private GitLab repository remains the **source of truth**, while still allowing **public access** via GitHub, I implemented **automated repository mirroring** through GitLab CI/CD.

#### ✅ Highlights:
- **Two Git remotes** configured:
  - `origin` → Private GitLab (`git@192.168.0.100:homelab/signature_project.git`)
  - `github` → Public GitHub (`git@github.com:marwiesing/signature_project.git`)
- A new GitLab CI job named `mirror-to-github` was added to automatically:
  - Authenticate via SSH using a **GitHub Deploy Key**
  - Push the latest commit and **all Git tags** to GitHub
  - Run after each successful deployment to ensure GitHub is always up-to-date

#### 🔧 Sample CI Job (`.gitlab-ci.yml`):

```yaml
mirror-to-github:
  stage: mirror
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh git
    - mkdir -p ~/.ssh
    - echo "$GITHUB_DEPLOY_KEY" > ~/.ssh/id_ed25519
    - chmod 600 ~/.ssh/id_ed25519
    - ssh-keyscan github.com >> ~/.ssh/known_hosts
    - git config --global user.name "GitLab CI Bot"
    - git config --global user.email "ci@homelab.local"
  script:
    - echo "📝 Commit: ${CI_COMMIT_TITLE} by ${GITLAB_USER_NAME}"
    - git log -1 --oneline
    - echo "🌍 Pushing to GitHub mirror..."
    - git remote add github git@github.com:marwiesing/signature_project.git || true
    - git push --force github HEAD:main
    - git push github --tags
  only:
    - main
```

---

### 🏷️ Git Tagging for Versioning

To mark production-ready releases, I introduced **semantic versioning** using Git tags.

#### ✅ Workflow:

1. After a successful build and deployment:
   ```bash
   git tag v1.0.0 -m "First public release"
   ```
2. Push the tag to GitLab:
   ```bash
   git push origin v1.0.0
   ```
3. The GitLab CI job automatically mirrors the tag to GitHub.

#### 🎯 Benefits:
- Clean version tracking
- Easy rollback or comparison between releases
- Visible release points for external users on GitHub

---

### 🔚 Conclusion

This setup establishes a **robust GitOps foundation** with:

- GitLab as the private DevOps hub
- GitHub as a public-facing mirror
- Automatic version tagging
- Seamless multi-platform availability

---
