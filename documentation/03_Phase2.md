This **is** a huge and exciting step — you’re going from **bare dev** into full **CI/CD-driven deployment** to your Kubernetes cluster! Let’s break it down into manageable phases.

---

### 🧩 Your Goal in Simple Terms

> ✅ Build Docker image of your app via GitLab CI  
> ✅ Push it to the GitLab container registry  
> ✅ Deploy it via ArgoCD using manifests in `manifests/webapp/`  
> ✅ Inside the deployed pod, auto-run the database initialization  
> ✅ Serve a test website to verify everything works

---

## 🧱 Phase 1: GitLab CI — Build and Push Docker Image

### ✅ Prerequisites

1. You already have a **Dockerfile** (in `prod/` or move to root?)
2. GitLab container registry is ready (`registry.gitlab.com/your_namespace/project`)
3. GitLab Runner is configured (you’ve done this ✅)

### 📄 `.gitlab-ci.yml` (simplified)

```yaml
stages:
  - build

variables:
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

build_image:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
  script:
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG
```

> You’ll need your GitLab secrets (`CI_REGISTRY_USER` + `CI_REGISTRY_PASSWORD`) set in the **project CI/CD variables**.

---

## 📦 Phase 2: Reference Image in Kustomize Deployment

In `manifests/webapp/kustomization.yaml`, you'll define:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
  - ingress.yaml

images:
  - name: chatbot-app
    newName: registry.gitlab.com/<your_namespace>/<your_project>
    newTag: <COMMIT_HASH or version>
```

---

## 🚀 Phase 3: `deployment.yaml`

This will:

- Pull the container image
- Run the app container
- Connect to the cluster DB
- Run `execute.py` to set up schema
- Serve the website

### 👇 Example `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-app
  namespace: chatbot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chatbot-app
  template:
    metadata:
      labels:
        app: chatbot-app
    spec:
      containers:
      - name: chatbot
        image: registry.gitlab.com/<your_namespace>/<your_project>:<TAG>
        ports:
          - containerPort: 5000
        env:
          - name: PSQL_HOST
            valueFrom:
              configMapKeyRef:
                name: postgres-config
                key: db_host
          - name: PSQL_DB
            valueFrom:
              configMapKeyRef:
                name: postgres-config
                key: db_name
          - name: PSQL_USER
            valueFrom:
              configMapKeyRef:
                name: postgres-config
                key: db_user
          - name: PSQL_PORT
            valueFrom:
              configMapKeyRef:
                name: db_port
          - name: PSQL_PASSWORD
            valueFrom:
              secretKeyRef:
                name: postgres-secret
                key: password
        command: ["python"]
        args: ["src/sql/execute.py"]
```

---

## 🎯 Phase 4: ArgoCD App Definition

You already have your ArgoCD app configured. Just update it to point to the right image/tag and sync.

---

### 🔁 Optional Enhancement

Later, split your image in two:

- `chatbot-init`: a Job that just runs `execute.py`
- `chatbot-web`: the actual web app

But for now, you can **run the init once inside your app container**.

---

## ✅ Checklist to Start

1. [✅] Create/verify working Dockerfile 
2. [✅] Push to GitLab and verify registry setup
3. [✅] Add `.gitlab-ci.yml` to build and push
4. [✅] Write `deployment.yaml` and reference image
5. [✅] Complete `kustomization.yaml`
6. [✅] Trigger ArgoCD to deploy
7. [✅] Use `kubectl logs` to verify `execute.py` + app

---

Want me to:

- Help you write the Dockerfile tailored to your app?
- Prepare a working `.gitlab-ci.yml` with registry details?
- Build a `deployment.yaml` stub using your app structure?

Let’s go step by step. What should we tackle next?