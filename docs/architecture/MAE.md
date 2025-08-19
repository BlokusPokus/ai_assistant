# Liste des tableaux

- Tableau 1: Document de référence
- Tableau 2: Sommaire des changements de la solution technique
- Tableau 3: Description des noeuds technologiques
- Tableau 4: Description des liens entre les noeuds technologiques de traitement
- Tableau 5: Description des environnements d'infrastructure
- Tableau 6: Criticité opérationnelle des applications ajoutées ou modifiées
- Tableau 7: Plage de maintenance de la solution
- Tableau 8: Composants à ajouter, modifier ou retirer de la relève
- Tableau 9: Environnements
- Tableau 10: Spécifications

# Liste des figures

- Figure 1: Schéma d'implémentation
- Figure 2: Schémas de répartition détaillée

# 1. Introduction

## 1.1 Objective du livrable

Le modèle d'architecture d'exploitation permet de définir les changements à apporter aux plateformes d'infrastructure technologiques de la solution, de la concption à l'exploitation de celle-ci.

## 1.2 But du projet

**Objectif principal** : Transformer l'infrastructure technologique de l'assistant personnel TDAH d'un environnement de développement local vers une plateforme d'exploitation de production robuste et sécurisée.

**Contexte** : L'assistant personnel TDAH nécessite une infrastructure d'exploitation de niveau entreprise pour supporter la production, incluant la conteneurisation, la sécurité renforcée, l'observabilité et la haute disponibilité.

**Solution** : Mise en place d'une architecture conteneurisée avec Docker, migration vers PostgreSQL, ajout de Redis, implémentation d'un proxy inverse sécurisé et déploiement d'une stack de monitoring complète pour l'exploitation en production.

## 1.3 Documents de référence

Fichier intrants de couts du project
Calculatrice des coûts pour les services du PaaS

## 1.4 Responsabilité de production du document

Conseiller en architecture de solutions d'exploitation
Analyste technologique d'exploitation
Expert d'architecture technologique

# 2. Solution technique

## 2.1 Aperçu

Cette sous-section résume les principaux changements requis aux infrastructures matérielles et logicielles afin de supporter la solution décrite dans le But du projet de ce document

### Vue - Aperçu technique cible

- Architecture conteneurisée (Docker) pour tous les services applicatifs
- Services principaux: API Backend (FastAPI), Service Agent (LLM orchestration), Workers asynchrones (scheduler/arrière-plan), Base de données PostgreSQL, Cache/Queue Redis, Proxy inverse (TLS), Observabilité (metrics/logs/traces), Gestion des secrets
- Intégrations externes: LLM (Gemini), Calendrier/Emails (Graph/Gmail), Notion/YouTube/Internet Tools; toutes les intégrations protégées par timeouts, retries, rate-limiting et circuit breakers
- Sécurité: TLS en transit, chiffrement au repos (DB), tokens d'API stockés de façon sécurisée, isolation stricte des données par utilisateur (multi-utilisateurs individuels, pas de collaboration d'équipe)
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
    subgraph "External"
        USER[👤 Utilisateur TDAH]
        TWILIO[📱 Twilio SMS]
        GEMINI[🤖 Google Gemini API]
        GRAPH[📅 Microsoft Graph API]
        GMAIL[📧 Gmail API]
        NOTION[📝 Notion API]
        YOUTUBE[🎥 YouTube API]
        INTERNET[🌐 Internet APIs]
    end

    %% Load Balancer and Security Layer
    subgraph "Security & Load Balancing"
        NGINX[🛡️ Nginx Proxy<br/>TLS 1.3, Rate Limiting<br/>HTTP/2, Compression]
        WAF[🛡️ WAF Rules<br/>DDoS Protection]
    end

    %% Main Application Services
    subgraph "Application Services"
        API[🚀 FastAPI Backend<br/>Authentication, Rate Limiting<br/>User Management, RBAC]
        AGENT[�� Agent Service<br/>AgentCore + Runner + Planner<br/>Orchestration centrale, ToolRegistry]
        WORKERS[⚙️ Background Workers<br/>Celery + Redis Queue<br/>Tâches asynchrones, Rappels, Sync]
    end

    %% Data Layer
    subgraph "Data Layer"
        POSTGRES[(🗄️ PostgreSQL<br/>User Data, LTM, Events<br/>Encrypted at Rest)]
        REDIS[(🔴 Redis<br/>Cache, Sessions, Queue<br/>Rate Limiting Data)]
    end

    %% Monitoring and Observability
    subgraph "Observability"
        PROMETHEUS[📊 Prometheus<br/>Metrics Collection]
        GRAFANA[📈 Grafana<br/>Dashboards, Alerts]
        LOKI[📝 Loki<br/>Log Aggregation]
        JAEGER[🔍 Jaeger<br/>Distributed Tracing]
    end

    %% CI/CD and Management
    subgraph "DevOps & Management"
        DOCKER[🐳 Docker Compose<br/>Orchestration, Secrets]
        CI_CD[🔄 CI/CD Pipeline<br/>Build, Test, Deploy]
        BACKUP[💾 Backup Service<br/>Encrypted Backups<br/>RPO: 24h, RTO: 30m]
    end

    %% ===== FLUX PRINCIPAL : Utilisateur → API → AGENT =====
    USER --> NGINX
    TWILIO --> NGINX

    NGINX --> WAF
    WAF --> API

    %% ===== AGENT EST LE POINT CENTRAL D'ORCHESTRATION =====
    API --> AGENT

    %% ===== AGENT ORCHESTRE TOUS LES SERVICES ET OUTILS =====
    AGENT --> GEMINI
    AGENT --> POSTGRES
    AGENT --> REDIS

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
    POSTGRES --> PROMETHEUS
    REDIS --> PROMETHEUS

    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA
    JAEGER --> GRAFANA

    %% ===== GESTION DOCKER ET BACKUP =====
    DOCKER --> API
    DOCKER --> AGENT
    DOCKER --> WORKERS
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

    class USER,TWILIO,GEMINI,GRAPH,GMAIL,NOTION,YOUTUBE,INTERNET external
    class NGINX,WAF security
    class API,AGENT,WORKERS app
    class POSTGRES,REDIS data
    class PROMETHEUS,GRAFANA,LOKI,JAEGER monitoring
    class DOCKER,CI_CD,BACKUP devops
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

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=agent:10m rate=5r/s;

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

  - job_name: "postgres"
    static_configs:
      - targets: ["postgres:5432"]

  - job_name: "redis"
    static_configs:
      - targets: ["redis:6379"]
```

### 2.2.5 Défis d'évolutivité SMS et solutions

**🚨 DÉCISION ARCHITECTURALE PRISE**: **Solution 1: Numéros dédiés par utilisateur** ⭐ **APPROUVÉE ET IMPLÉMENTÉE**

**Enjeu critique identifié**: L'architecture SMS actuelle (un seul numéro Twilio) ne peut pas évoluer vers un modèle multi-utilisateurs.

#### **2.2.5.1 Problème d'évolutivité SMS**

**Architecture actuelle (MVP - Single User)**:

- **Un numéro Twilio** → Un utilisateur unique
- **Webhook direct** → Assistant personnel direct
- **Configuration simple** → Fonctionne parfaitement pour un utilisateur

**Défi multi-utilisateurs**:

- **Multiple utilisateurs** nécessitent **multiple numéros de téléphone**
- **Coûts Twilio** → ~$1/mois par numéro + coûts d'utilisation
- **Complexité opérationnelle** → Gestion de multiples webhooks et routage
- **Isolation des données** → Séparation stricte des conversations par utilisateur

#### **2.2.5.2 Solutions d'évolutivité SMS**

**✅ Solution 1: Numéros dédiés par utilisateur** ⭐ **APPROUVÉE - Phase 2**

**Avantages**:

- **Isolation parfaite** des données utilisateur
- **Expérience utilisateur** identique à l'actuelle
- **Sécurité maximale** avec séparation des conversations
- **Scalabilité** jusqu'à 1000+ utilisateurs
- **Simplicité de maintenance** par rapport aux solutions complexes

**Inconvénients**:

- **Coûts** : $1/mois par numéro Twilio
- **Complexité** : Gestion de multiples webhooks
- **Maintenance** : Rotation et gestion des numéros

**Architecture technique approuvée**:

```mermaid
graph TB
    subgraph "Utilisateurs"
        USER1[👤 Utilisateur 1<br/>+1-555-0101]
        USER2[👤 Utilisateur 2<br/>+1-555-0102]
        USER3[👤 Utilisateur 3<br/>+1-555-0103]
    end

    subgraph "Twilio Numbers"
        TWILIO1[📱 +1-555-0101<br/>Webhook: /webhook/user1]
        TWILIO2[📱 +1-555-0102<br/>Webhook: /webhook/user2]
        TWILIO3[📱 +1-555-0103<br/>Webhook: /webhook/user3]
    end

    subgraph "SMS Router Service"
        ROUTER[🔄 SMS Router<br/>Identification utilisateur<br/>Routage vers Agent]
    end

    subgraph "Agent Service"
        AGENT[🧠 Agent Service<br/>Isolation par utilisateur<br/>LTM séparé]
    end

    USER1 --> TWILIO1
    USER2 --> TWILIO2
    USER3 --> TWILIO3

    TWILIO1 --> ROUTER
    TWILIO2 --> ROUTER
    TWILIO3 --> ROUTER

    ROUTER --> AGENT
