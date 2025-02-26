Yes, it's absolutely possible! Here's a high-level plan for your setup:

### **1. Architecture Overview**
- **Linux Mint VM (192.168.0.42)**: Runs `ollama run deepseek-coder` on GPU.
- **Ubuntu Server (192.168.0.100, Kubernetes Cluster)**:
  - **Flask API/Web App**: Accepts user input, sends it to DeepSeek Coder, and stores conversation logs.
  - **PostgreSQL Database**: Stores chat history.

### **2. Steps to Implement**
#### **Step 1: Expose DeepSeek Coder API on Linux Mint VM**
- DeepSeek Coder runs locally. To interact with it remotely, expose it via an HTTP API.
- Start DeepSeek Coder with `ollama serve` and check the API:
  ```bash
  ollama serve
  curl -X POST http://127.0.0.1:11434/api/generate -d '{"model":"deepseek-coder","prompt":"Hello"}'
  ```
- Modify firewall rules if needed to allow connections from the Ubuntu server.

#### **Step 2: Deploy Flask App in Kubernetes**
- Create a Flask-based web app with:
  - A text input form.
  - API request handling to DeepSeek Coder.
  - PostgreSQL storage integration.
- Example Flask API (`app.py`):
  ```python
  from flask import Flask, request, jsonify
  import requests
  import psycopg2

  app = Flask(__name__)

  # PostgreSQL connection
  conn = psycopg2.connect(
      dbname="chatdb",
      user="your_user",
      password="your_password",
      host="postgres-service",
      port="5432"
  )
  cur = conn.cursor()

  @app.route("/chat", methods=["POST"])
  def chat():
      user_input = request.json.get("message")
      deepseek_url = "http://192.168.0.42:11434/api/generate"

      response = requests.post(deepseek_url, json={"model": "deepseek-coder", "prompt": user_input})
      ai_response = response.json().get("response", "")

      # Store conversation in PostgreSQL
      cur.execute("INSERT INTO conversations (user_input, ai_response) VALUES (%s, %s)", (user_input, ai_response))
      conn.commit()

      return jsonify({"response": ai_response})

  if __name__ == "__main__":
      app.run(host="0.0.0.0", port=5000)
  ```
  
#### **Step 3: Create Kubernetes Manifests**
- **Deployment for Flask API**
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: flask-chatbot
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: flask-chatbot
    template:
      metadata:
        labels:
          app: flask-chatbot
      spec:
        containers:
        - name: flask-chatbot
          image: your-docker-image
          ports:
          - containerPort: 5000
          env:
          - name: DB_HOST
            value: "postgres-service"
          - name: DB_USER
            value: "your_user"
          - name: DB_PASSWORD
            value: "your_password"
  ```

- **PostgreSQL Service & Deployment**
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: postgres-service
  spec:
    selector:
      app: postgres
    ports:
      - protocol: TCP
        port: 5432
  ---
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: postgres
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: postgres
    template:
      metadata:
        labels:
          app: postgres
      spec:
        containers:
        - name: postgres
          image: postgres:15
          env:
          - name: POSTGRES_DB
            value: "chatdb"
          - name: POSTGRES_USER
            value: "your_user"
          - name: POSTGRES_PASSWORD
            value: "your_password"
          ports:
          - containerPort: 5432
  ```

- **Service for Flask API**
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: flask-service
  spec:
    selector:
      app: flask-chatbot
    ports:
      - protocol: TCP
        port: 5000
        targetPort: 5000
    type: NodePort
  ```

#### **Step 4: Deploy to Kubernetes**
- Build & push the Flask app image:
  ```bash
  docker build -t your-dockerhub/flask-chatbot .
  docker push your-dockerhub/flask-chatbot
  ```
- Apply the manifests:
  ```bash
  kubectl apply -f flask-deployment.yaml
  kubectl apply -f postgres-deployment.yaml
  kubectl apply -f flask-service.yaml
  ```

#### **Step 5: Test the Chatbot**
- Get the service's NodePort:
  ```bash
  kubectl get svc flask-service
  ```
- Send a request from your browser or terminal:
  ```bash
  curl -X POST http://192.168.0.100:<NODE_PORT>/chat -H "Content-Type: application/json" -d '{"message":"Hello"}'
  ```

### **Next Steps**
- Add a frontend UI (HTML/React) for a chatbot-like experience.
- Secure PostgreSQL using Kubernetes secrets.
- Deploy a Kubernetes Ingress to expose the service externally.

Would you like any modifications or additional features? 🚀