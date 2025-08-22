# 2. Solution technique

## 2.1 Aperçu

Cette sous-section résume les principaux changements requis aux infrastructures matérielles et logicielles afin de supporter la solution décrite dans le But du projet de ce document

### Vue - Aperçu technique cible

- **Architecture multi-utilisateurs** avec isolation stricte des données par utilisateur
- **Authentification OAuth progressive** par service (Notion, Google, Microsoft, YouTube)
- **Stratégie SMS unique** : Un numéro Twilio avec identification utilisateur par numéro de téléphone
- Architecture conteneurisée (Docker) pour tous les services applicatifs
- Services principaux: API Backend (FastAPI), Service Agent (LLM orchestration), Workers asynchrones (scheduler/arrière-plan), Base de données PostgreSQL, Cache/Queue Redis, Proxy inverse (TLS), Observabilité (metrics/logs/traces), Gestion des secrets
- Intégrations externes: LLM (Gemini), Calendrier/Emails (Graph/Gmail), Notion/YouTube/Internet Tools; toutes les intégrations protégées par timeouts, retries, rate-limiting et circuit breakers
- Sécurité: TLS en transit, chiffrement au repos (DB), **tokens OAuth stockés de façon sécurisée par utilisateur**, isolation stricte des données par utilisateur (multi-utilisateurs individuels, pas de collaboration d'équipe)
- Déploiement: Docker containers, orchestrés par un compose/stacks (évolution possible vers orchestrateur géré ultérieurement)
- Environnements: Dev/Stage/Prod (détails en 2.3), avec variables d'environnement et gestion de secrets séparée

### Objectifs non-fonctionnels (cibles)

- Performance: latence de réponse utilisateur P95 < 2 s (hors dépendances externes), budgets d'appels API par requête documentés et respectés
- Fiabilité: disponibilité > 99.5% (Prod), MTTD < 5 min, MTTR < 30 min
- Sécurité: chiffrement des données au repos et en transit, gestion des accès par utilisateur, journaux d'audit
- Observabilité: métriques clés (latence LLM, taux d'erreur outils, appels API/min), journaux centralisés, traces sur les parcours critiques
- Portabilité des données: export/suppression des données utilisateur (portabilité, droit à l'oubli)

### Table 2 - Sommaire des changements de la solution technique

| Description des modifications, retraits, ajouts requis                                      | Ajout/modification/retrait |
| ------------------------------------------------------------------------------------------- | -------------------------- |
| Conteneurisation des services (API, Agent, Workers)                                         | Ajout                      |
| Mise en place d'un proxy inverse (TLS, HTTP/2)                                              | Ajout                      |
| Chiffrement en transit (TLS) et au repos (DB chiffrée/volumes)                              | Ajout                      |
| PostgreSQL managé/haute fiabilité (remplace DB locale Dev)                                  | Modification               |
| Ajout d'un cache/queue Redis (sessions, rate-limit, tâches)                                 | Ajout                      |
| Workers d'arrière-plan (scheduler/rappels, sync intégrations)                               | Ajout                      |
| Observabilité: métriques (Prometheus), tableaux (Grafana), logs centralisés (Loki/ELK)      | Ajout                      |
| Centralisation et rotation des logs (niveau App + Proxy)                                    | Ajout                      |
| Gestion des secrets (Docker secrets/gestionnaire de secrets)                                | Ajout                      |
| Sauvegardes DB chiffrées et plan de reprise (RPO/RTO définis)                               | Ajout                      |
| Rate-limiting, timeouts, retries, et circuit breakers pour intégrations externes            | Ajout                      |
| Authentification des utilisateurs (MFA optionnel) et autorisation (RBAC minimal individuel) | Ajout                      |
| Politique de rétention/portabilité des données (export/suppression)                         | Ajout                      |
| Pipeline CI/CD (build images, scans, tests, déploiement)                                    | Ajout                      |
| Paramétrage d'environnements séparés (Dev/Stage/Prod)                                       | Ajout                      |
| Optimisations de performance LLM (mise en cache, compression/prompts, budgets d'appels)     | Ajout                      |

### Points techniques clés (fondation actuelle → cible finale)

#### **Foundation (existant) - Architecture actuelle en développement :**

- **AgentCore/Runner/Planner** : Orchestration complète avec gestion d'état, exécution d'outils et planification LLM
- **Système LTM avancé** : Mémoire à long terme avec optimisation continue et apprentissage automatique
- **Intégrations outils** : Registry d'outils extensible (calendrier, emails, notes, recherche, YouTube, Notion)
- **Stockage utilisateur** : Base SQLite avec modèles de données complets (14 tables incluant objectifs, tâches, courses, dépenses)
- **Prompts optimisés TDAH** : Prompts spécialisés pour la compréhension des défis cognitifs TDAH
- **Gestion des conversations** : Système de résumption automatique avec gestion d'état persistant
- **Système RAG intégré** : Recherche sémantique dans la base de connaissances avec embeddings Gemini
- **Interface SMS principale** : Intégration Twilio pour accès universel sans internet requis
- **Interface CLI** : Commandes système de base pour la gestion administrative

#### **Cible finale - Architecture d'exploitation de production :**

- **Séparation claire des services** : API FastAPI, Service Agent, Workers Celery avec responsabilités distinctes
- **Observabilité de production** : Stack complet Prometheus + Grafana + Loki + Jaeger avec métriques, logs et traces
- **Sécurité renforcée** : TLS 1.3, chiffrement AES-256 au repos, authentification MFA, isolation stricte des données
- **Résilience des intégrations** : Rate limiting, circuit breakers, retry automatique pour toutes les APIs externes
- **Portabilité des données** : Export/suppression des données utilisateur, conformité GDPR, droit à l'oubli
- **Haute disponibilité** : Réplication PostgreSQL, cluster Redis, sauvegardes automatisées avec RPO 24h/RTO 30min
- **Scalabilité** : Architecture conteneurisée Docker avec orchestration et auto-scaling
- **Monitoring 24/7** : Alertes automatiques, détection d'anomalies, escalade des incidents
- **Pipeline CI/CD** : Déploiement automatisé, tests de sécurité, rollback automatique
- **Gestion des secrets** : Rotation automatique des clés, stockage sécurisé, audit trail complet

## 2.2 Implémentation

### 2.2.1 Schéma d'implémentation

En général, le schéma d'implémentation de la plateforme d'infrastructure Production est le même pour toutes les plateformes. Il est montré ici avec la description de ses composants et des interactions entre eux.

**Figure 1 - Schéma d'implémentation**

```mermaid
graph TB
    %% External Users and Services
    subgraph "External Multi-Users"
        USER1[👤 Utilisateur TDAH 1]
        USER2[👤 Utilisateur TDAH 2]
        USER3[👤 Utilisateur TDAH 3]
        TWILIO[📱 Twilio SMS<br/>Numéro unique + Identification]
        GEMINI[🤖 Google Gemini API<br/>Clé API organisation]
        GRAPH[📅 Microsoft Graph API<br/>OAuth par utilisateur]
        GMAIL[📧 Gmail API<br/>OAuth par utilisateur]
        NOTION[📝 Notion API<br/>OAuth par utilisateur]
        YOUTUBE[🎥 YouTube API<br/>OAuth par utilisateur]
        INTERNET[🌐 Internet APIs<br/>Recherche publique]
    end

    %% Load Balancer and Security Layer
    subgraph "Security & Load Balancing"
        NGINX[🛡️ Nginx Proxy<br/>TLS 1.3, Rate Limiting<br/>HTTP/2, Compression]
        WAF[🛡️ WAF Rules<br/>DDoS Protection<br/>Multi-utilisateurs]
    end

    %% Main Application Services
    subgraph "Application Services Multi-Users"
        API[🚀 FastAPI Backend<br/>Authentication OAuth, Rate Limiting<br/>User Management, RBAC, Isolation]
        AGENT[🧠 Agent Service<br/>AgentCore + Runner + Planner<br/>Orchestration centrale, ToolRegistry<br/>Contexte utilisateur isolé]
        WORKERS[⚙️ Background Workers<br/>Celery + Redis Queue<br/>Tâches asynchrones, Rappels, Sync<br/>OAuth refresh, Isolation]
        OAUTH_MGR[🔑 OAuth Manager<br/>Gestion progressive<br/>Activation granulaire<br/>Isolation utilisateur]
    end

    %% Data Layer
    subgraph "Data Layer Multi-Users"
        POSTGRES[(🗄️ PostgreSQL<br/>User Data, LTM, Events<br/>Encrypted at Rest<br/>Isolation stricte par utilisateur)]
        REDIS[(🔴 Redis<br/>Cache, Sessions, Queue<br/>Rate Limiting Data<br/>Isolation par utilisateur)]
    end

    %% Monitoring and Observability
    subgraph "Observability Multi-Users"
        PROMETHEUS[📊 Prometheus<br/>Metrics Collection<br/>Par utilisateur]
        GRAFANA[📈 Grafana<br/>Dashboards, Alerts<br/>Multi-utilisateurs]
        LOKI[📝 Loki<br/>Log Aggregation<br/>Isolation utilisateur]
        JAEGER[🔍 Jaeger<br/>Distributed Tracing<br/>Contexte utilisateur]
    end

    %% CI/CD and Management
    subgraph "DevOps & Management"
        DOCKER[🐳 Docker Compose<br/>Orchestration, Secrets<br/>Multi-utilisateurs]
        CI_CD[🔄 CI/CD Pipeline<br/>Build, Test, Deploy<br/>Tests multi-utilisateurs]
        BACKUP[💾 Backup Service<br/>Encrypted Backups<br/>RPO: 24h, RTO: 30m<br/>Isolation utilisateur]
    end

    %% ===== FLUX PRINCIPAL : Multi-utilisateurs avec OAuth =====
    USER1 --> NGINX
    USER2 --> NGINX
    USER3 --> NGINX
    TWILIO --> NGINX

    NGINX --> WAF
    WAF --> API

    %% ===== AGENT EST LE POINT CENTRAL D'ORCHESTRATION =====
    API --> AGENT
    API --> OAUTH_MGR

    %% ===== AGENT ORCHESTRE TOUS LES SERVICES ET OUTILS =====
    AGENT --> GEMINI
    AGENT --> POSTGRES
    AGENT --> REDIS

    %% ===== OAuth Manager gère les intégrations par utilisateur =====
    OAUTH_MGR --> GRAPH
    OAUTH_MGR --> GMAIL
    OAUTH_MGR --> NOTION
    OAUTH_MGR --> YOUTUBE

    %% ===== AGENT COORDONNE AVEC LES WORKERS POUR LES TÂCHES ASYNCHRONES =====
    AGENT --> WORKERS
    WORKERS --> POSTGRES
    WORKERS --> REDIS

    %% ===== WORKERS ONT ACCÈS LIMITÉ AUX OUTILS (seulement si requis) =====
    WORKERS --> GRAPH
    WORKERS --> GMAIL
    WORKERS --> NOTION
    WORKERS --> YOUTUBE
    WORKERS --> INTERNET

    %% ===== MONITORING DE TOUS LES SERVICES =====
    API --> PROMETHEUS
    AGENT --> PROMETHEUS
    WORKERS --> PROMETHEUS
    OAUTH_MGR --> PROMETHEUS
    POSTGRES --> PROMETHEUS
    REDIS --> PROMETHEUS

    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA
    JAEGER --> GRAFANA

    %% ===== GESTION DOCKER ET BACKUP =====
    DOCKER --> API
    DOCKER --> AGENT
    DOCKER --> WORKERS
    DOCKER --> OAUTH_MGR
    DOCKER --> POSTGRES
    DOCKER --> REDIS

    CI_CD --> DOCKER
    BACKUP --> POSTGRES

    %% ===== STYLING =====
    classDef external fill:#e1f5fe
    classDef security fill:#fff3e0
    classDef app fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef monitoring fill:#fce4ec
    classDef devops fill:#f1f8e9
    classDef oauth fill:#ffebee

    class USER1,USER2,USER3,TWILIO,GEMINI,GRAPH,GMAIL,NOTION,YOUTUBE,INTERNET external
    class NGINX,WAF security
    class API,AGENT,WORKERS,OAUTH_MGR app
    class POSTGRES,REDIS data
    class PROMETHEUS,GRAFANA,LOKI,JAEGER monitoring
    class DOCKER,CI_CD,BACKUP devops
    class OAUTH_MGR oauth
```

### 2.2.2 Description des noeuds technologiques de traitement

**Tableau 3 - Description des noeuds technologiques de traitement**

| Identification du noeud technologique de traitement | Description                                                                                                    | Caractéristiques                                                                                  | Contexte                                                    |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| **Nginx Proxy (NGINX)**                             | Proxy inverse avec TLS 1.3, compression HTTP/2, rate limiting et protection DDoS                               | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, haute disponibilité               |
| **FastAPI Backend (API)**                           | Service principal d'API avec authentification, gestion des utilisateurs et RBAC                                | **Nature du changement infrastructure**: Modification<br>**Type d'hébergement**: Container Docker | **Contexte**: Production, multi-utilisateurs                |
| **Agent Service (AGENT)**                           | Service d'orchestration centrale (AgentCore + Runner + Planner) avec ToolRegistry, gestion LTM et RAG          | **Nature du changement infrastructure**: Modification<br>**Type d'hébergement**: Container Docker | **Contexte**: Production, orchestration centrale du système |
| **Background Workers (WORKERS)**                    | Services asynchrones pour tâches planifiées, rappels et synchronisation, avec accès limité aux outils externes | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, tâches d'arrière-plan             |
| **PostgreSQL Database (POSTGRES)**                  | Base de données principale avec chiffrement au repos et haute disponibilité                                    | **Nature du changement infrastructure**: Modification<br>**Type d'hébergement**: Container Docker | **Contexte**: Production, données utilisateur               |
| **Redis Cache/Queue (REDIS)**                       | Cache en mémoire et file d'attente pour sessions et rate limiting                                              | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, performance et scalabilité        |
| **Prometheus (PROMETHEUS)**                         | Collecte de métriques et monitoring des services                                                               | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, observabilité                     |
| **Grafana (GRAFANA)**                               | Tableaux de bord et alertes pour le monitoring                                                                 | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, visualisation des métriques       |
| **Loki (LOKI)**                                     | Agrégation et recherche de logs centralisés                                                                    | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, gestion des logs                  |
| **Jaeger (JAEGER)**                                 | Traçage distribué pour le debugging et l'optimisation                                                          | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, observabilité avancée             |
| **Docker Compose (DOCKER)**                         | Orchestration des containers et gestion des secrets                                                            | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Host System             | **Contexte**: Production, déploiement et gestion            |
| **CI/CD Pipeline (CI_CD)**                          | Pipeline automatisé de build, test et déploiement                                                              | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: External Service        | **Contexte**: Production, développement continu             |
| **Backup Service (BACKUP)**                         | Service de sauvegarde chiffrée avec RPO 24h et RTO 30m                                                         | **Nature du changement infrastructure**: Ajout<br>**Type d'hébergement**: Container Docker        | **Contexte**: Production, continuité des affaires           |

### 2.2.3 Liens entre les noeuds technologiques de traitement

**Tableau 4 - Description des liens entre les noeuds technologiques de traitement**

| Identification du lien     | Noeuds touchés               | Description                                     | Caractéristiques                       | Protocole d'échange de données utilisé | Nature du lien/chiffrement                    |
| -------------------------- | ---------------------------- | ----------------------------------------------- | -------------------------------------- | -------------------------------------- | --------------------------------------------- |
| **Lien utilisateur-proxy** | USER → NGINX                 | Communication utilisateur avec le proxy inverse | **Nature du changement**: Ajout        | HTTPS/TLS 1.3                          | Chiffré en transit                            |
| **Lien Twilio-proxy**      | TWILIO → NGINX               | Webhooks SMS de Twilio vers le proxy            | **Nature du changement**: Ajout        | HTTPS/TLS 1.3                          | Chiffré en transit                            |
| **Lien proxy-API**         | NGINX → API                  | Routage des requêtes du proxy vers l'API        | **Nature du changement**: Ajout        | HTTP/2                                 | Non chiffré (réseau interne)                  |
| **Lien API-Agent**         | API → AGENT                  | Communication entre l'API et le service Agent   | **Nature du changement**: Ajout        | HTTP/2                                 | Non chiffré (réseau interne)                  |
| **Lien Agent-Workers**     | AGENT → WORKERS              | Coordination des tâches asynchrones par l'Agent | **Nature du changement**: Ajout        | HTTP/2                                 | Non chiffré (réseau interne)                  |
| **Lien Agent-LLM**         | AGENT → GEMINI               | Appels vers l'API Gemini pour traitement LLM    | **Nature du changement**: Modification | HTTPS/TLS 1.3                          | Chiffré en transit, rate limiting             |
| **Lien Workers-APIs**      | WORKERS → GRAPH/GMAIL/NOTION | Synchronisation avec les APIs externes          | **Nature du changement**: Modification | HTTPS/TLS 1.3                          | Chiffré en transit, circuit breakers          |
| **Lien services-DB**       | AGENT/WORKERS → POSTGRES     | Accès à la base de données PostgreSQL           | **Nature du changement**: Modification | TCP/SSL                                | Chiffré en transit, isolation par utilisateur |
| **Lien services-Redis**    | AGENT/WORKERS → REDIS        | Cache et file d'attente Redis                   | **Nature du changement**: Ajout        | TCP                                    | Non chiffré (réseau interne)                  |
| **Lien monitoring**        | Services → PROMETHEUS        | Collecte de métriques Prometheus                | **Nature du changement**: Ajout        | HTTP                                   | Non chiffré (réseau interne)                  |
| **Lien logs**              | Services → LOKI              | Agrégation des logs vers Loki                   | **Nature du changement**: Ajout        | HTTP                                   | Non chiffré (réseau interne)                  |
| **Lien tracing**           | Services → JAEGER            | Traçage distribué vers Jaeger                   | **Nature du changement**: Ajout        | HTTP                                   | Non chiffré (réseau interne)                  |
| **Lien Docker**            | DOCKER → Services            | Orchestration et gestion des containers         | **Nature du changement**: Ajout        | Docker API                             | Non chiffré (host local)                      |
| **Lien backup**            | BACKUP → POSTGRES            | Sauvegarde chiffrée de la base de données       | **Nature du changement**: Ajout        | TCP/SSL                                | Chiffré en transit et au repos                |

### 2.2.4 Spécifications techniques détaillées

#### **Configuration Docker Compose**

```yaml
version: "3.8"
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - agent
    restart: unless-stopped

  api:
    build: ./src
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/personal_assistant
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  agent:
    build: ./src
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@postgres:5432/personal_assistant
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  oauth_manager:
    build: ./src
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/personal_assistant
      - REDIS_URL=redis://redis:6379
      - MICROSOFT_CLIENT_ID=${MICROSOFT_CLIENT_ID}
      - MICROSOFT_CLIENT_SECRET=${MICROSOFT_CLIENT_SECRET}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - NOTION_CLIENT_ID=${NOTION_CLIENT_ID}
      - NOTION_CLIENT_SECRET=${NOTION_CLIENT_SECRET}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  workers:
    build: ./src
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/personal_assistant
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=personal_assistant
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    secrets:
      - db_password
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki
    restart: unless-stopped

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
  loki_data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

#### **Configuration Nginx (Proxy inverse)**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api:8000;
    }

    upstream agent_backend {
        server agent:8001;
    }

    upstream oauth_backend {
        server oauth_manager:8002;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=agent:10m rate=5r/s;
    limit_req_zone $binary_remote_addr zone=oauth:10m rate=2r/s;

    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Agent routes
        location /agent/ {
            limit_req zone=agent burst=10 nodelay;
            proxy_pass http://agent_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # OAuth routes
        location /oauth/ {
            limit_req zone=oauth burst=10 nodelay;
            proxy_pass http://oauth_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

#### **Configuration Prometheus**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: "fastapi-api"
    static_configs:
      - targets: ["api:8000"]
    metrics_path: "/metrics"

  - job_name: "agent-service"
    static_configs:
      - targets: ["agent:8001"]
    metrics_path: "/metrics"

  - job_name: "oauth-manager"
    static_configs:
      - targets: ["oauth_manager:8002"]
    metrics_path: "/metrics"

  - job_name: "postgres"
    static_configs:
      - targets: ["postgres:5432"]

  - job_name: "redis"
    static_configs:
      - targets: ["redis:6379"]
```

### 2.2.5 Défis d'évolutivité SMS et solutions

**🚨 DÉCISION ARCHITECTURALE PRISE**: **Solution 1: Numéro unique avec identification utilisateur** ⭐ **APPROUVÉE ET IMPLÉMENTÉE**

**Enjeu critique identifié**: L'architecture SMS actuelle (un seul numéro Twilio) doit évoluer vers un modèle multi-utilisateurs avec identification utilisateur.

#### **2.2.5.1 Problème d'évolutivité SMS**

**Architecture actuelle (MVP - Single User)**:

- **Un numéro Twilio** → Un utilisateur unique
- **Webhook direct** → Assistant personnel direct
- **Configuration simple** → Fonctionne parfaitement pour un utilisateur

**Défi multi-utilisateurs**:

- **Multiple utilisateurs** nécessitent **identification et routage des SMS**
- **Coûts Twilio** → Un seul numéro (~$1/mois) + coûts d'utilisation
- **Complexité opérationnelle** → Gestion de l'identification utilisateur et routage
- **Isolation des données** → Séparation stricte des conversations par utilisateur

#### **2.2.5.2 Solutions d'évolutivité SMS**

**✅ Solution 1: Numéro unique avec identification utilisateur** ⭐ **APPROUVÉE - Phase 2**

**Avantages**:

- **Coûts optimisés** : Un seul numéro Twilio (~$1/mois)
- **Simplicité opérationnelle** : Gestion d'un seul webhook
- **Scalabilité** : Support de 1000+ utilisateurs avec identification
- **Expérience utilisateur** : Interface SMS familière et simple
- **Isolation des données** : Séparation stricte des conversations par utilisateur

**Inconvénients**:

- **Complexité technique** : Système d'identification utilisateur
- **Maintenance** : Gestion de l'identification et du routage
- **Limitations** : Dépendance de la reconnaissance du numéro de téléphone

**Architecture technique approuvée**:

```mermaid
graph TB
    subgraph "Utilisateurs"
        USER1[👤 Utilisateur 1<br/>+1-555-0101]
        USER2[👤 Utilisateur 2<br/>+1-555-0102]
        USER3[👤 Utilisateur 3<br/>+1-555-0103]
    end

    subgraph "Twilio Single Number"
        TWILIO[📱 +1-555-0000<br/>Webhook: /webhook/sms<br/>Identification par numéro]
    end

    subgraph "SMS Router Service"
        ROUTER[🔄 SMS Router<br/>Identification utilisateur<br/>Routage vers Agent<br/>Isolation des données]
    end

    subgraph "Agent Service Multi-Users"
        AGENT[🧠 Agent Service<br/>Isolation par utilisateur<br/>LTM séparé<br/>Contexte utilisateur]
    end

    USER1 --> TWILIO
    USER2 --> TWILIO
    USER3 --> TWILIO

    TWILIO --> ROUTER
    ROUTER --> AGENT
```

**Solution 2: Numéros dédiés par utilisateur** 🔄 **Rejetée - Phase 2**

**Avantages**:

- **Isolation parfaite** des données utilisateur
- **Expérience utilisateur** identique à l'actuelle
- **Sécurité maximale** avec séparation des conversations

**Inconvénients**:

- **Coûts élevés** : $1/mois par numéro Twilio
- **Complexité** : Gestion de multiples webhooks
- **Maintenance** : Rotation et gestion des numéros
- **Non-scalable** : Coûts prohibitifs pour 1000+ utilisateurs

**Solution 3: Interface web principale + SMS secondaire** 🎯 **Phase 3**

**Avantages**:

- **Coûts optimisés** : SMS limité aux notifications critiques
- **Expérience riche** : Interface web complète
- **Scalabilité** : Support de milliers d'utilisateurs

**Inconvénients**:

- **Changement UX** : Perte de l'interface SMS principale
- **Complexité** : Développement d'interface web complète
- **Adoption** : Risque de résistance au changement

#### **2.2.5.3 Recommandation architecturale**

**✅ Phase 2 (Enterprise) - Solution 1: Numéro unique avec identification - APPROUVÉE**

- **Justification** : Maintien de l'expérience utilisateur actuelle avec coûts optimisés
- **Coûts** : Acceptables pour 1000+ utilisateurs (1 numéro ~$1/mois)
- **Complexité** : Gérée par l'équipe DevOps
- **Sécurité** : Isolation parfaite des données via identification
- **Statut** : **DÉCISION PRISE - Implémentation en cours**

**Phase 3 (SaaS) - Solution 3: Interface web + SMS secondaire**

- **Justification** : Scalabilité vers milliers d'utilisateurs
- **Coûts** : Optimisés pour la croissance
- **Complexité** : Développement d'interface web complète
- **Sécurité** : Maintien de l'isolation des données

#### **2.2.5.4 Impact sur l'architecture technique**

**Modifications requises dans Phase 2**:

1. **Service de routage SMS** : Nouveau composant pour identifier et router les SMS
2. **Système d'identification utilisateur** : Reconnaissance du numéro de téléphone
3. **Isolation des données** : Renforcement de la séparation des données par utilisateur
4. **Monitoring SMS** : Métriques par utilisateur et par numéro de téléphone
5. **Gestion des coûts** : Monitoring des coûts Twilio par utilisateur

**Nouveaux composants à ajouter**:

- **SMS Router Service** : Port 8003, routage des SMS par utilisateur
- **User Identification Service** : Service de reconnaissance des numéros de téléphone
- **User SMS Analytics** : Métriques d'utilisation SMS par utilisateur
- **Cost Management** : Suivi des coûts Twilio et optimisation

**Modifications des composants existants**:

- **FastAPI Backend** : Ajout des endpoints de gestion de l'identification SMS
- **Database Models** : Extension des modèles utilisateur pour les numéros de téléphone
- **Monitoring** : Ajout des métriques SMS et coûts Twilio

#### **2.2.5.5 Plan d'implémentation détaillé**

**Phase 2.1: Infrastructure SMS Router**

1. **Création du SMS Router Service**

   - Port 8003, service FastAPI dédié
   - Gestion de l'identification utilisateur par numéro de téléphone
   - Routage basé sur l'identification utilisateur

2. **User Identification Service**

   - API pour associer numéros de téléphone et utilisateurs
   - Gestion des numéros de téléphone multiples par utilisateur
   - Validation et vérification des numéros

3. **Database Schema Updates**
   - Table `user_phone_numbers` pour associer utilisateurs et numéros
   - Table `sms_usage_logs` pour le suivi des coûts
   - Table `user_identification_logs` pour l'audit de l'identification

**Phase 2.2: Intégration et Tests**

1. **Tests d'intégration**

   - Simulation de multiples utilisateurs avec un seul numéro Twilio
   - Validation du routage des SMS par identification
   - Tests de performance avec charge

2. **Monitoring et Alertes**
   - Métriques de performance du router
   - Alertes sur les coûts Twilio
   - Surveillance de la qualité de l'identification

**Phase 2.3: Déploiement et Migration**

1. **Migration des utilisateurs existants**

   - Attribution de numéros de téléphone uniques
   - Migration des conversations existantes
   - Tests de validation post-migration

2. **Documentation et Formation**
   - Guide d'administration de l'identification SMS
   - Procédures de gestion des coûts
   - Formation de l'équipe DevOps

## 2.3 Environnements

**Tableau 5 - Description des environnements d'infrastructure**

| Noms de l'environnement | Plateforme d'infrastructure            | Description ou informations pertinentes                                                                                              |
| ----------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Development (Dev)**   | Docker Compose sur machine locale      | Environnement de développement avec base de données locale, logs en console, pas de chiffrement, variables d'environnement dans .env |
| **Staging (Stage)**     | Docker Compose sur serveur dédié       | Environnement de test avec configuration de production, base de données de test, monitoring basique, chiffrement activé              |
| **Production (Prod)**   | Docker Compose sur serveur(s) dédié(s) | Environnement de production avec haute disponibilité, chiffrement complet, monitoring avancé, sauvegardes automatisées               |

### 2.3.1 Configuration des environnements

#### **Environnement Development (Dev)**

**Objectif**: Développement local et tests unitaires

**Configuration Docker Compose**:

```yaml
# docker-compose.dev.yml
version: "3.8"
services:
  api:
    build: ./src
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - DATABASE_URL=postgresql://dev_user:dev_pass@postgres:5432/personal_assistant_dev
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./src:/app/src # Hot reload
    ports:
      - "8000:8000" # Expose API locally

  oauth_manager:
    build: ./src
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - DATABASE_URL=postgresql://dev_user:dev_pass@postgres:5432/personal_assistant_dev
      - REDIS_URL=redis://redis:6379
      - MICROSOFT_CLIENT_ID=${MICROSOFT_CLIENT_ID}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - NOTION_CLIENT_ID=${NOTION_CLIENT_ID}
    volumes:
      - ./src:/app/src # Hot reload
    ports:
      - "8002:8002" # Expose OAuth Manager locally

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=personal_assistant_dev
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=dev_pass
    ports:
      - "5432:5432" # Expose DB locally

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379" # Expose Redis locally

volumes:
  postgres_dev_data:
```

**Variables d'environnement (.env.dev)**:

```bash
# Development Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/personal_assistant_dev

# Redis
REDIS_URL=redis://localhost:6379

# External APIs (test keys)
GEMINI_API_KEY=your_test_gemini_key
TWILIO_ACCOUNT_SID=your_test_twilio_sid
TWILIO_AUTH_TOKEN=your_test_twilio_token

# OAuth Client IDs (development)
MICROSOFT_CLIENT_ID=your_dev_microsoft_client_id
GOOGLE_CLIENT_ID=your_dev_google_client_id
NOTION_CLIENT_ID=your_dev_notion_client_id

# Logging
LOG_TO_FILE=false
LOG_TO_CONSOLE=true
```

**Caractéristiques**:

- Base de données locale avec données de test
- Logs en console pour debugging
- Pas de chiffrement des données
- Hot reload du code source
- Ports exposés localement pour debugging

#### **Environnement Staging (Stage)**

**Objectif**: Tests d'intégration et validation de production

**Configuration Docker Compose**:

```yaml
# docker-compose.stage.yml
version: "3.8"
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/stage.conf:/etc/nginx/nginx.conf
      - ./ssl/stage:/etc/nginx/ssl

  api:
    build: ./src
    environment:
      - ENVIRONMENT=staging
      - DEBUG=false
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://stage_user:${DB_PASSWORD}@postgres:5432/personal_assistant_stage
      - REDIS_URL=redis://redis:6379
    secrets:
      - db_password
    restart: unless-stopped

  oauth_manager:
    build: ./src
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=postgresql://stage_user:${DB_PASSWORD}@postgres:5432/personal_assistant_stage
      - REDIS_URL=redis:redis:6379
      - MICROSOFT_CLIENT_ID=${MICROSOFT_CLIENT_ID}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - NOTION_CLIENT_ID=${NOTION_CLIENT_ID}
    secrets:
      - db_password
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=personal_assistant_stage
      - POSTGRES_USER=stage_user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_stage_data:/var/lib/postgresql/data
      - ./backups/stage:/backups

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_stage_data:/data

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/stage:/etc/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

volumes:
  postgres_stage_data:
  redis_stage_data:

secrets:
  db_password:
    file: ./secrets/stage/db_password.txt
```

**Variables d'environnement (.env.stage)**:

```bash
# Staging Environment
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Database
DB_PASSWORD=secure_stage_password

# Redis
REDIS_PASSWORD=secure_redis_password

# External APIs (staging keys)
GEMINI_API_KEY=your_staging_gemini_key
TWILIO_ACCOUNT_SID=your_staging_twilio_sid
TWILIO_AUTH_TOKEN=your_staging_twilio_token

# OAuth Client IDs (staging)
MICROSOFT_CLIENT_ID=your_staging_microsoft_client_id
GOOGLE_CLIENT_ID=your_staging_google_client_id
NOTION_CLIENT_ID=your_staging_notion_client_id

# Monitoring
GRAFANA_PASSWORD=secure_grafana_password

# Logging
LOG_TO_FILE=true
LOG_TO_CONSOLE=false
LOG_DIR=logs/stage
```

**Caractéristiques**:

- Configuration similaire à la production
- Base de données de test avec données réalistes
- Monitoring basique (Prometheus + Grafana)
- Chiffrement des données activé
- Secrets gérés via Docker secrets

#### **Environnement Production (Prod)**

**Objectif**: Service en production avec haute disponibilité

**Configuration Docker Compose**:

```yaml
# docker-compose.prod.yml
version: "3.8"
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf
      - ./ssl/prod:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    restart: unless-stopped

  api:
    build: ./src
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=WARNING
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/personal_assistant_prod
      - REDIS_URL=redis://redis:6379
    secrets:
      - db_password
      - api_secret_key
    restart: unless-stopped
    deploy:
      replicas: 2

  agent:
    build: ./src
    environment:
      - ENVIRONMENT=production
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/personal_assistant_prod
    secrets:
      - db_password
      - gemini_api_key
    restart: unless-stopped
    deploy:
      replicas: 2

  oauth_manager:
    build: ./src
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/personal_assistant_prod
      - REDIS_URL=redis://redis:6379
      - MICROSOFT_CLIENT_ID=${MICROSOFT_CLIENT_ID}
      - MICROSOFT_CLIENT_SECRET=${MICROSOFT_CLIENT_SECRET}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - NOTION_CLIENT_ID=${NOTION_CLIENT_ID}
      - NOTION_CLIENT_SECRET=${NOTION_CLIENT_SECRET}
    secrets:
      - db_password
      - microsoft_client_secret
      - google_client_secret
      - notion_client_secret
    restart: unless-stopped
    deploy:
      replicas: 2

  workers:
    build: ./src
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/personal_assistant_prod
      - REDIS_URL=redis://redis:6379
    secrets:
      - db_password
      - redis_password
    restart: unless-stopped
    deploy:
      replicas: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=personal_assistant_prod
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups/prod:/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_prod_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prod:/etc/prometheus
      - prometheus_prod_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_prod_data:/var/lib/grafana
    restart: unless-stopped

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki_prod_data:/loki
    restart: unless-stopped

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    restart: unless-stopped

  backup:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - ./backups/prod:/backups
      - postgres_prod_data:/var/lib/postgresql/data
    command: |
      sh -c '
      while true; do
        pg_dump -h postgres -U prod_user -d personal_assistant_prod > /backups/backup_$(date +%Y%m%d_%H%M%S).sql
        # Backup OAuth Manager data
        pg_dump -h postgres -U prod_user -d personal_assistant_prod -t oauth_tokens -t oauth_integrations > /backups/oauth_backup_$(date +%Y%m%d_%H%M%S).sql
        sleep 86400
      done
      '
    restart: unless-stopped

volumes:
  postgres_prod_data:
  redis_prod_data:
  prometheus_prod_data:
  grafana_prod_data:
  loki_prod_data:

secrets:
  db_password:
    file: ./secrets/prod/db_password.txt
  api_secret_key:
    file: ./secrets/prod/api_secret_key.txt
  gemini_api_key:
    file: ./secrets/prod/gemini_api_key.txt
  redis_password:
    file: ./secrets/prod/redis_password.txt
  microsoft_client_secret:
    file: ./secrets/prod/microsoft_client_secret.txt
  google_client_secret:
    file: ./secrets/prod/google_client_secret.txt
  notion_client_secret:
    file: ./secrets/prod/notion_client_secret.txt
```

**Variables d'environnement (.env.prod)**:

```bash
# Production Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database
DB_PASSWORD=very_secure_prod_password

# Redis
REDIS_PASSWORD=very_secure_redis_password

# External APIs (production keys)
GEMINI_API_KEY=your_production_gemini_key
TWILIO_ACCOUNT_SID=your_production_twilio_sid
TWILIO_AUTH_TOKEN=your_production_twilio_token

# OAuth Client IDs (production)
MICROSOFT_CLIENT_ID=your_production_microsoft_client_id
GOOGLE_CLIENT_ID=your_production_google_client_id
NOTION_CLIENT_ID=your_production_notion_client_id

# Monitoring
GRAFANA_PASSWORD=very_secure_grafana_password

# Logging
LOG_TO_FILE=true
LOG_TO_CONSOLE=false
LOG_DIR=logs/prod

# Security
API_SECRET_KEY=very_secure_api_secret_key
```

**Caractéristiques**:

- Configuration de production complète
- Réplication des services (API: 2, Agent: 2, Workers: 3)
- Monitoring avancé (Prometheus + Grafana + Loki + Jaeger)
- Chiffrement complet des données
- Sauvegardes automatisées (RPO: 24h, RTO: 30m)
- Secrets gérés via Docker secrets
- Logs centralisés et rotation automatique

### 2.3.2 Gestion des secrets et variables d'environnement

#### **Structure des secrets**

```
secrets/
├── dev/
│   └── .env (variables en clair pour développement)
├── stage/
│   ├── db_password.txt
│   ├── redis_password.txt
│   ├── grafana_password.txt
│   ├── microsoft_client_secret.txt
│   ├── google_client_secret.txt
│   └── notion_client_secret.txt
└── prod/
    ├── db_password.txt
    ├── api_secret_key.txt
    ├── gemini_api_key.txt
    ├── redis_password.txt
    ├── grafana_password.txt
    ├── microsoft_client_secret.txt
    ├── google_client_secret.txt
    └── notion_client_secret.txt
```

#### **Rotation des secrets**

- **Mots de passe de base de données**: Rotation tous les 90 jours
- **Clés API externes**: Rotation selon la politique des fournisseurs
- **Clés de chiffrement**: Rotation tous les 365 jours
- **Mots de passe d'administration**: Rotation tous les 180 jours
- **Secrets OAuth clients**: Rotation tous les 180 jours
- **Tokens OAuth utilisateur**: Rotation selon la politique des fournisseurs (Microsoft: 90 jours, Google: 1 an, Notion: permanent)

#### **Sécurité des environnements**

- **Development**: Variables en clair dans .env (pas de secrets), **OAuth client IDs en clair pour développement**
- **Staging**: Secrets gérés via Docker secrets, chiffrement des données, **OAuth client secrets sécurisés**
- **Production**: Secrets gérés via Docker secrets, chiffrement complet, rotation automatique, **OAuth client secrets avec rotation automatique**

### 2.3.3 Déploiement et maintenance

#### **Scripts de déploiement**

```bash
#!/bin/bash
# deploy.sh

ENVIRONMENT=$1

if [ "$ENVIRONMENT" = "dev" ]; then
    docker-compose -f docker-compose.dev.yml up -d
elif [ "$ENVIRONMENT" = "stage" ]; then
    docker-compose -f docker-compose.stage.yml up -d
elif [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    echo "Usage: ./deploy.sh [dev|stage|prod]"
    exit 1
fi
```

#### **Maintenance et mises à jour**

- **Développement**: Déploiement continu avec hot reload
- **Staging**: Déploiement manuel après validation des tests
- **Production**: Déploiement automatisé via CI/CD avec tests et rollback

#### **Monitoring et alertes**

- **Métriques système**: CPU, mémoire, disque, réseau
- **Métriques applicatives**: Latence API, taux d'erreur, appels LLM
- **Métriques base de données**: Connexions actives, requêtes lentes, taille des tables
- **Alertes**: Disponibilité des services, erreurs critiques, performance dégradée

## 2.4 Contexte opérationnel

### 2.4.1 Criticité opérationnelle, Disponibilité

**PDR (Plan de Reprise d'Activité)**: PDR 2 - Récupération en 24h avec perte de données maximale de 24h

**Tableau 6 - Criticité opérationnelle des applications ajoutées ou modifiées**

| Applications touchées          | OTR/OPR | PDR demandé | PDR livré | Criticité opérationnelle                                                        |
| ------------------------------ | ------- | ----------- | --------- | ------------------------------------------------------------------------------- |
| **FastAPI Backend (API)**      | OTR     | PDR 2       | PDR 2     | **Critique** - Service principal d'authentification et gestion des utilisateurs |
| **Agent Service (LLM)**        | OTR     | PDR 2       | PDR 2     | **Critique** - Service principal d'assistance TDAH et orchestration LLM         |
| **OAuth Manager**              | OTR     | PDR 2       | PDR 2     | **Critique** - Gestion des intégrations OAuth et activation granulaire          |
| **Background Workers**         | OTR     | PDR 2       | PDR 2     | **Élevée** - Synchronisation des données et rappels automatiques                |
| **Base de données PostgreSQL** | OTR     | PDR 2       | PDR 2     | **Critique** - Stockage des données utilisateur et mémoire LTM                  |
| **Cache Redis**                | OTR     | PDR 2       | PDR 2     | **Élevée** - Performance et sessions utilisateur                                |
| **Proxy Nginx**                | OTR     | PDR 2       | PDR 2     | **Élevée** - Point d'entrée et sécurité du système                              |

**Autres particularités**

**Tableau 7 - Plage de maintenance de la solution**

| Plages horaires de dispo requises (jours et heures)       | Plages de maintenance                                        | Exception et particularités                                                                                   |
| --------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| **Disponibilité**: 24h/7j (99.5% uptime)                  | **Maintenance planifiée**: Dimanche 02h00-06h00 (UTC)        | **Maintenance d'urgence**: 24h/7j avec notification utilisateur 2h à l'avance                                 |
| **Support utilisateur**: Lundi-Vendredi 08h00-18h00 (UTC) | **Maintenance corrective**: Mardi et Jeudi 03h00-05h00 (UTC) | **Périodes de pointe**: Éviter les maintenances entre 08h00-18h00 UTC (heures de travail)                     |
| **Monitoring**: 24h/7j                                    | **Mises à jour de sécurité**: Dès réception des patches      | **Fenêtres critiques**: Pas de maintenance pendant les heures de pointe TDAH (09h00-11h00 et 14h00-16h00 UTC) |

### 2.4.2 Robustesse

#### **Objectifs de disponibilité et performance**

- **Disponibilité globale**: 99.5% (4.38h d'indisponibilité par mois)
- **Temps de réponse P95**: < 2 secondes pour les requêtes utilisateur
- **Temps de réponse P99**: < 5 secondes pour les requêtes utilisateur
- **Temps de récupération (MTTR)**: < 30 minutes pour les incidents critiques
- **Temps de détection (MTTD)**: < 5 minutes pour les incidents critiques

#### **Mécanismes de résilience**

- **Redondance des services**: Réplication des instances API (2), Agent (2), **OAuth Manager (2)**, Workers (3)
- **Load balancing**: Distribution automatique de la charge via Nginx
- **Circuit breakers**: Protection contre les défaillances des APIs externes
- **Retry avec backoff exponentiel**: Gestion des erreurs temporaires
- **Rate limiting**: Protection contre la surcharge et les abus
- **Health checks**: Vérification continue de l'état des services

#### **Gestion des pannes**

- **Dégradation gracieuse**: Service partiel en cas de panne d'APIs externes
- **Mode hors ligne**: Cache des données utilisateur pour accès limité
- **Fallback LLM**: Utilisation de modèles de secours en cas de panne Gemini
- **Notifications automatiques**: Alertes immédiates en cas d'incident

### 2.4.3 Relève

**Tableau 8 - Composants à ajouter, modifier ou retirer de la relève**

| Type de composant              | Description                            | Type de relève    | Actions                                                           |
| ------------------------------ | -------------------------------------- | ----------------- | ----------------------------------------------------------------- |
| **Base de données PostgreSQL** | Données utilisateur, LTM, événements   | **Relève chaude** | **Ajouter** - Réplication en temps réel avec failover automatique |
| **Cache Redis**                | Sessions, cache, file d'attente        | **Relève chaude** | **Ajouter** - Cluster Redis avec réplication                      |
| **Stockage des fichiers**      | Logs, sauvegardes, uploads utilisateur | **Relève froide** | **Ajouter** - Stockage redondant avec réplication géographique    |
| **Configuration des services** | Variables d'environnement, secrets     | **Relève chaude** | **Ajouter** - Gestion centralisée des configurations              |
| **Monitoring et alertes**      | Métriques, logs, traces                | **Relève chaude** | **Ajouter** - Système de monitoring redondant                     |
| **APIs externes**              | Gemini, Graph, Gmail, Notion           | **Relève chaude** | **Modifier** - Intégration de fournisseurs alternatifs            |

#### **Stratégie de relève**

- **Relève chaude**: Base de données et cache avec failover automatique en < 30 secondes
- **Relève tiède**: Services applicatifs avec redémarrage automatique en < 5 minutes
- **Relève froide**: Données de sauvegarde avec restauration en < 24 heures
- **Site de secours**: Infrastructure de repli dans une zone géographique différente

### 2.4.4 Outils de gestion de surveillance TI

#### **Monitoring et observabilité**

- **Prometheus**: Collecte de métriques système et applicatives
- **Grafana**: Tableaux de bord et alertes
- **Loki**: Agrégation et recherche de logs centralisés
- **Jaeger**: Traçage distribué pour le debugging
- **AlertManager**: Gestion des alertes et notifications

#### **Métriques clés surveillées**

**Métriques système**:

- CPU, mémoire, disque, réseau
- Utilisation des containers Docker
- Performance des volumes de données

**Métriques applicatives**:

- Latence des APIs (P50, P95, P99)
- Taux d'erreur par endpoint
- Nombre de requêtes par minute
- Temps de réponse LLM Gemini
- Utilisation des outils externes

**Métriques base de données**:

- Connexions actives
- Requêtes lentes (> 1 seconde)
- Taille des tables et index
- Performance des requêtes LTM

**Métriques Redis**:

- Utilisation mémoire
- Nombre de connexions
- Latence des opérations
- Taux de hit/miss du cache

#### **Seuils d'alerte**

- **Critique**: Service indisponible, erreurs > 5%, latence > 10s
- **Élevé**: Performance dégradée, erreurs > 2%, latence > 5s
- **Moyen**: Utilisation élevée des ressources, latence > 2s
- **Faible**: Avertissements, utilisation > 80%

### 2.4.5 Sauvegardes

#### **Stratégie de sauvegarde**

- **Sauvegarde complète**: Quotidienne à 02h00 UTC
- **Sauvegarde incrémentale**: Toutes les 4 heures
- **Sauvegarde des logs**: Quotidienne avec rotation sur 30 jours
- **Sauvegarde de configuration**: À chaque modification

#### **Rétention des sauvegardes**

- **Sauvegardes quotidiennes**: 30 jours
- **Sauvegardes hebdomadaires**: 12 semaines
- **Sauvegardes mensuelles**: 12 mois
- **Sauvegardes annuelles**: 7 ans

#### **Récupération et tests**

- **RPO (Recovery Point Objective)**: 24 heures maximum
- **RTO (Recovery Time Objective)**: 30 minutes maximum
- **Tests de restauration**: Mensuels avec validation des données
- **Documentation de procédures**: Procédures détaillées pour chaque type de restauration

#### **Chiffrement et sécurité**

- **Chiffrement des sauvegardes**: AES-256 en transit et au repos
- **Authentification**: Accès restreint aux sauvegardes
- **Audit**: Traçabilité complète des accès et opérations
- **Stockage sécurisé**: Sauvegardes isolées de l'infrastructure principale

### 2.4.6 Autres

#### **Gestion des incidents**

- **Classification des incidents**: P1 (Critique), P2 (Élevé), P3 (Moyen), P4 (Faible)
- **Escalade automatique**: Notification des équipes selon la criticité
- **Procédures d'urgence**: Runbooks détaillés pour chaque type d'incident
- **Post-mortem**: Analyse des incidents avec plan d'amélioration

#### **Conformité et audit**

- **Journaux d'audit**: Conservation de tous les accès et modifications
- **Traçabilité**: Suivi complet des actions utilisateur et système
- **Conformité GDPR**: Gestion des données personnelles et droit à l'oubli
- **Rapports de conformité**: Génération automatique des rapports d'audit

#### **Formation et documentation**

- **Formation des équipes**: Sessions régulières sur les procédures opérationnelles
- **Documentation technique**: Mise à jour continue des procédures
- **Simulations d'incident**: Exercices réguliers de gestion de crise
- **Partage d'expérience**: Retours d'expérience et bonnes pratiques

#### **Évolution et maintenance**

- **Mises à jour de sécurité**: Application immédiate des patches critiques
- **Mises à jour fonctionnelles**: Planification et tests en staging
- **Gestion des versions**: Stratégie de déploiement avec rollback
- **Monitoring des dépendances**: Surveillance des vulnérabilités des composants tiers