```

**Solution 2: Numéro partagé avec identification** 🔄 **Rejetée - Phase 2**

**Avantages**:

- **Coûts réduits** : Un seul numéro Twilio
- **Simplicité** : Gestion d'un seul webhook
- **Rapidité** : Déploiement plus rapide

**Inconvénients**:

- **Complexité** : Identification utilisateur par SMS
- **Expérience utilisateur** : Moins intuitive
- **Sécurité** : Risque de confusion entre utilisateurs
- **Maintenance** : Gestion des codes utilisateur et parsing

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

**✅ Phase 2 (Enterprise) - Solution 1: Numéros dédiés - APPROUVÉE**

- **Justification** : Maintien de l'expérience utilisateur actuelle
- **Coûts** : Acceptables pour 100-500 utilisateurs ($100-500/mois)
- **Complexité** : Gérée par l'équipe DevOps
- **Sécurité** : Isolation parfaite des données
- **Statut** : **DÉCISION PRISE - Implémentation en cours**

**Phase 3 (SaaS) - Solution 3: Interface web + SMS secondaire**

- **Justification** : Scalabilité vers milliers d'utilisateurs
- **Coûts** : Optimisés pour la croissance
- **Complexité** : Développement d'interface web complète
- **Sécurité** : Maintien de l'isolation des données

#### **2.2.5.4 Impact sur l'architecture technique**

**Modifications requises dans Phase 2**:

1. **Service de routage SMS** : Nouveau composant pour identifier et router les SMS
2. **Gestion des numéros Twilio** : Service de provisionnement et gestion des numéros
3. **Isolation des données** : Renforcement de la séparation des données par utilisateur
4. **Monitoring SMS** : Métriques par numéro et par utilisateur
5. **Gestion des coûts** : Monitoring des coûts Twilio par utilisateur

**Nouveaux composants à ajouter**:

- **SMS Router Service** : Port 8003, routage des SMS par utilisateur
- **Twilio Number Manager** : Gestion des numéros et webhooks
- **User SMS Analytics** : Métriques d'utilisation SMS par utilisateur
- **Cost Management** : Suivi des coûts Twilio et optimisation

**Modifications des composants existants**:

- **FastAPI Backend** : Ajout des endpoints de gestion des numéros SMS
- **Database Models** : Extension des modèles utilisateur pour les numéros SMS
- **Monitoring** : Ajout des métriques SMS et coûts Twilio

#### **2.2.5.5 Plan d'implémentation détaillé**

**Phase 2.1: Infrastructure SMS Router**

1. **Création du SMS Router Service**

   - Port 8003, service FastAPI dédié
   - Gestion des webhooks multiples
   - Routage basé sur l'URL du webhook

2. **Twilio Number Manager**

   - API pour provisionner de nouveaux numéros
   - Gestion des webhooks par numéro
   - Monitoring des coûts par numéro

3. **Database Schema Updates**
   - Table `user_phone_numbers` pour associer utilisateurs et numéros
   - Table `sms_usage_logs` pour le suivi des coûts
   - Table `webhook_configurations` pour la gestion des webhooks

**Phase 2.2: Intégration et Tests**

1. **Tests d'intégration**

   - Simulation de multiples numéros Twilio
   - Validation du routage des SMS
   - Tests de performance avec charge

2. **Monitoring et Alertes**
   - Métriques de performance du router
   - Alertes sur les coûts Twilio
   - Surveillance de la qualité des webhooks

**Phase 2.3: Déploiement et Migration**

1. **Migration des utilisateurs existants**

   - Attribution de numéros dédiés
   - Migration des conversations existantes
   - Tests de validation post-migration

2. **Documentation et Formation**
   - Guide d'administration des numéros
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

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=personal_assistant_dev
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=dev_pass
    ports:
      - "5432:5432" # Expose DB locally
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

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
│   └── grafana_password.txt
└── prod/
    ├── db_password.txt
    ├── api_secret_key.txt
    ├── gemini_api_key.txt
    ├── redis_password.txt
    └── grafana_password.txt
```

#### **Rotation des secrets**

- **Mots de passe de base de données**: Rotation tous les 90 jours
- **Clés API externes**: Rotation selon la politique des fournisseurs
- **Clés de chiffrement**: Rotation tous les 365 jours
- **Mots de passe d'administration**: Rotation tous les 180 jours

#### **Sécurité des environnements**

- **Development**: Variables en clair dans .env (pas de secrets)
- **Staging**: Secrets gérés via Docker secrets, chiffrement des données
- **Production**: Secrets gérés via Docker secrets, chiffrement complet, rotation automatique

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

- **Redondance des services**: Réplication des instances API (2), Agent (2), Workers (3)
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

# 3. Sécurité

## 3.1 Risques et conformité

### 3.1.1 Requis de conformité

**Tableau 3.1.1 - Exigences de conformité et réglementations**

| Réglementation/Standard | Applicabilité     | Exigences clés                                                                                              | Statut de conformité         |
| ----------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------- |
| **GDPR (UE)**           | ✅ Obligatoire    | • Consentement explicite<br>• Droit à l'oubli<br>• Portabilité des données<br>• Notification des violations | 🔄 En cours d'implémentation |
| **CCPA (Californie)**   | ✅ Obligatoire    | • Transparence des données<br>• Droit de suppression<br>• Non-discrimination                                | 🔄 En cours d'implémentation |
| **PIPEDA (Canada)**     | ✅ Obligatoire    | • Consentement<br>• Limitation de la collecte<br>• Accès et correction                                      | 🔄 En cours d'implémentation |
| **SOC 2 Type II**       | 🎯 Cible 2025     | • Sécurité<br>• Disponibilité<br>• Traitement<br>• Confidentialité<br>• Intégrité                           | ❌ Non implémenté            |
| **ISO 27001**           | 🎯 Cible 2026     | • Système de gestion de la sécurité<br>• Contrôles de sécurité<br>• Évaluation des risques                  | ❌ Non implémenté            |
| **HIPAA**               | ❌ Non applicable | • Pas de données médicales sensibles<br>• Assistant de productivité uniquement                              | ✅ Conforme par design       |

**Exigences de conformité détaillées:**

#### **GDPR (Règlement Général sur la Protection des Données)**

- **Article 5 - Principes de traitement**: Licéité, loyauté, transparence, limitation des finalités, minimisation des données, exactitude, limitation de la conservation, intégrité et confidentialité
- **Article 6 - Base légale**: Consentement explicite de l'utilisateur pour le traitement des données
- **Article 17 - Droit à l'oubli**: Suppression complète des données utilisateur sur demande
- **Article 20 - Portabilité**: Export des données dans un format structuré et lisible par machine
- **Article 32 - Sécurité**: Chiffrement des données, authentification forte, audit trail

#### **CCPA (California Consumer Privacy Act)**

- **Section 1798.100**: Droit de savoir quelles données personnelles sont collectées
- **Section 1798.105**: Droit de suppression des données personnelles
- **Section 1798.110**: Droit de connaître les catégories de données collectées
- **Section 1798.115**: Droit de connaître les catégories de données vendues
- **Section 1798.125**: Non-discrimination pour l'exercice des droits

### 3.1.2 Mitigation des risques de sécurité identifiés

**Tableau 3.1.2 - Analyse des risques de sécurité et mitigation**

| Risque                               | Probabilité | Impact     | Niveau de risque | Mesures de mitigation                                                                                       | Responsable  |
| ------------------------------------ | ----------- | ---------- | ---------------- | ----------------------------------------------------------------------------------------------------------- | ------------ |
| **Violation de données utilisateur** | Moyenne     | Très élevé | **Élevé**        | • Chiffrement AES-256<br>• Isolation stricte des données<br>• Audit trail complet<br>• Tests de pénétration | CISO         |
| **Attaque par injection SQL**        | Faible      | Élevé      | **Moyen**        | • Requêtes préparées<br>• Validation des entrées<br>• WAF avec règles OWASP<br>• Tests automatisés          | Développeurs |
| **Exposition des clés API**          | Moyenne     | Élevé      | **Moyen**        | • Gestion des secrets Docker<br>• Rotation automatique<br>• Accès restreint<br>• Monitoring des accès       | DevOps       |
| **Attaque par déni de service**      | Moyenne     | Moyen      | **Moyen**        | • Rate limiting Nginx<br>• Protection DDoS<br>• Monitoring des ressources<br>• Auto-scaling                 | DevOps       |
| **Violation de l'authentification**  | Faible      | Très élevé | **Moyen**        | • MFA optionnel<br>• Sessions sécurisées<br>• Gestion des tokens JWT<br>• Détection d'anomalies             | Développeurs |
| **Exposition des données LTM**       | Faible      | Élevé      | **Moyen**        | • Chiffrement au repos<br>• Isolation par utilisateur<br>• Audit des accès<br>• Tests de sécurité           | Développeurs |

**Stratégie de mitigation globale:**

1. **Prévention**: Implémentation de contrôles de sécurité robustes
2. **Détection**: Monitoring continu et détection d'anomalies
3. **Réponse**: Procédures d'incident et plans de reprise
4. **Récupération**: Sauvegardes sécurisées et plans de restauration

## 3.2 Classification et gestion des données informationnelles

### 3.2.1 Classification et catégorisation des données

**Tableau 3.2.1 - Classification des données par niveau de sensibilité**

| Niveau de sensibilité    | Description                                       | Exemples de données                                                                | Contrôles de sécurité requis                                                            | Rétention                   |
| ------------------------ | ------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | --------------------------- |
| **Données publiques**    | Informations non sensibles                        | • Documentation produit<br>• Guides utilisateur<br>• Informations marketing        | • Validation des entrées<br>• Protection contre le spam                                 | Illimitée                   |
| **Données internes**     | Informations de l'organisation                    | • Métriques de performance<br>• Logs système<br>• Configuration                    | • Accès authentifié<br>• Audit des accès                                                | 2 ans                       |
| **Données personnelles** | Informations identifiant l'utilisateur            | • Nom, email, profil<br>• Préférences utilisateur<br>• Historique des interactions | • Chiffrement en transit et au repos<br>• Isolation stricte<br>• Consentement explicite | Selon demande utilisateur   |
| **Données sensibles**    | Informations nécessitant une protection renforcée | • Tokens d'API<br>• Clés de chiffrement<br>• Données d'authentification            | • Chiffrement AES-256<br>• Accès restreint<br>• Rotation automatique                    | Selon politique de sécurité |
| **Données critiques**    | Informations essentielles au fonctionnement       | • Configuration système<br>• Clés de chiffrement maîtres<br>• Sauvegardes système  | • Chiffrement maximum<br>• Accès privilégié<br>• Sauvegarde sécurisée                   | Permanente                  |

**Catégorisation par domaine fonctionnel:**

#### **Données utilisateur (PII - Personally Identifiable Information)**

- **Profil utilisateur**: Nom, email, préférences, paramètres
- **Données de session**: Tokens d'authentification, cookies sécurisés
- **Historique d'utilisation**: Interactions, préférences, patterns

#### **Données d'assistance (LTM - Long Term Memory)**

- **Mémoires contextuelles**: Conversations, objectifs, tâches
- **Métadonnées**: Tags, catégories, scores d'importance
- **Relations**: Liens entre informations, contextes

#### **Données d'intégration (APIs tierces)**

- **Tokens d'accès**: Clés API, tokens OAuth, refresh tokens
- **Configuration**: Paramètres de connexion, endpoints
- **Métadonnées**: Statut de synchronisation, dernière mise à jour

#### **Données système (Infrastructure)**

- **Logs**: Journaux d'audit, logs d'erreur, métriques
- **Configuration**: Variables d'environnement, paramètres
- **Monitoring**: Métriques de performance, alertes

### 3.2.2 Gestion des mécanismes et cycle de vie des données

**Tableau 3.2.2 - Cycle de vie des données et mécanismes de gestion**

| Phase du cycle de vie | Mécanismes de gestion                                                              | Contrôles de sécurité                                                                    | Rétention             | Disposition                                                                          |
| --------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------ |
| **Collecte**          | • Consentement explicite<br>• Minimisation des données<br>• Validation des entrées | • Chiffrement en transit (TLS 1.3)<br>• Validation des sources<br>• Audit de la collecte | N/A                   | N/A                                                                                  |
| **Traitement**        | • Isolation par utilisateur<br>• Chiffrement au repos<br>• Contrôle d'accès        | • Chiffrement AES-256<br>• RBAC strict<br>• Audit des opérations                         | Selon type de données | N/A                                                                                  |
| **Stockage**          | • Base de données chiffrée<br>• Sauvegardes sécurisées<br>• Réplication sécurisée  | • Chiffrement au repos<br>• Accès restreint<br>• Monitoring continu                      | Selon politique       | N/A                                                                                  |
| **Partage**           | • Isolation stricte<br>• Pas de partage inter-utilisateur<br>• Export contrôlé     | • Validation des destinataires<br>• Chiffrement des exports<br>• Audit des partages      | N/A                   | N/A                                                                                  |
| **Archivage**         | • Chiffrement des archives<br>• Accès restreint<br>• Rotation automatique          | • Chiffrement AES-256<br>• Contrôle d'accès<br>• Monitoring des accès                    | Selon politique       | N/A                                                                                  |
| **Suppression**       | • Suppression sécurisée<br>• Audit de suppression<br>• Confirmation utilisateur    | • Overwriting sécurisé<br>• Audit trail<br>• Validation de suppression                   | N/A                   | • Suppression physique<br>• Overwriting des données<br>• Confirmation de destruction |

