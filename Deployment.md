# 3. Deployment Configuration
# 3.1 Docker Compose Setup

```
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: crypto_inventory
      POSTGRES_USER: crypto_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  vault:
    image: vault:1.15
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: ${VAULT_TOKEN}
      VAULT_DEV_LISTEN_ADDRESS: "0.0.0.0:8200"
    ports:
      - "8200:8200"
    volumes:
      - ./vault_config.hcl:/vault/config/vault.hcl

  claude-agent:
    build: .
    environment:
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
      DATABASE_URL: "postgresql://crypto_admin:${DB_PASSWORD}@postgres/crypto_inventory"
      VAULT_ADDR: "http://vault:8200"
      VAULT_TOKEN: ${VAULT_TOKEN}
      POLICY_PATH: "/app/config/policies.yaml"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - postgres
      - vault

  api-gateway:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - claude-agent

volumes:
  postgres_data:
```

# 3.2 Kubernetes Deployment

```
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: claude-crypto-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: crypto-agent
  template:
    metadata:
      labels:
        app: crypto-agent
    spec:
      containers:
      - name: agent
        image: claude-crypto-agent:latest
        env:
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: claude
        - name: VAULT_TOKEN
          valueFrom:
            secretKeyRef:
              name: vault-creds
              key: token
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: audit-logs
          mountPath: /app/logs
      volumes:
      - name: config-volume
        configMap:
          name: crypto-policies
      - name: audit-logs
        persistentVolumeClaim:
          claimName: audit-logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: claude-agent-service
spec:
  selector:
    app: crypto-agent
  ports:
  - port: 80
    targetPort: 8000
```

