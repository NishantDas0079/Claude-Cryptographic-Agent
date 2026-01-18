## 📚 Documentation Index

| Document | Description | Link |
|----------|-------------|------|
| Architecture Decision | Why we chose multi-agent | [Final-Decision.md](Final-Decision.md) |
| Core Design | Multi-agent system architecture | [Multi-Agent-Architecture.md](Multi-Agent-Architecture.md) |
| Tool Protocol | MCP integration | [MCP.md](MCP.md) |
| Agent Framework | LangChain implementation | [LangChain.md](LangChain.md) |
| Knowledge System | Graph RAG for cryptography | [GraphRAG.md](GraphRAG.md) |
| Implementation | Code and configuration | [Implementation.md](Implementation.md) |
| Complete System | Unified architecture | [Unified-System.md](Unified-System.md) |
| Deployment | Setup and operations | [Deployment.md](Deployment.md) |
| Monitoring | Observability and alerts | [Monitoring.md](Monitoring.md) |



# 1. Architecture Design
# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  (CLI / Web UI / API Gateway)                               │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/JSON
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Claude Agent Orchestrator                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Task Planner & Reasoner                            │    │
│  │  • Parse natural language requests                   │    │
│  │  • Sequence cryptographic operations                 │    │
│  │  • Validate against policies                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                    │                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Policy Engine Interface                            │    │
│  │  • Check key size requirements                      │    │
│  │  • Validate certificate parameters                  │    │
│  │  • Enforce compliance rules                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                    │                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Tool Dispatcher                                   │    │
│  │  • Route to appropriate tool                       │    │
│  │  • Handle error conditions                         │    │
│  │  • Validate outputs                                │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │ Tool Calls
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tool Layer (External Systems)            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ OpenSSL  │  │  Vault   │  │  CA API  │  │  HSM     │   │
│  │ CLI/API  │  │ (TLS/API)│  │ (REST)   │  │ (PKCS#11)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Certificate Inventory DB                           │    │
│  │  • PostgreSQL with crypto schema                    │    │
│  │  • All keys/certs metadata                          │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Audit Log (Immutable)                             │    │
│  │  • Tamper-evident storage                          │    │
│  │  • SIEM integration                                │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Policy Configuration                              │    │
│  │  • YAML/JSON configs                              │    │
│  │  • GitOps for versioning                          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
    subgraph "User Interface Layer"
        A[Human Operator] --> B[Admin Dashboard]
        B --> C[API Gateway<br/>REST/gRPC]
        C --> D[Audit Log Viewer]
    end

    subgraph "Claude Agent Core Layer"
        E[Claude AI Agent] --> F{Agent Core Components}
        F --> G[Task Planner<br/>& Orchestrator]
        F --> H[Policy Engine<br/>& Guardrails]
        F --> I[Context Manager<br/>& State Tracker]
        
        G --> J[Cryptographic Workflow<br/>Sequencer]
        H --> K[Policy Validator]
        I --> L[Session Context<br/>& History]
    end

    subgraph "Tool Integration Layer"
        M[Tool Registry] --> N[Approved Tools]
        N --> O[Key Generation Tools<br/>OpenSSL, PKCS#11]
        N --> P[CSR Tools<br/>X.509 Library]
        N --> Q[Certificate Tools<br/>CA Interface]
        N --> R[Validation Tools<br/>Policy Checker]
    end

    subgraph "External PKI Systems"
        S[Certificate Authority<br/>e.g., EJBCA, MS CA]
        T[Crypto Vault<br/>e.g., HashiCorp Vault]
        U[Hardware Security Module<br/>HSM]
        V[Key Management System<br/>KMS]
    end

    subgraph "Data & Compliance Layer"
        W[Audit Log Database<br/>Immutable Storage]
        X[Certificate Inventory<br/>CMDB]
        Y[Policy Repository<br/>JSON/YAML]
        Z[Compliance Dashboard]
    end

    %% Connections between layers
    C --> E
    E --> M
    
    O --> S
    O --> T
    O --> U
    
    P --> S
    Q --> S
    
    R --> Y
    
    G --> W
    H --> W
    
    Q --> X
    
    W --> Z
    X --> Z
```


# Core Components
# 1. Claude Agent
Purpose: Main orchestrator and decision-maker

# Capabilities:

Natural language processing for requests

Multi-step planning and reasoning

Policy validation before execution

Error handling and recovery

# 2. Policy Engine
Policy Store: Git repository with YAML policy files

Validation Rules: Key size, algorithm, validity period, EKUs

Compliance Checks: NIST, FIPS, organizational standards

# 3. Tool Integrations
OpenSSL Wrapper: Safe command generation and output parsing

Vault Integration: Secure key storage and management

CA APIs: Integration with CAs (Let's Encrypt, Private CA)

HSM Interface: PKCS#11 for hardware security modules

# 4. Inventory & Audit
PostgreSQL Database: Structured storage of all crypto assets

Immutable Audit Log: Blockchain-like ledger or WORM storage

SIEM Integration: Real-time security monitoring