**Mécanismes de gestion spécifiques:**

#### **Gestion du consentement**

- **Interface de consentement**: Formulaire clair et compréhensible
- **Granularité**: Consentement par type de données et finalité
- **Révocation**: Possibilité de retirer le consentement à tout moment
- **Audit**: Traçabilité complète des consentements et révocations

#### **Minimisation des données**

- **Collecte limitée**: Seules les données nécessaires sont collectées
- **Anonymisation**: Suppression des identifiants directs quand possible
- **Pseudonymisation**: Remplacement des identifiants par des alias
- **Aggrégation**: Regroupement des données pour réduire l'identifiabilité

#### **Qualité des données**

- **Validation**: Vérification de l'exactitude et de la cohérence
- **Nettoyage**: Suppression des données obsolètes ou incorrectes
- **Mise à jour**: Actualisation régulière des données utilisateur
- **Vérification**: Confirmation périodique de l'exactitude

## 3.3 Protection des données

### 3.3.1 Niveau d'assurance cryptographique exigé

**Tableau 3.3.1 - Exigences cryptographiques par type de données**

| Type de données           | Niveau d'assurance  | Algorithmes requis                                                                        | Longueur des clés                                                          | Rotation                                                         | Validation                                                                            |
| ------------------------- | ------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Données en transit**    | Niveau 1 (Standard) | • TLS 1.3<br>• Chiffrement symétrique AES-256<br>• Échange de clés ECDHE                  | • RSA: 2048 bits minimum<br>• ECDSA: 256 bits minimum<br>• AES: 256 bits   | • Certificats: 1 an<br>• Clés de session: Par session            | • Tests de pénétration<br>• Validation des certificats<br>• Monitoring des protocoles |
| **Données au repos (DB)** | Niveau 2 (Élevé)    | • AES-256-GCM<br>• Chiffrement des colonnes sensibles<br>• Hachage bcrypt (mots de passe) | • AES: 256 bits<br>• bcrypt: 12 rounds minimum<br>• Salt: 16 bytes minimum | • Clés de chiffrement: 1 an<br>• Mots de passe: Selon politique  | • Tests de résistance<br>• Audit des algorithmes<br>• Validation des implémentations  |
| **Sauvegardes**           | Niveau 2 (Élevé)    | • AES-256-CBC<br>• Chiffrement des fichiers<br>• Hachage SHA-256                          | • AES: 256 bits<br>• SHA-256: 256 bits<br>• IV: 16 bytes                   | • Clés de chiffrement: 1 an<br>• Hachage: Permanent              | • Tests d'intégrité<br>• Validation des sauvegardes<br>• Tests de restauration        |
| **Secrets système**       | Niveau 3 (Maximum)  | • AES-256-GCM<br>• Chiffrement des secrets<br>• Hachage SHA-512                           | • AES: 256 bits<br>• SHA-512: 512 bits<br>• Nonce: 12 bytes                | • Clés maîtres: 2 ans<br>• Secrets: 1 an<br>• Hachage: Permanent | • Tests de résistance<br>• Audit des secrets<br>• Validation des accès                |

**Standards cryptographiques de référence:**

#### **NIST (National Institute of Standards and Technology)**

- **FIPS 140-2**: Validation des modules cryptographiques
- **SP 800-57**: Gestion des clés cryptographiques
- **SP 800-131A**: Transitions vers des algorithmes cryptographiques sécurisés

#### **ANSSI (Agence Nationale de la Sécurité des Systèmes d'Information)**

- **Référentiel Général de Sécurité (RGS)**: Standards de sécurité français
- **Qualification des produits de sécurité**: Validation des solutions cryptographiques

#### **OWASP (Open Web Application Security Project)**

- **Top 10**: Vulnérabilités web les plus critiques
- **Cryptographic Storage**: Bonnes pratiques de stockage cryptographique

### 3.3.2 Protection des données en transit

**Mécanismes de protection en transit:**

#### **TLS (Transport Layer Security) 1.3**

- **Version minimale**: TLS 1.3 obligatoire
- **Versions interdites**: TLS 1.0, 1.1, 1.2 (dépréciés)
- **Suites de chiffrement**: ECDHE-RSA-AES256-GCM-SHA384 et supérieures
- **Échange de clés**: ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)
- **Authentification**: Certificats X.509 avec validation de chaîne

#### **Configuration Nginx (Proxy inverse)**

```nginx
# Configuration TLS 1.3 sécurisée
ssl_protocols TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA256;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;

# Headers de sécurité
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
```

#### **Protection des APIs internes**

- **Communication inter-services**: HTTP/2 avec validation des certificats
- **Authentification mutuelle**: mTLS pour les communications critiques
- **Chiffrement des métadonnées**: Headers sensibles chiffrés
- **Validation des endpoints**: Vérification des certificats des services

### 3.3.3 Protection des données au repos

**Mécanismes de protection au repos:**

#### **Chiffrement de la base de données**

- **PostgreSQL**: Chiffrement des tables sensibles avec pgcrypto
- **Chiffrement des colonnes**: Données critiques chiffrées individuellement
- **Clés de chiffrement**: Gestion centralisée via Docker secrets
- **Rotation des clés**: Changement automatique des clés de chiffrement

```sql
-- Exemple de chiffrement des colonnes sensibles
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Chiffrement des tokens d'API
UPDATE external_integrations
SET access_token = pgp_sym_encrypt(access_token, current_setting('app.encryption_key'))
WHERE user_id = $1;

-- Décryptage pour utilisation
SELECT pgp_sym_decrypt(access_token::bytea, current_setting('app.encryption_key'))
FROM external_integrations
WHERE user_id = $1;
```

#### **Chiffrement des fichiers et sauvegardes**

- **Sauvegardes**: Chiffrement AES-256-CBC avec clés dérivées
- **Logs sensibles**: Chiffrement des fichiers de logs contenant des PII
- **Uploads utilisateur**: Chiffrement des fichiers uploadés
- **Cache Redis**: Chiffrement des données sensibles en cache

#### **Gestion des clés de chiffrement**

- **Key Management Service**: Gestion centralisée des clés
- **Rotation automatique**: Changement périodique des clés
- **Backup sécurisé**: Sauvegarde chiffrée des clés maîtres
- **Récupération**: Procédures de récupération des clés

### 3.3.4 Gestion des certificats et clés cryptographiques

**Tableau 3.3.2 - Gestion des certificats et clés**

| Type de clé/certificat     | Gestion                                                                               | Rotation                                                                                       | Sauvegarde                                                               | Récupération                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| **Certificats TLS**        | • Let's Encrypt automatique<br>• Validation de chaîne<br>• Monitoring des expirations | • 90 jours (Let's Encrypt)<br>• Renouvellement automatique<br>• Validation post-renouvellement | • Certificats publics<br>• Clés privées chiffrées<br>• Stockage sécurisé | • Procédure de récupération<br>• Certificats de secours<br>• Tests de restauration |
| **Clés de chiffrement DB** | • Génération sécurisée<br>• Stockage Docker secrets<br>• Accès restreint              | • 1 an<br>• Rotation automatique<br>• Rechiffrement des données                                | • Clés chiffrées<br>• Stockage hors site<br>• Accès privilégié           | • Procédure de récupération<br>• Clés de secours<br>• Tests de restauration        |
| **Clés API externes**      | • Génération par fournisseur<br>• Stockage sécurisé<br>• Accès limité                 | • Selon fournisseur<br>• Rotation manuelle<br>• Validation post-rotation                       | • Clés chiffrées<br>• Stockage sécurisé<br>• Accès restreint             | • Contact fournisseur<br>• Génération de nouvelles clés<br>• Tests de connexion    |
| **Clés de signature JWT**  | • Génération sécurisée<br>• Stockage Docker secrets<br>• Accès restreint              | • 1 an<br>• Rotation automatique<br>• Invalidation des tokens                                  | • Clés chiffrées<br>• Stockage sécurisé<br>• Accès privilégié            | • Procédure de récupération<br>• Clés de secours<br>• Tests de signature           |

**Procédures de gestion des clés:**

#### **Génération sécurisée des clés**

```bash
# Génération de clés AES-256
openssl rand -hex 32

# Génération de clés RSA-2048
openssl genrsa -out private_key.pem 2048

# Génération de certificats auto-signés
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
```

#### **Rotation automatique des clés**

- **Monitoring**: Surveillance des dates d'expiration
- **Notification**: Alertes 30 jours avant expiration
- **Rotation**: Changement automatique des clés
- **Validation**: Tests post-rotation
- **Rollback**: Possibilité de revenir aux anciennes clés

## 3.4 Gestion des identités et des accès

### 3.4.1 Authentification

**Mécanismes d'authentification:**

#### **Authentification multi-facteurs (MFA)**

- **Facteur 1**: Mot de passe fort (bcrypt, 12 rounds minimum)
- **Facteur 2**: Code TOTP (Time-based One-Time Password)
- **Facteur 3**: SMS/Email de récupération (optionnel)
- **Implémentation**: Google Authenticator, Authy, ou équivalent

#### **Gestion des mots de passe**

- **Complexité**: Minimum 12 caractères, mélange de types
- **Hachage**: bcrypt avec salt unique, 12 rounds minimum
- **Validation**: Vérification de la force du mot de passe
- **Politique**: Expiration tous les 90 jours, historique des 5 derniers

```python
# Exemple de validation de mot de passe
import re
from passlib.hash import bcrypt

def validate_password(password):
    """Validation de la complexité du mot de passe"""
    if len(password) < 12:
        return False, "Le mot de passe doit contenir au moins 12 caractères"

    if not re.search(r"[A-Z]", password):
        return False, "Le mot de passe doit contenir au moins une majuscule"

    if not re.search(r"[a-z]", password):
        return False, "Le mot de passe doit contenir au moins une minuscule"

    if not re.search(r"\d", password):
        return False, "Le mot de passe doit contenir au moins un chiffre"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial"

    return True, "Mot de passe valide"

def hash_password(password):
    """Hachage sécurisé du mot de passe"""
    return bcrypt.hash(password, rounds=12)

def verify_password(password, hashed):
    """Vérification du mot de passe"""
    return bcrypt.verify(password, hashed)
```

#### **Gestion des sessions**

- **Tokens JWT**: Signature HMAC-SHA256, expiration configurable
- **Refresh tokens**: Rotation automatique des tokens d'accès
- **Invalidation**: Possibilité de révoquer les sessions
- **Monitoring**: Détection de sessions suspectes

### 3.4.2 Gestion des accès

**Système de contrôle d'accès:**

#### **RBAC (Role-Based Access Control)**

- **Rôles utilisateur**: Standard, Premium, Administrateur
- **Permissions**: Lecture, écriture, suppression, administration
- **Isolation**: Accès strictement limité aux données de l'utilisateur
- **Héritage**: Permissions héritées des rôles parents

**Tableau 3.4.1 - Matrice des permissions RBAC**

| Ressource                 | Rôle Standard         | Rôle Premium              | Rôle Administrateur          |
| ------------------------- | --------------------- | ------------------------- | ---------------------------- |
| **Profil utilisateur**    | R/W (propre profil)   | R/W (propre profil)       | R/W (tous les profils)       |
| **Données LTM**           | R/W (propres données) | R/W (propres données)     | R (toutes les données)       |
| **Objectifs et tâches**   | R/W (propres données) | R/W (propres données)     | R (toutes les données)       |
| **Intégrations externes** | R/W (propres données) | R/W (propres données)     | R (toutes les données)       |
| **Métriques système**     | Aucun accès           | R (métriques utilisateur) | R/W (toutes les métriques)   |
| **Logs système**          | Aucun accès           | Aucun accès               | R (tous les logs)            |
| **Configuration**         | Aucun accès           | Aucun accès               | R/W (toute la configuration) |

#### **ABAC (Attribute-Based Access Control)**

- **Attributs utilisateur**: Type de compte, date d'inscription, localisation
- **Attributs ressource**: Type de données, niveau de sensibilité, propriétaire
- **Attributs environnement**: Heure d'accès, localisation, type de connexion
- **Politiques**: Règles dynamiques basées sur les attributs

```python
# Exemple de politique ABAC
def check_access(user, resource, action, context):
    """Vérification des accès basée sur les attributs"""

    # Politique: Les utilisateurs premium peuvent accéder aux analytics avancés
    if (resource.type == "analytics" and
        resource.level == "advanced" and
        user.subscription_tier != "premium"):
        return False, "Accès aux analytics avancés réservé aux utilisateurs premium"

    # Politique: Accès limité aux heures de travail pour les données sensibles
    if (resource.sensitivity == "high" and
        context.hour < 8 or context.hour > 18):
        return False, "Accès aux données sensibles limité aux heures de travail"

    # Politique: Isolation stricte des données par utilisateur
    if (resource.owner_id != user.id and
        user.role != "administrator"):
        return False, "Accès limité aux données de l'utilisateur"

    return True, "Accès autorisé"
```

### 3.4.3 Contrôles des comptes à accès privilégié

**Gestion des comptes privilégiés:**

#### **Comptes administrateur**

- **Accès restreint**: Limitation aux opérations nécessaires
- **Authentification renforcée**: MFA obligatoire, mots de passe complexes
- **Monitoring**: Surveillance continue des actions privilégiées
- **Rotation**: Changement régulier des accès privilégiés

#### **Comptes de service**

- **Authentification par clé**: Pas de mots de passe, clés API uniquement
- **Permissions minimales**: Principe du moindre privilège
- **Rotation automatique**: Changement périodique des clés
- **Monitoring**: Détection d'utilisation anormale

#### **Procédures d'urgence**

- **Break-glass**: Procédure d'accès d'urgence en cas de crise
- **Accès temporaire**: Création d'accès limités dans le temps
- **Audit**: Traçabilité complète des accès d'urgence
- **Révocation**: Suppression immédiate des accès d'urgence

## 3.5 Sécurité des infrastructures

### 3.5.1 Mécanismes de protection (proxy, DLP, Pare-feu applicatifs)

**Mécanismes de protection réseau:**

#### **Proxy inverse (Nginx)**

- **Filtrage des requêtes**: Validation des headers, méthodes HTTP
- **Rate limiting**: Limitation du nombre de requêtes par IP
- **Protection DDoS**: Détection et blocage des attaques par déni de service
- **Filtrage géographique**: Blocage des accès depuis certaines régions

```nginx
# Configuration de protection DDoS
http {
    # Limitation du nombre de connexions par IP
    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
    limit_conn conn_limit_per_ip 10;

    # Limitation du nombre de requêtes par IP
    limit_req_zone $binary_remote_addr zone=req_limit_per_ip:10m rate=10r/s;
    limit_req zone=req_limit_per_ip burst=20 nodelay;

    # Blocage des User-Agents suspects
    if ($http_user_agent ~* (bot|crawler|spider|scraper)) {
        return 403;
    }

    # Blocage des méthodes HTTP dangereuses
    if ($request_method !~ ^(GET|POST|PUT|DELETE)$) {
        return 405;
    }
}
```

#### **Pare-feu applicatif (WAF)**

- **Règles OWASP**: Protection contre les vulnérabilités web courantes
- **Détection d'injection**: SQL, XSS, command injection
- **Protection CSRF**: Validation des tokens anti-CSRF
- **Filtrage des entrées**: Validation et assainissement des données

#### **Protection contre la fuite de données (DLP)**

- **Détection des PII**: Identification automatique des données personnelles
- **Chiffrement automatique**: Protection des données sensibles
- **Monitoring des exports**: Surveillance des téléchargements et exports
- **Alertes**: Notification en cas de fuite potentielle

### 3.5.2 Optionnel à n'utiliser que lorsque le projet requiert l'installation de produit de sécurité physique

**Produits de sécurité physique (optionnels):**

#### **HSM (Hardware Security Module)**

- **Cas d'usage**: Gestion des clés de chiffrement critiques
- **Avantages**: Sécurité matérielle, protection contre les attaques physiques
- **Coûts**: Élevés (installation, maintenance, expertise)
- **Recommandation**: Non requis pour le MVP, à évaluer pour la production

#### **Pare-feu physique**

- **Cas d'usage**: Protection réseau avancée, segmentation
- **Avantages**: Performance élevée, fonctionnalités avancées
- **Coûts**: Matériel, licences, maintenance
- **Recommandation**: Non requis, protection logicielle suffisante

## 3.6 Protection des endpoints

### 3.6.1 Endurcissement des plateformes serveurs (OS et applicatif)

**Endurcissement des serveurs:**

#### **Système d'exploitation**

- **Mise à jour**: Patches de sécurité automatiques
- **Services**: Désactivation des services inutiles
- **Utilisateurs**: Suppression des comptes par défaut
- **Permissions**: Restriction des permissions de fichiers

```bash
# Script d'endurcissement Ubuntu/Debian
#!/bin/bash

# Mise à jour automatique des paquets de sécurité
apt-get update && apt-get upgrade -y

# Désactivation des services inutiles
systemctl disable telnet
systemctl disable rsh
systemctl disable rlogin

# Configuration du pare-feu
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Restriction des permissions
chmod 600 /etc/shadow
chmod 644 /etc/passwd
chmod 644 /etc/group
```

#### **Application**

- **Variables d'environnement**: Pas d'informations sensibles dans le code
- **Logs**: Pas de données sensibles dans les logs
- **Erreurs**: Messages d'erreur génériques en production
- **Headers**: Suppression des headers d'information

### 3.6.2 Endurcissement des endpoints utilisateur

**Protection des clients:**

#### **Interface web**

- **Interface SMS (Principale)** : Via Twilio, accessible sans internet, simple d'usage
- **Interface CLI** : Commandes de base pour la gestion système
- **Interface Web (Planifiée Phase 2)** : Interface complémentaire avec HTTPS obligatoire
- **Headers de sécurité**: CSP, HSTS, X-Frame-Options
- **Validation côté client**: Double validation (client + serveur)
- **Sanitisation**: Nettoyage des entrées utilisateur

#### **APIs**

- **Authentification**: Validation stricte des tokens
- **Validation**: Vérification des paramètres et du corps des requêtes
- **Rate limiting**: Limitation des appels API par utilisateur
- **Monitoring**: Détection d'utilisation anormale

## 3.7 Journalisation et surveillance

### 3.7.1 Configuration, protection et cycle de vie de la journalisation

**Configuration des logs:**

#### **Niveaux de journalisation**

- **ERROR**: Erreurs critiques nécessitant une intervention immédiate
- **WARNING**: Avertissements nécessitant une attention
- **INFO**: Informations générales sur le fonctionnement
- **DEBUG**: Détails techniques pour le développement (désactivé en production)

#### **Protection des logs**

- **Chiffrement**: Logs sensibles chiffrés au repos
- **Accès restreint**: Seuls les administrateurs peuvent accéder aux logs
- **Intégrité**: Hachage des logs pour détecter les modifications
- **Rotation**: Rotation automatique des fichiers de logs

```python
# Configuration de journalisation sécurisée
import logging
import logging.handlers
from cryptography.fernet import Fernet

class SecureRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Handler de logs avec chiffrement et rotation"""

    def __init__(self, filename, max_bytes, backup_count, encryption_key):
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count)
        self.fernet = Fernet(encryption_key)

    def emit(self, record):
        # Chiffrement du message avant écriture
        encrypted_msg = self.fernet.encrypt(self.format(record).encode())
        record.msg = encrypted_msg.decode()
        super().emit(record)

# Configuration du logger
logger = logging.getLogger('personal_assistant')
logger.setLevel(logging.INFO)

# Handler sécurisé avec rotation
secure_handler = SecureRotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,
    encryption_key=os.getenv('LOG_ENCRYPTION_KEY')
)

logger.addHandler(secure_handler)
```

#### **Cycle de vie des logs**

- **Rétention**: 30 jours pour les logs d'application, 90 jours pour les logs de sécurité
- **Archivage**: Compression et chiffrement des logs archivés
- **Suppression**: Suppression automatique des logs expirés
- **Audit**: Traçabilité de la gestion des logs

### 3.7.2 Surveillances de sécurité

**Monitoring de sécurité:**

#### **Détection d'intrusion**

- **Anomalies comportementales**: Détection des comportements suspects
- **Tentatives d'accès**: Surveillance des tentatives d'authentification
- **Modifications de données**: Détection des changements non autorisés
- **Utilisation des ressources**: Surveillance de l'utilisation anormale

#### **Alertes de sécurité**

- **Temps réel**: Notification immédiate des incidents critiques
- **Escalade**: Escalade automatique selon la criticité
- **Canaux**: Email, SMS, Slack, dashboard
- **Documentation**: Procédures de réponse aux incidents

```python
# Système d'alertes de sécurité
class SecurityAlerting:
    def __init__(self):
        self.alert_channels = {
            'critical': ['sms', 'email', 'slack'],
            'high': ['email', 'slack'],
            'medium': ['email'],
            'low': ['dashboard']
        }

    def send_alert(self, level, message, context):
        """Envoi d'alerte selon le niveau de criticité"""
        channels = self.alert_channels.get(level, ['dashboard'])

        for channel in channels:
            if channel == 'sms':
                self.send_sms_alert(message, context)
            elif channel == 'email':
                self.send_email_alert(message, context)
            elif channel == 'slack':
                self.send_slack_alert(message, context)
            elif channel == 'dashboard':
                self.update_dashboard(message, context)

    def detect_security_incident(self, event):
        """Détection d'incident de sécurité"""
        if event.type == 'failed_login' and event.count > 5:
            self.send_alert('high', 'Tentatives de connexion échouées multiples', event)
        elif event.type == 'data_access' and event.user_id != event.resource_owner:
            self.send_alert('critical', 'Accès non autorisé aux données', event)
        elif event.type == 'api_abuse' and event.rate > 100:
            self.send_alert('medium', 'Utilisation abusive de l\'API', event)
```

## 3.8 Tests ETTIC

**Tests de sécurité ETTIC (Évaluation Technique de la Sécurité des Technologies de l'Information et de la Communication):**

#### **Tests de pénétration**

- **Fréquence**: Annuelle, plus fréquent en cas de changements majeurs
- **Portée**: Applications, infrastructure, réseau
- **Méthodologie**: OWASP Testing Guide, NIST Cybersecurity Framework
- **Rapport**: Documentation complète des vulnérabilités et recommandations

#### **Tests de vulnérabilité**

- **Automatisés**: Scans quotidiens avec outils spécialisés
- **Manuels**: Tests manuels pour les vulnérabilités complexes
- **Validation**: Vérification des vulnérabilités détectées
- **Correction**: Plan de correction avec priorités

#### **Tests de résistance**

- **Chiffrement**: Validation de la résistance des algorithmes
- **Authentification**: Tests de force brute et de dictionnaire
- **Session**: Tests de fixation et de hijacking
- **Autorisation**: Tests de contournement des contrôles d'accès

**Plan de tests ETTIC:**

| Type de test               | Fréquence   | Portée                        | Responsable        | Livrable                                |
| -------------------------- | ----------- | ----------------------------- | ------------------ | --------------------------------------- |
| **Tests de pénétration**   | Annuel      | Applications + Infrastructure | Consultant externe | Rapport détaillé + Plan de correction   |
| **Tests de vulnérabilité** | Quotidien   | Applications                  | Équipe DevOps      | Rapport de vulnérabilités + Corrections |
| **Tests de résistance**    | Mensuel     | Composants critiques          | Équipe sécurité    | Rapport de résistance + Améliorations   |
| **Audit de sécurité**      | Trimestriel | Processus + Procédures        | CISO               | Rapport d'audit + Plan d'action         |

# 4. Répartition détaillée des composants

Cette section contient les schémas de répartition détaillée des composants de la solution

**Tableau 9 - Environnements**

| Environnement         | À inclure | Justification                                                                                                                  |
| --------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Development (Dev)** | ✅ Oui    | Environnement de développement local avec base de données SQLite, hot reload activé, et logs en console pour le debugging      |
| **Staging (Stage)**   | ✅ Oui    | Environnement de test avec configuration de production, base de données PostgreSQL, monitoring basique, et tests d'intégration |
| **Production (Prod)** | ✅ Oui    | Environnement de production avec haute disponibilité, chiffrement complet, monitoring avancé, et sauvegardes automatisées      |

**Figure 2 - Schémas de répartition détaillée**

#### **2.1 Architecture réseau globale et segmentation de sécurité**

```mermaid
graph TB
    subgraph "Internet - Zone publique"
        USERS[👥 Utilisateurs finaux]
        PARTNERS[🤝 Partenaires APIs]
        TWILIO[📱 Twilio SMS<br/>Interface principale]
    end

    subgraph "DMZ - Zone de sécurité publique"
        CDN[📡 CDN Cloudflare<br/>DDoS Protection<br/>Cache Global]
        WAF[🛡️ WAF Cloudflare<br/>Règles OWASP<br/>Rate Limiting]
        LOAD_BALANCER[⚖️ Load Balancer<br/>HAProxy + Keepalived<br/>Failover automatique]
    end

    subgraph "Zone Applications - Sécurité renforcée"
        NGINX[🛡️ Nginx Proxy<br/>TLS 1.3, HTTP/2<br/>Rate Limiting]
        API[🚀 FastAPI Backend<br/>Port 8000]
        AGENT[🧠 Agent Service<br/>Port 8001<br/>Orchestration centrale]
        WORKERS[⚙️ Background Workers<br/>Port 8002<br/>Tâches asynchrones]
    end

    subgraph "Zone Données - Sécurité maximale"
        POSTGRES[(🗄️ PostgreSQL<br/>Port 5432<br/>Chiffrement AES-256)]
        REDIS[(🔴 Redis<br/>Port 6379<br/>Cluster Redis)]
        BACKUP[💾 Backup Storage<br/>Port 5433<br/>RPO 24h, RTO 30min]
    end

    subgraph "Zone Monitoring - Accès privilégié"
        PROMETHEUS[📊 Prometheus<br/>Port 9090]
        GRAFANA[📈 Grafana<br/>Port 3000]
        LOKI[📝 Loki<br/>Port 3100]
        JAEGER[🔍 Jaeger<br/>Port 16686]
    end

    %% Flux réseau principal avec sécurité
    USERS --> CDN
    PARTNERS --> CDN
    TWILIO --> CDN

    CDN --> WAF
    WAF --> LOAD_BALANCER
    LOAD_BALANCER --> NGINX

    %% Routage vers applications avec isolation
    NGINX --> API
    NGINX --> AGENT
    NGINX --> WORKERS

    %% Communication inter-services (zone applications)
    API --> AGENT
    AGENT --> POSTGRES
    AGENT --> REDIS
    AGENT --> WORKERS

    WORKERS --> POSTGRES
    WORKERS --> REDIS

    %% Monitoring de tous les services
    API --> PROMETHEUS
    AGENT --> PROMETHEUS
    WORKERS --> PROMETHEUS
    POSTGRES --> PROMETHEUS
    REDIS --> PROMETHEUS

    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA
    JAEGER --> GRAFANA

    %% Sauvegarde sécurisée
    BACKUP --> POSTGRES

    %% Styling par zones de sécurité
    classDef internet fill:#e1f5fe
    classDef dmz fill:#fff3e0
    classDef apps fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef monitoring fill:#fce4ec

    class USERS,PARTNERS,TWILIO internet
    class CDN,WAF,LOAD_BALANCER dmz
    class NGINX,API,AGENT,WORKERS apps
    class POSTGRES,REDIS,BACKUP data
    class PROMETHEUS,GRAFANA,LOKI,JAEGER monitoring
```

**Explication de l'architecture réseau**:

L'architecture réseau suit le principe de **défense en profondeur** avec plusieurs zones de sécurité et une isolation stricte, optimisée pour l'assistant personnel TDAH :

#### **1. Zone publique (Internet)**

- **Utilisateurs finaux** : Accès via HTTPS/TLS 1.3 depuis n'importe quel appareil
- **Partenaires APIs** : Intégrations externes sécurisées (Gemini, Graph, Notion, YouTube)
- **Twilio SMS** : Interface SMS principale pour l'assistant TDAH (accès universel sans internet requis)

#### **2. Zone DMZ - Sécurité publique**

- **CDN Cloudflare** : Protection DDoS de niveau entreprise, cache global, distribution géographique
- **WAF Cloudflare** : Règles OWASP, protection contre les attaques web, filtrage des menaces
- **Load Balancer** : HAProxy + Keepalived avec failover automatique, distribution de charge intelligente

#### **3. Zone Applications - Sécurité renforcée**

- **Nginx Proxy** : TLS 1.3, HTTP/2, rate limiting, compression, protection contre la surcharge
- **FastAPI Backend** : Service d'API principal avec authentification et gestion des utilisateurs
- **Agent Service** : Orchestration centrale de l'assistant TDAH, gestion des outils et de la mémoire
- **Background Workers** : Tâches asynchrones (rappel, synchronisation, planification)

#### **4. Zone Données - Sécurité maximale**

- **PostgreSQL** : Base de données principale avec chiffrement AES-256, données utilisateur et LTM
- **Redis** : Cache et queues avec cluster Redis, sessions utilisateur et rate limiting
- **Backup** : Stockage de sauvegarde avec RPO 24h et RTO 30min, chiffrement des sauvegardes

#### **5. Zone Monitoring - Accès privilégié**

- **Prometheus** : Collecte de métriques haute résolution, surveillance des performances
- **Grafana** : Dashboards et alertes, visualisation des métriques en temps réel
- **Loki** : Agrégation des logs centralisés, recherche et analyse des logs
- **Jaeger** : Traçage distribué pour le debugging et l'optimisation des performances

#### **Principes de sécurité appliqués :**

- **Isolation des zones** : Communication strictement contrôlée entre zones de sécurité
- **Chiffrement** : TLS 1.3 en transit, AES-256 au repos pour les données sensibles
- **Authentification** : MFA pour l'accès aux zones sensibles, RBAC strict
- **Monitoring** : Surveillance continue de tous les composants réseau et applicatifs
- **Redondance** : Load balancer avec failover automatique, sauvegardes automatisées
- **Protection TDAH** : Interface SMS accessible sans internet, simplicité d'usage

#### **2.2 Environnement Development (Dev) - Local**

```mermaid
graph TB
    subgraph "Machine de développement locale"
        DEV_USER[👤 Développeur]
        DEV_TERMINAL[💻 Terminal local]
        DEV_DOCKER[🐳 Docker Desktop]
    end

    subgraph "Services conteneurisés (ports exposés localement)"
        DEV_API[🚀 FastAPI Dev<br/>Port 8000<br/>Hot Reload Activé]
        DEV_AGENT[🧠 Agent Service Dev<br/>Port 8001]
        DEV_POSTGRES[🗄️ PostgreSQL Dev<br/>Port 5432<br/>Base locale]
        DEV_REDIS[🔴 Redis Dev<br/>Port 6379<br/>Cache local]
    end

    subgraph "Fichiers et configuration"
        DEV_SRC[📁 Code source<br/>Montage volume]
        DEV_ENV[⚙️ .env.dev<br/>Variables locales]
        DEV_LOGS[📝 Logs console<br/>Debug activé]
    end

    %% Flux de développement
    DEV_USER --> DEV_TERMINAL
    DEV_TERMINAL --> DEV_DOCKER
    DEV_DOCKER --> DEV_API
    DEV_DOCKER --> DEV_AGENT
    DEV_DOCKER --> DEV_POSTGRES
    DEV_DOCKER --> DEV_REDIS

    DEV_API --> DEV_AGENT
    DEV_AGENT --> DEV_POSTGRES
    DEV_AGENT --> DEV_REDIS

    DEV_SRC --> DEV_API
    DEV_ENV --> DEV_API
    DEV_LOGS --> DEV_API

    %% Styling
    classDef dev fill:#e8f5e8
    classDef services fill:#f3e5f5
    classDef files fill:#fff3e0

    class DEV_USER,DEV_TERMINAL,DEV_DOCKER dev
    class DEV_API,DEV_AGENT,DEV_POSTGRES,DEV_REDIS services
    class DEV_SRC,DEV_ENV,DEV_LOGS files
```

#### **2.3 Environnement Staging (Stage) - Serveur dédié**

```mermaid
graph TB
    subgraph "Serveur de staging dédié"
        STAGE_SERVER[🖥️ Serveur Stage<br/>8 vCPU, 16 GB RAM<br/>200 GB SSD]
        STAGE_NETWORK[🌐 Réseau isolé<br/>VLAN Stage<br/>Pare-feu dédié]
    end

    subgraph "Services de staging"
        STAGE_NGINX[🛡️ Nginx Stage<br/>Ports 80/443<br/>TLS Stage]
        STAGE_API[🚀 FastAPI Stage<br/>Port 8000<br/>Authentification]
        STAGE_AGENT[🧠 Agent Service Stage<br/>Port 8001]
        STAGE_WORKERS[⚙️ Workers Stage<br/>Port 8002]
        STAGE_POSTGRES[🗄️ PostgreSQL Stage<br/>Port 5432<br/>Données de test]
        STAGE_REDIS[🔴 Redis Stage<br/>Port 6379<br/>Cache stage]
    end

    subgraph "Monitoring de staging"
        STAGE_PROMETHEUS[📊 Prometheus Stage<br/>Port 9090]
        STAGE_GRAFANA[📈 Grafana Stage<br/>Port 3000<br/>Dashboards de test]
    end

    subgraph "Sécurité et configuration"
        STAGE_WAF[🛡️ WAF Stage<br/>Règles de test]
        STAGE_SECRETS[🔐 Secrets Stage<br/>Docker secrets]
        STAGE_BACKUP[💾 Backup Stage<br/>Sauvegarde test]
    end

    %% Flux de staging
    STAGE_SERVER --> STAGE_NETWORK
    STAGE_NETWORK --> STAGE_NGINX
    STAGE_NGINX --> STAGE_API
    STAGE_NGINX --> STAGE_AGENT
    STAGE_NGINX --> STAGE_WORKERS

    STAGE_API --> STAGE_AGENT
    STAGE_AGENT --> STAGE_POSTGRES
    STAGE_AGENT --> STAGE_REDIS
    STAGE_AGENT --> STAGE_WORKERS

    STAGE_WORKERS --> STAGE_POSTGRES
    STAGE_WORKERS --> STAGE_REDIS

    %% Monitoring
    STAGE_API --> STAGE_PROMETHEUS
    STAGE_AGENT --> STAGE_PROMETHEUS
    STAGE_WORKERS --> STAGE_PROMETHEUS
    STAGE_POSTGRES --> STAGE_PROMETHEUS
    STAGE_REDIS --> STAGE_PROMETHEUS

    STAGE_PROMETHEUS --> STAGE_GRAFANA

    %% Sécurité
    STAGE_WAF --> STAGE_NGINX
    STAGE_SECRETS --> STAGE_API
    STAGE_SECRETS --> STAGE_AGENT
    STAGE_BACKUP --> STAGE_POSTGRES

    %% Styling
    classDef server fill:#e8f5e8
    classDef services fill:#f3e5f5
    classDef monitoring fill:#fce4ec
    classDef security fill:#fff3e0

    class STAGE_SERVER,STAGE_NETWORK server
    class STAGE_NGINX,STAGE_API,STAGE_AGENT,STAGE_WORKERS,STAGE_POSTGRES,STAGE_REDIS services
    class STAGE_PROMETHEUS,STAGE_GRAFANA monitoring
    class STAGE_WAF,STAGE_SECRETS,STAGE_BACKUP security
```

#### **2.4 Environnement Production (Prod) - Haute disponibilité**

```mermaid
graph TB
    subgraph "Infrastructure de production multi-serveurs"
        PROD_LB[⚖️ Load Balancer<br/>HAProxy + Keepalived<br/>Failover automatique]
        PROD_SERVER1[🖥️ Serveur Prod 1<br/>16 vCPU, 32 GB RAM<br/>500 GB SSD]
        PROD_SERVER2[🖥️ Serveur Prod 2<br/>16 vCPU, 32 GB RAM<br/>500 GB SSD]
        PROD_DB_SERVER[🗄️ Serveur DB<br/>32 vCPU, 64 GB RAM<br/>1 TB SSD + RAID]
    end

    subgraph "Services de production (répliqués)"
        PROD_NGINX1[🛡️ Nginx Prod 1<br/>Ports 80/443<br/>TLS 1.3 Production]
        PROD_NGINX2[🛡️ Nginx Prod 2<br/>Ports 80/443<br/>TLS 1.3 Production]

        PROD_API1[🚀 FastAPI Prod 1<br/>Port 8000<br/>Authentification MFA]
        PROD_API2[🚀 FastAPI Prod 2<br/>Port 8000<br/>Authentification MFA]

        PROD_AGENT1[🧠 Agent Service Prod 1<br/>Port 8001<br/>Orchestration]
        PROD_AGENT2[🧠 Agent Service Prod 2<br/>Port 8001<br/>Orchestration]

        PROD_WORKERS1[⚙️ Workers Prod 1<br/>Port 8002<br/>Tâches asynchrones]
        PROD_WORKERS2[⚙️ Workers Prod 2<br/>Port 8002<br/>Tâches asynchrones]
        PROD_WORKERS3[⚙️ Workers Prod 3<br/>Port 8002<br/>Tâches asynchrones]
    end

    subgraph "Base de données haute disponibilité"
        PROD_POSTGRES_MASTER[(🗄️ PostgreSQL Master<br/>Port 5432<br/>Chiffrement AES-256)]
        PROD_POSTGRES_REPLICA[(🗄️ PostgreSQL Replica<br/>Port 5433<br/>Réplication temps réel)]
        PROD_REDIS_MASTER[(🔴 Redis Master<br/>Port 6379<br/>Cluster Redis)]
        PROD_REDIS_REPLICA[(🔴 Redis Replica<br/>Port 6380<br/>Réplication Redis)]
    end

    subgraph "Monitoring et observabilité production"
        PROD_PROMETHEUS[📊 Prometheus Prod<br/>Port 9090<br/>Métriques haute résolution]
        PROD_GRAFANA[📈 Grafana Prod<br/>Port 3000<br/>Dashboards production]
        PROD_LOKI[📝 Loki Prod<br/>Port 3100<br/>Logs centralisés]
        PROD_JAEGER[🔍 Jaeger Prod<br/>Port 16686<br/>Tracing distribué]
    end

    subgraph "Sécurité et sauvegarde production"
        PROD_WAF[🛡️ WAF Production<br/>Règles avancées]
        PROD_SECRETS[🔐 Gestionnaire de secrets<br/>HashiCorp Vault]
        PROD_BACKUP[💾 Backup Production<br/>RPO 24h, RTO 30min]
        PROD_CDN[📡 CDN Production<br/>Cloudflare Enterprise]
    end

    %% Flux de production avec haute disponibilité
    PROD_CDN --> PROD_LB
    PROD_LB --> PROD_NGINX1
    PROD_LB --> PROD_NGINX2

    PROD_NGINX1 --> PROD_API1
    PROD_NGINX1 --> PROD_AGENT1
    PROD_NGINX2 --> PROD_API2
    PROD_NGINX2 --> PROD_AGENT2

    PROD_API1 --> PROD_AGENT1
    PROD_API2 --> PROD_AGENT2

    PROD_AGENT1 --> PROD_POSTGRES_MASTER
    PROD_AGENT2 --> PROD_POSTGRES_MASTER
    PROD_AGENT1 --> PROD_REDIS_MASTER
    PROD_AGENT2 --> PROD_REDIS_MASTER

    PROD_AGENT1 --> PROD_WORKERS1
    PROD_AGENT2 --> PROD_WORKERS2

    PROD_WORKERS1 --> PROD_POSTGRES_MASTER
    PROD_WORKERS2 --> PROD_POSTGRES_MASTER
    PROD_WORKERS3 --> PROD_POSTGRES_MASTER

    PROD_WORKERS1 --> PROD_REDIS_MASTER
    PROD_WORKERS2 --> PROD_REDIS_MASTER
    PROD_WORKERS3 --> PROD_REDIS_MASTER

    %% Réplication base de données
    PROD_POSTGRES_MASTER --> PROD_POSTGRES_REPLICA
    PROD_REDIS_MASTER --> PROD_REDIS_REPLICA

    %% Monitoring production
    PROD_API1 --> PROD_PROMETHEUS
    PROD_API2 --> PROD_PROMETHEUS
    PROD_AGENT1 --> PROD_PROMETHEUS
    PROD_AGENT2 --> PROD_PROMETHEUS
    PROD_WORKERS1 --> PROD_PROMETHEUS
    PROD_WORKERS2 --> PROD_PROMETHEUS
    PROD_WORKERS3 --> PROD_PROMETHEUS
    PROD_POSTGRES_MASTER --> PROD_PROMETHEUS
    PROD_REDIS_MASTER --> PROD_PROMETHEUS

    PROD_PROMETHEUS --> PROD_GRAFANA
    PROD_LOKI --> PROD_GRAFANA
    PROD_JAEGER --> PROD_GRAFANA

    %% Sécurité et sauvegarde
    PROD_WAF --> PROD_LB
    PROD_SECRETS --> PROD_API1
    PROD_SECRETS --> PROD_API2
    PROD_SECRETS --> PROD_AGENT1
    PROD_SECRETS --> PROD_AGENT2
    PROD_BACKUP --> PROD_POSTGRES_MASTER

    %% Styling
    classDef infrastructure fill:#e8f5e8
    classDef services fill:#f3e5f5
    classDef database fill:#e1f5fe
    classDef monitoring fill:#fce4ec
    classDef security fill:#fff3e0

    class PROD_LB,PROD_SERVER1,PROD_SERVER2,PROD_DB_SERVER infrastructure
    class PROD_NGINX1,PROD_NGINX2,PROD_API1,PROD_API2,PROD_AGENT1,PROD_AGENT2,PROD_WORKERS1,PROD_WORKERS2,PROD_WORKERS3 services
    class PROD_POSTGRES_MASTER,PROD_POSTGRES_REPLICA,PROD_REDIS_MASTER,PROD_REDIS_REPLICA database
    class PROD_PROMETHEUS,PROD_GRAFANA,PROD_LOKI,PROD_JAEGER monitoring
    class PROD_WAF,PROD_SECRETS,PROD_BACKUP,PROD_CDN security
```

## 4.1 Spécification des composants

Cette section contient des spécification technologiques de chaque infrastructure de la solution

**Tableau 10 - Spécifications**

| Spécifications               | S'applique à la solution |
| ---------------------------- | ------------------------ |
| **Tableaux VM**              | ❌ Non                   |
| **Données**                  | ✅ Oui                   |
| **Intergiciel**              | ✅ Oui                   |
| **Applicatif**               | ✅ Oui                   |
| **Coupe-feu**                | ✅ Oui                   |
| **Microsegmentation**        | ❌ Non                   |
| **Alertage et surveillance** | ✅ Oui                   |
| **Automatisation**           | ✅ Oui                   |
| **Transferts de fichiers**   | ✅ Oui                   |
| **Relève**                   | ✅ Oui                   |
| **Balancement de charge**    | ✅ Oui                   |

## 4.2 Analyse des écarts et dérogations

### 4.2.1 Écarts identifiés par rapport aux standards

**Tableau 4.2.1 - Analyse des écarts et dérogations**

| Composant               | Standard attendu             | Implémentation actuelle              | Écart                         | Justification                               | Plan de correction                                               |
| ----------------------- | ---------------------------- | ------------------------------------ | ----------------------------- | ------------------------------------------- | ---------------------------------------------------------------- |
| **Base de données**     | PostgreSQL 16+               | PostgreSQL 15+                       | Version légèrement antérieure | Stabilité et compatibilité des extensions   | Mise à jour vers PostgreSQL 16+ lors de la prochaine maintenance |
| **Chiffrement**         | AES-256-GCM partout          | AES-256-GCM + AES-256-CBC            | Mélange d'algorithmes         | Optimisation des performances selon l'usage | Standardisation sur AES-256-GCM d'ici 6 mois                     |
| **Monitoring**          | Stack observabilité complète | Prometheus + Grafana + Loki + Jaeger | Jaeger non implémenté         | Priorité sur les métriques et logs          | Implémentation de Jaeger dans la phase 2                         |
| **Haute disponibilité** | Multi-zone géographique      | Single-zone avec réplication         | Risque de perte de service    | Coût et complexité initiale                 | Migration multi-zone dans la phase 3                             |

### 4.2.2 Dérogations justifiées

#### **4.2.2.1 Utilisation de Docker Compose vs Kubernetes**

**Dérogation**: Utilisation de Docker Compose au lieu de Kubernetes pour l'orchestration

**Justification**:

- **Complexité réduite**: Équipe DevOps plus petite, expertise Docker disponible
- **Coût initial**: Pas de coûts de licence Kubernetes
- **Time-to-market**: Déploiement plus rapide pour le MVP
- **Évolutivité**: Migration vers Kubernetes possible dans la phase 3

**Plan de migration**:

- Phase 1: Docker Compose avec monitoring avancé
- Phase 2: Préparation de la migration Kubernetes
- Phase 3: Migration complète vers Kubernetes

#### **4.2.2.2 Base de données single-instance vs cluster**

**Dérogation**: Base de données PostgreSQL single-instance avec réplication simple

**Justification**:

- **Charge initiale**: Nombre d'utilisateurs limité au début
- **Complexité opérationnelle**: Équipe d'exploitation réduite
- **Coût**: Réduction des coûts d'infrastructure
- **Évolutivité**: Migration vers cluster possible selon la croissance

**Plan d'évolution**:

- Phase 1: Single-instance avec réplication
- Phase 2: Cluster avec failover automatique
- Phase 3: Distribution géographique

### 4.2.3 Plan de correction des écarts

#### **4.2.3.1 Court terme (0-3 mois)**

- **Mise à jour PostgreSQL**: Migration vers PostgreSQL 16+
- **Standardisation chiffrement**: Utilisation exclusive d'AES-256-GCM
- **Implémentation Jaeger**: Ajout du traçage distribué
- **Tests de sécurité**: Validation des composants de sécurité

#### **4.2.3.2 Moyen terme (3-6 mois)**

- **Préparation Kubernetes**: Formation équipe et tests de concept
- **Optimisation monitoring**: Amélioration des métriques et alertes
- **Tests de charge**: Validation des performances sous charge
- **Documentation**: Procédures opérationnelles complètes

#### **4.2.3.3 Long terme (6-12 mois)**

- **Migration Kubernetes**: Orchestration complète avec auto-scaling
- **Multi-zone**: Distribution géographique des services
- **Cluster DB**: Base de données haute disponibilité
- **Observabilité avancée**: APM et tracing complet

# 5. Infrastructure de transport

## 5.1 Sommaire de la solution réseau

Cette section contient les schémas globaux pour la télécommunication

### 5.1.1 Architecture réseau globale

**Vue - Architecture réseau de la solution**

```mermaid
graph TB
    subgraph "Internet"
        USERS[👥 Utilisateurs finaux]
        PARTNERS[🤝 Partenaires APIs]
    end

    subgraph "DMZ - Zone publique"
        CDN[📡 CDN Cloudflare<br/>DDoS Protection<br/>Cache Global]
        WAF[🛡️ WAF Cloudflare<br/>Règles OWASP<br/>Rate Limiting]
        LOAD_BALANCER[⚖️ Load Balancer<br/>Distribution de charge<br/>SSL Termination]
    end

    subgraph "Zone sécurisée - Applications"
        NGINX[🛡️ Nginx Proxy<br/>TLS 1.3<br/>HTTP/2]
        API[🚀 FastAPI Backend]
        AGENT[🧠 Agent Service]
        WORKERS[⚙️ Background Workers]
    end

    subgraph "Zone sécurisée - Données"
        POSTGRES[(🗄️ PostgreSQL)]
        REDIS[(🔴 Redis)]
        BACKUP[💾 Backup Storage]
    end

    subgraph "Zone sécurisée - Monitoring"
        PROMETHEUS[📊 Prometheus]
        GRAFANA[📈 Grafana]
        LOKI[📝 Loki]
    end

    USERS --> CDN
    PARTNERS --> CDN
    CDN --> WAF
    WAF --> LOAD_BALANCER
    LOAD_BALANCER --> NGINX
    NGINX --> API
    NGINX --> AGENT
    NGINX --> WORKERS

    API --> POSTGRES
    API --> REDIS
    AGENT --> POSTGRES
    AGENT --> REDIS
    WORKERS --> POSTGRES
    WORKERS --> REDIS

    API --> PROMETHEUS
    AGENT --> PROMETHEUS
    WORKERS --> PROMETHEUS
    POSTGRES --> PROMETHEUS
    REDIS --> PROMETHEUS

    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA

    POSTGRES --> BACKUP
```

**Explication de l'architecture réseau**:

L'architecture réseau suit le principe de défense en profondeur avec plusieurs zones de sécurité :

1. **Zone publique (DMZ)**: CDN, WAF et load balancer exposés à Internet
2. **Zone applications**: Services applicatifs avec accès contrôlé
3. **Zone données**: Base de données et stockage avec accès restreint
4. **Zone monitoring**: Outils de surveillance avec accès privilégié

### 5.1.2 Composants de sécurité réseau

#### **5.1.2.1 Protection DDoS**

- **CDN Cloudflare**: Protection DDoS de niveau entreprise
- **Rate limiting**: Limitation des requêtes par IP et utilisateur
- **Geoblocking**: Blocage des accès depuis certaines régions
- **Bot protection**: Détection et blocage des robots malveillants

#### **5.1.2.2 WAF (Web Application Firewall)**

- **Règles OWASP**: Protection contre les vulnérabilités web courantes
- **Détection d'injection**: SQL, XSS, command injection
- **Protection CSRF**: Validation des tokens anti-CSRF
- **Filtrage des entrées**: Validation et assainissement des données

#### **5.1.2.3 Load Balancer**

- **Distribution de charge**: Répartition équitable des requêtes
- **Health checks**: Vérification continue de l'état des services
- **SSL termination**: Gestion centralisée des certificats TLS
- **Sticky sessions**: Maintien des sessions utilisateur

## 5.2 Spécification Réseaux/Télécom

**Tableau 5.2.1 - Spécifications réseau et télécom**

| Spécifications         | S'applique à la solution | Détails                                                                     |
| ---------------------- | ------------------------ | --------------------------------------------------------------------------- |
| **VLAN/Subnet**        | ✅ Oui                   | Segmentation des zones de sécurité (DMZ, Applications, Données, Monitoring) |
| **VRF/Zones**          | ❌ Non                   | Pas de routage multi-VRF requis                                             |
| **DNS**                | ✅ Oui                   | Gestion DNS avec Cloudflare, résolution interne pour les services           |
| **VPN/IPVPN**          | ❌ Non                   | Accès direct via Internet sécurisé (HTTPS/TLS)                              |
| **Circuits/capacités** | ✅ Oui                   | Bande passante Internet 1Gbps+, redondance avec fournisseur secondaire      |
| **NAT**                | ✅ Oui                   | NAT sortant pour les services internes, pas de NAT entrant                  |

### 5.2.1 Configuration des VLANs et subnets

#### **5.2.1.1 Segmentation réseau**

**Zone DMZ (10.0.1.0/24)**:

- **10.0.1.1-10.0.1.10**: Load balancer et WAF
- **10.0.1.11-10.0.1.20**: CDN et services publics
- **10.0.1.21-10.0.1.30**: Services de sécurité

**Zone Applications (10.0.2.0/24)**:

- **10.0.2.1-10.0.2.20**: Services FastAPI et Agent
- **10.0.2.21-10.0.2.40**: Workers et services asynchrones
- **10.0.2.41-10.0.2.50**: Services d'intégration

**Zone Données (10.0.3.0/24)**:

- **10.0.3.1-10.0.3.10**: Base de données PostgreSQL
- **10.0.3.11-10.0.3.20**: Cache Redis
- **10.0.3.21-10.0.3.30**: Stockage de sauvegarde

**Zone Monitoring (10.0.4.0/24)**:

- **10.0.4.1-10.0.4.10**: Prometheus et métriques
- **10.0.4.11-10.0.4.20**: Grafana et visualisation
- **10.0.4.21-10.0.4.30**: Logs et traces

#### **5.2.1.2 Règles de routage**

- **Isolation stricte**: Pas de communication directe entre zones
- **Trafic autorisé**: Seulement via les services de proxy et d'API
- **Monitoring**: Accès en lecture seule depuis la zone monitoring
- **Backup**: Accès restreint depuis la zone données

### 5.2.2 Configuration DNS

#### **5.2.2.1 DNS externe (Cloudflare)**

**Domaines principaux**:

- **personal-assistant.com**: Domaine principal de production
- **api.personal-assistant.com**: API publique
- **admin.personal-assistant.com**: Interface d'administration

**Configuration DNS**:

- **A Records**: Pointage vers les load balancers
- **CNAME**: Alias pour les sous-domaines
- **MX Records**: Configuration email (si applicable)
- **TXT Records**: Validation et sécurité (SPF, DKIM, DMARC)

#### **5.2.2.2 DNS interne**

**Résolution des services**:

- **postgres.internal**: Base de données PostgreSQL
- **redis.internal**: Cache Redis
- **prometheus.internal**: Collecte de métriques
- **grafana.internal**: Interface de monitoring

**Configuration**:

- **Forwarders**: Résolution DNS externe via Cloudflare
- **Cache**: Cache local pour améliorer les performances
- **Logs**: Journalisation des requêtes DNS

### 5.2.3 Circuits et capacités

#### **5.2.3.1 Connexion Internet principale**

- **Fournisseur**: Fournisseur Internet principal
- **Bande passante**: 1Gbps symétrique
- **SLA**: 99.9% de disponibilité
- **Support**: Support technique 24/7

#### **5.2.3.2 Connexion Internet secondaire**

- **Fournisseur**: Fournisseur Internet secondaire
- **Bande passante**: 500Mbps symétrique
- **SLA**: 99.5% de disponibilité
- **Support**: Support technique 8/5

#### **5.2.3.3 Gestion de la redondance**

- **Failover automatique**: Basculement en cas de panne
- **Load balancing**: Répartition de la charge entre les connexions
- **Monitoring**: Surveillance continue de la qualité des connexions
- **Alertes**: Notification en cas de dégradation

### 5.2.4 Configuration NAT

#### **5.2.4.1 NAT sortant**

- **Masquerading**: Traduction des adresses IP internes
- **Pool d'adresses**: Utilisation des adresses IP publiques
- **Logs**: Journalisation des connexions sortantes
- **Monitoring**: Surveillance de l'utilisation de la bande passante

#### **5.2.4.2 Pas de NAT entrant**

- **Justification**: Services accessibles directement via load balancer
- **Sécurité**: Protection par WAF et règles de pare-feu
- **Performance**: Pas de surcharge due à la traduction d'adresses
- **Monitoring**: Surveillance directe des connexions entrantes

## 5.3 Spécification Téléphonie/VoIP

**Tableau 5.3.1 - Spécifications téléphonie et VoIP**

| Spécifications         | S'applique à la solution | Détails                                    |
| ---------------------- | ------------------------ | ------------------------------------------ |
| **VLAN/Subnet**        | ❌ Non                   | Pas de téléphonie VoIP dans la solution    |
| **VRF/Zones**          | ❌ Non                   | Pas de routage téléphonique requis         |
| **DNS**                | ❌ Non                   | Pas de résolution DNS téléphonique         |
| **VPN/IPVPN**          | ❌ Non                   | Pas de réseau téléphonique privé           |
| **Circuits/capacités** | ❌ Non                   | Pas de circuits téléphoniques              |
| **NAT**                | ❌ Non                   | Pas de traduction d'adresses téléphoniques |

### 5.3.1 Justification de l'exclusion

**Pas de composants téléphoniques**:

- **Communication SMS**: Via Twilio API (pas de PBX local)
- **Notifications**: Email, push notifications, SMS via APIs
- **Support utilisateur**: Interface web et chat (pas de téléphone)
- **Intégrations**: APIs tierces pour toutes les communications

**Alternatives implémentées**:

- **Twilio SMS** : **Interface principale** - Envoi et réception de SMS via API
- **Interface CLI** : Commandes de base pour la gestion système
- **Interface Web** : **Planifiée Phase 2** - Interface complémentaire
- **Notifications push** : Notifications en temps réel via WebSocket
- **Email** : Communications importantes par email
- **Chat intégré** : Interface de conversation dans l'application

# 6. Infrastructure de transport (suite)

## 6.1 Sécurité réseau avancée

### 6.1.1 Microsegmentation

**Tableau 6.1.1 - Règles de microsegmentation**

| Source              | Destination         | Protocole | Port            | Justification             |
| ------------------- | ------------------- | --------- | --------------- | ------------------------- |
| **Internet**        | **Load Balancer**   | TCP       | 80, 443         | Accès public aux services |
| **Load Balancer**   | **Nginx Proxy**     | TCP       | 80, 443         | Routage des requêtes      |
| **Nginx Proxy**     | **FastAPI Backend** | TCP       | 8000            | Communication API         |
| **Nginx Proxy**     | **Agent Service**   | TCP       | 8001            | Communication Agent       |
| **FastAPI Backend** | **PostgreSQL**      | TCP       | 5432            | Accès base de données     |
| **FastAPI Backend** | **Redis**           | TCP       | 6379            | Accès cache               |
| **Agent Service**   | **PostgreSQL**      | TCP       | 5432            | Accès base de données     |
| **Agent Service**   | **Redis**           | TCP       | 6379            | Accès cache               |
| **Monitoring**      | **Tous services**   | TCP       | Ports métriques | Collecte de métriques     |

### 6.1.2 Pare-feu applicatif

#### **6.1.2.1 Règles de filtrage**

**Règles entrantes**:

- **HTTP/HTTPS**: Ports 80 et 443 uniquement
- **SSH**: Port 22 depuis IPs d'administration
- **Monitoring**: Ports spécifiques depuis zone monitoring

**Règles sortantes**:

- **APIs externes**: Accès aux services tiers requis
- **DNS**: Résolution DNS externe
- **NTP**: Synchronisation temporelle
- **Logs**: Envoi des logs de sécurité

#### **6.1.2.2 Protection avancée**

- **Intrusion Detection**: Détection des tentatives d'intrusion
- **Anomaly Detection**: Détection des comportements anormaux
- **Threat Intelligence**: Intégration des feeds de menaces
- **Automated Response**: Réponse automatique aux menaces

## 6.2 Monitoring et observabilité réseau

### 6.2.1 Métriques réseau

#### **6.2.1.1 Métriques de base**

- **Bande passante**: Utilisation upload/download
- **Latence**: RTT vers les services critiques
- **Paquets perdus**: Taux de perte de paquets
- **Connexions actives**: Nombre de connexions simultanées

#### **6.2.1.2 Métriques de sécurité**

- **Tentatives d'accès**: Nombre de tentatives d'authentification
- **Trafic bloqué**: Volume de trafic rejeté par le WAF
- **Anomalies détectées**: Comportements suspects identifiés
- **Vulnérabilités**: Scans de vulnérabilités détectés

### 6.2.2 Alertes réseau

#### **6.2.2.1 Seuils d'alerte**

- **Critique**: Service indisponible, attaque détectée
- **Élevé**: Performance dégradée, anomalies détectées
- **Moyen**: Utilisation élevée, attention requise
- **Faible**: Informations, maintenance planifiée

#### **6.2.2.2 Canaux de notification**

- **Email**: Alertes critiques et élevées
- **SMS**: Alertes critiques uniquement
- **Slack**: Toutes les alertes
- **Dashboard**: Visualisation en temps réel

## 6.3 Plan de reprise après sinistre réseau

### 6.3.1 Scénarios de sinistre

#### **6.3.1.1 Panne de connectivité**

- **Panne Internet principale**: Basculement vers connexion secondaire
- **Panne de fournisseur**: Utilisation de CDN de secours
- **Panne de load balancer**: Basculement vers instance de secours
- **Panne de WAF**: Mode dégradé avec protection basique

#### **6.3.1.2 Attaques réseau**

- **DDoS**: Activation de la protection Cloudflare
- **Intrusion**: Isolation des services compromis
- **Malware**: Nettoyage et restauration depuis sauvegarde
- **Ransomware**: Restauration complète depuis sauvegarde

### 6.3.2 Procédures de récupération

#### **6.3.2.1 Récupération automatique**

- **Failover**: Basculement automatique des services
- **Restart**: Redémarrage automatique des services défaillants
- **Isolation**: Isolation automatique des composants compromis
- **Notification**: Alerte automatique des équipes

#### **6.3.2.2 Récupération manuelle**

- **Procédures documentées**: Étapes détaillées pour chaque scénario
- **Équipes d'intervention**: Rôles et responsabilités définis
- **Communication**: Procédures de notification et d'escalade
- **Documentation**: Enregistrement des actions et leçons apprises

# 7. Annexe

Cette annexe contient les enjeux non résolus, fichiers complémentaires et informations additionnelles

## 7.1 Enjeux non résolus

### 7.1.1 Enjeux techniques

#### **7.1.1.1 Migration vers Kubernetes**

**Enjeu**: Passage de Docker Compose vers Kubernetes pour la scalabilité

**Impact**:

- **Court terme**: Augmentation de la complexité opérationnelle
- **Moyen terme**: Amélioration de la scalabilité et de la résilience
- **Long terme**: Réduction des coûts et amélioration de la maintenabilité

**Plan de résolution**:

- **Phase 1**: Formation de l'équipe DevOps
- **Phase 2**: Tests de concept et validation
- **Phase 3**: Migration progressive des services
- **Phase 4**: Optimisation et tuning

#### **7.1.1.2 Multi-zone géographique**

**Enjeu**: Distribution géographique des services pour la haute disponibilité

**Impact**:

- **Court terme**: Augmentation des coûts d'infrastructure
- **Moyen terme**: Amélioration de la latence et de la disponibilité
- **Long terme**: Conformité aux exigences de résilience

**Plan de résolution**:

- **Phase 1**: Analyse des besoins et des coûts
- **Phase 2**: Sélection des zones géographiques
- **Phase 3**: Déploiement et tests
- **Phase 4**: Optimisation des performances

### 7.1.2 Enjeux opérationnels

#### **7.1.2.1 Expertise DevOps**

**Enjeu**: Besoin d'expertise DevOps avancée pour la maintenance

**Impact**:

- **Court terme**: Dépendance aux consultants externes
- **Moyen terme**: Formation de l'équipe interne
- **Long terme**: Autonomie complète de l'équipe

**Plan de résolution**:

- **Phase 1**: Recrutement d'experts DevOps
- **Phase 2**: Formation de l'équipe existante
- **Phase 3**: Transfert de compétences
- **Phase 4**: Autonomie complète

#### **7.1.2.2 Monitoring 24/7**

**Enjeu**: Surveillance continue des services en production

**Impact**:

- **Court terme**: Coûts de monitoring et d'alerting
- **Moyen terme**: Amélioration de la détection des incidents
- **Long terme**: Réduction du temps de résolution

**Plan de résolution**:

- **Phase 1**: Mise en place du monitoring de base
- **Phase 2**: Implémentation des alertes automatiques
- **Phase 3**: Optimisation des seuils et procédures
- **Phase 4**: Automatisation complète

## 7.2 Fichiers complémentaires

### 7.2.1 Documentation technique

- **Architecture détaillée**: Schémas techniques complets
- **Procédures opérationnelles**: Guides de maintenance et d'exploitation
- **Plans de test**: Procédures de test et validation
- **Manuels utilisateur**: Documentation pour les utilisateurs finaux

### 7.2.2 Scripts et outils

- **Scripts de déploiement**: Automatisation du déploiement
- **Outils de monitoring**: Scripts de surveillance personnalisés
- **Utilitaires de maintenance**: Outils de diagnostic et de réparation
- **Tests automatisés**: Scripts de test et validation

### 7.2.3 Configurations

- **Docker Compose**: Configurations pour tous les environnements
- **Nginx**: Configurations de proxy et de sécurité
- **PostgreSQL**: Configurations de base de données
- **Monitoring**: Configurations Prometheus, Grafana, Loki

## 7.3 Informations additionnelles

### 7.3.1 Contacts et responsabilités

#### **7.3.1.1 Équipe technique**

- **Architecte solution**: Responsable de l'architecture globale
- **DevOps Lead**: Responsable de l'infrastructure et du déploiement
- **Développeur Backend**: Responsable des services applicatifs
- **Expert sécurité**: Responsable de la sécurité et de la conformité

#### **7.3.1.2 Fournisseurs et partenaires**

- **Cloudflare**: Protection DDoS et WAF
- **Google Cloud**: APIs Gemini et services cloud
- **Microsoft**: Graph API et services Office
- **Twilio**: Services SMS et communication

### 7.3.2 Calendrier et jalons

#### **7.3.2.1 Phase 1 - MVP (0-3 mois)**

- **Mois 1**: Infrastructure de base et déploiement
- **Mois 2**: Tests et validation
- **Mois 3**: Mise en production et monitoring

#### **7.3.2.2 Phase 2 - Enterprise (3-8 mois)**

- **Mois 4-5**: Sécurité et conformité
- **Mois 6-7**: Haute disponibilité et monitoring
- **Mois 8**: Tests et déploiement

#### **7.3.2.3 Phase 3 - SaaS (8-18 mois)**

- **Mois 9-12**: Migration vers Kubernetes
- **Mois 13-15**: Multi-zone géographique
- **Mois 16-18**: Optimisation et évolutivité

### 7.3.3 Métriques de succès

#### **7.3.3.1 Métriques techniques**

- **Disponibilité**: > 99.5% en production
- **Performance**: Latence P95 < 2s
- **Sécurité**: 0 vulnérabilités critiques
- **Scalabilité**: Support de 1000+ utilisateurs simultanés

#### **7.3.3.2 Métriques métier**

- **Adoption**: Croissance des utilisateurs actifs
- **Satisfaction**: Score de satisfaction utilisateur > 4.5/5
- **Rétention**: Taux de rétention > 80%
- **ROI**: Retour sur investissement positif en 18 mois

---

**Document généré le**: $(date)
**Version**: 1.0
**Statut**: Finalisé
**Approbé par**: Équipe d'architecture
