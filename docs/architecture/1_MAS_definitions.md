# 1. Définition

## 1.1 But, contexte affaires, portée et exclusions

Ce document présente les modèles servant à former et orienter la solution. Dans le but de comprendre le contexte de l'initiative, sa portée ainsi que ses exclusions

### 1.1.1 But du projet

**Objectif principal**: Développer un assistant personnel intelligent spécialement conçu pour les personnes atteintes de TDAH (Trouble du Déficit de l'Attention avec ou sans Hyperactivité) afin d'améliorer leur productivité, organisation et accomplissement d'objectifs personnels.

**Valeur ajoutée**: Utiliser les technologies LLM (Large Language Models) de pointe pour créer un système d'assistance qui intègre les techniques et stratégies spécifiques au TDAH, augmentant significativement les chances de succès dans l'atteinte des objectifs personnels.

### 1.1.2 Contexte affaires

**Problématique identifiée**: Les personnes atteintes de TDAH rencontrent des défis uniques dans la gestion du temps, l'organisation des tâches, la planification à long terme et le maintien de la motivation. Les solutions existantes ne sont souvent pas adaptées à leurs besoins cognitifs spécifiques.

**Opportunité technologique**: L'émergence des LLM avancés permet de créer un assistant intelligent capable de :

- Comprendre le contexte cognitif unique de chaque utilisateur
- Adapter les stratégies d'organisation selon les patterns TDAH
- Fournir un support personnalisé et contextuel
- Intégrer des données provenant de multiples applications pour une vue holistique

**Marché cible**: Individus diagnostiqués avec TDAH ou présentant des traits TDAH, cherchant à améliorer leur productivité personnelle et leur accomplissement d'objectifs.

### 1.1.3 Portée de la solution

**Fonctionnalités incluses**:

- Assistant conversationnel intelligent basé sur LLM
- Système de mémoire à long terme (LTM) pour la continuité des interactions
- Intégration avec des APIs tierces (calendrier, emails, notes, etc.)
- Outils de planification et de suivi d'objectifs
- Système de rappels et notifications intelligents
- Analyse des patterns comportementaux et optimisation continue
- Interface adaptée aux besoins cognitifs TDAH
- Accès direct des données personnelles aux utilisateurs \*\*

**Capacités techniques**:

- Architecture modulaire avec système d'outils extensibles
- Gestion intelligente de la mémoire et du contexte
- Intégration sécurisée avec des services externes
- Système de tags et de catégorisation intelligent
- Optimisation continue basée sur l'apprentissage machine

**APIs et services externes intégrés**:

- **Google Gemini API** : LLM principal pour l'assistance conversationnelle
- **Microsoft Graph API** : Intégration calendrier et emails
- **Twilio API** : Notifications SMS et communications
- **Notion API** : Gestion des notes et pages avec liens bidirectionnels
- **YouTube Data API v3** : Extraction de métadonnées et informations vidéo
- **YouTube Transcript API** : Récupération des transcriptions vidéo
- **DuckDuckGo Search API** : Recherche web et actualités
- **MSAL (Microsoft Authentication Library)** : Authentification OAuth Microsoft

### 1.1.4 Exclusions explicites

**Fonctionnalités non incluses**:

- Diagnostic médical ou évaluation clinique du TDAH
- Conseils médicaux ou thérapeutiques
- Gestion de projets d'équipe ou collaboration organisationnelle
- Intégration avec des systèmes ERP ou CRM d'entreprise
- Fonctionnalités de conformité réglementaire (SOX, GDPR, etc.)
- Support multilingue (version initiale en anglais uniquement)
- Applications mobiles natives (interface web responsive uniquement)

**Limitations techniques**:

- Pas de stockage de données médicales sensibles
- Pas d'intégration avec des systèmes de santé
- Pas de certification HIPAA ou équivalente
- Pas de support pour des environnements multi-utilisateurs partagés
- Pas de fonctionnalités de sauvegarde automatique cloud

**Contraintes réglementaires**:

- Conformité aux standards de protection des données personnelles
- Respect des réglementations sur l'accessibilité numérique
- Conformité aux standards de sécurité informatique de base

## 1.2 Stratégie, besoins et exigences

### 1.2.1 Stratégie

**Vue - Stratégique**

**Vision stratégique**: Devenir l'assistant personnel de référence pour les personnes atteintes de TDAH, en créant une plateforme qui unifie et analyse les données de multiples applications pour fournir des insights personnalisés et des recommandations adaptées aux besoins cognitifs spécifiques.

**Objectifs stratégiques à 5 ans**:

1. **Leadership du marché**: Positionner l'assistant comme la solution de référence pour la productivité TDAH
2. **Expansion internationale**: Déployer dans les marchés anglophones puis francophones
3. **Écosystème d'intégration**: Développer des partenariats avec les principales applications de productivité
4. **Modèle d'affaires durable**: Transition vers un modèle SaaS avec plans premium

**Positionnement stratégique**:

- **Différenciateur clé**: Intégration intelligente multi-apps avec analyse contextuelle TDAH
- **Avantage concurrentiel**: LLM spécialisé dans la compréhension des patterns cognitifs TDAH
- **Barrière à l'entrée**: Accumulation de données comportementales et d'apprentissage continu

**Explication de la stratégie**:
La stratégie repose sur trois piliers fondamentaux :

1. **Unification des données**: Agréger les informations de multiples applications (calendrier, emails, notes, tâches) pour créer une vue holistique de l'utilisateur
2. **Intelligence contextuelle**: Utiliser l'IA pour analyser les patterns et fournir des recommandations adaptées aux défis TDAH
3. **Propriété des données**: Garantir que chaque utilisateur conserve le contrôle total sur ses données personnelles

### 1.2.2 Positionnement du projet

**Positionnement dans l'écosystème TDAH**:

- **Niveau**: Assistant personnel intelligent (niveau individuel)
- **Rôle**: Facilitateur de productivité et d'organisation
- **Différenciation**: Approche technologique avancée vs. solutions traditionnelles

**Positionnement technologique**:

- **Architecture**: Système modulaire basé sur LLM avec intégration API
- **Innovation**: Première solution à combiner multi-apps, IA contextuelle et spécialisation TDAH
- **Évolutivité**: Conçu pour passer de l'usage individuel à l'usage organisationnel \*\*à changer

**Positionnement concurrentiel**:

- **Vs. Solutions générales**: Spécialisation TDAH et intégration multi-apps
- **Vs. Solutions TDAH traditionnelles**: Technologie de pointe et personnalisation continue
- **Vs. Assistants IA génériques**: Expertise domain-specific et compréhension des défis cognitifs

### 1.2.3 Besoins et exigences

Cette vue présente les besoins et exigences, fonctionnels et non-fonctionnels, ainsi que les contraintes connues d'initiatives, d'entreprise, technologiques et de sécurité.

Les modèles de solutions présentés dans ce livrable répondent à ces éléments. Pour bien comprendre les orientations décrites et modélisées dans ce document il est important de comprendre l'entièreté de ces éléments

En faisabilité, seuls les besoins et contraintes à haut-niveau sont définis. Lors de la phase de conception, un raffinement est appliqué et ces besoins sont déclinés en exigences plus détaillées

**Vue - Besoins et exigences**

**Explications des besoins et exigences**:

#### **Besoins fonctionnels prioritaires**:

**1. Intégration multi-applications**:

- **Besoins**: Connexion avec calendrier, emails, notes, tâches, et autres applications de productivité
- **Exigences**: APIs sécurisées, synchronisation en temps réel, gestion des erreurs de connexion
- **Capacités actuelles MVP**: ✅ Intégration calendrier, emails, notes, planning, LTM

**2. Unification et analyse des données**:

- **Besoins**: Regroupement intelligent des données de multiples sources pour créer des insights contextuels
- **Exigences**: Algorithmes d'agrégation, détection de patterns, corrélation temporelle
- **Capacités actuelles MVP**: ✅ Système LTM avec tags et catégorisation, RAG pour contexte

**3. Assistant conversationnel intelligent**:

- **Besoins**: Interface naturelle et intuitive pour interagir avec l'assistant
- **Exigences**: Réponses rapides (<2 secondes), compréhension contextuelle, personnalisation continue
- **Capacités actuelles MVP**: ✅ LLM Gemini intégré, gestion d'état, prompts optimisés TDAH

**4. Gestion de la mémoire et du contexte**:

- **Besoins**: Système de mémoire à long terme pour la continuité des interactions
- **Exigences**: Persistance des données, optimisation continue, récupération contextuelle
- **Capacités actuelles MVP**: ✅ Système LTM complet avec optimisation et cycle de vie

#### **Besoins non-fonctionnels critiques**:

**1. Performance et réactivité**:

- **Besoins**: Réponses rapides comme une conversation humaine
- **Exigences**: Latence <2 secondes, gestion optimisée des appels API, mise en cache intelligente
- **Contraintes techniques**: Limitation des appels API, optimisation des prompts LLM

**2. Sécurité et confidentialité**:

- **Besoins**: Protection des données personnelles et professionnelles
- **Exigences**: Chiffrement des données, authentification robuste, isolation des données utilisateur
- **Risques identifiés**: Données sensibles (emails, calendrier, notes personnelles)

**3. Disponibilité et fiabilité**:

- **Besoins**: Service disponible 24/7 avec récupération automatique
- **Exigences**: Uptime >99.5%, sauvegarde automatique, monitoring proactif
- **Contraintes opérationnelles**: Gestion des pannes API tierces, résilience système

**4. Évolutivité et extensibilité**:

- **Besoins**: Capacité à ajouter de nouvelles intégrations et fonctionnalités
- **Exigences**: Architecture modulaire, APIs extensibles, gestion des versions
- **Capacités actuelles MVP**: ✅ Système d'outils extensible, architecture modulaire

#### **Contraintes identifiées**:

**Contraintes technologiques**:

- **LLM** : Dépendance aux APIs Gemini, coûts par token
- **APIs tierces** : Limites de taux, disponibilité des services
- **Performance** : Équilibre entre rapidité et qualité des réponses

**Dépendances techniques détaillées**:

- **Google Services** : Gemini API, YouTube Data API v3, YouTube Transcript API
- **Microsoft Services** : Graph API, MSAL authentication, OAuth flows
- **Communication** : Twilio SMS API, gestion des tokens
- **Productivité** : Notion API, gestion des pages et liens bidirectionnels
- **Recherche** : DuckDuckGo Search API, gestion des limites de taux
- **Authentification** : MSAL OAuth, refresh tokens, stockage sécurisé
- **Bibliothèques Python** : notion_client, msal, youtube_transcript_api, duckduckgo_search, googleapiclient

**Contraintes de sécurité**:

- **Données sensibles** : Emails professionnels, informations personnelles
- **Conformité** : Respect des réglementations de protection des données
- **Authentification** : Gestion sécurisée des accès multi-apps
- **Tokens** : Stockage sécurisé des refresh tokens et clés API

**Contraintes opérationnelles**:

- **Monitoring**: Suivi des appels API et de la performance
- **Support**: Gestion des erreurs et assistance utilisateur
- **Évolutivité**: Passage de l'usage individuel à l'usage organisationnel

### 1.2.4 Réalisation des exigences

Cette vue permet de déterminer les exigences et contraintes significatives à la solution d'architecture, qui seront répondues dans l'architecture de la solution. Elle identifie également les capacités impactées par la solution

**Vue - Réalisation des exigences**

#### **1.2.4.1 Ébauche du registre des décisions d'architecture (alignements)**

**Décision 1: Architecture modulaire avec système d'outils**

- **Alignement**: Architecture d'entreprise (AE) - Principe de modularité
- **Justification**: Permet l'ajout facile de nouvelles intégrations et fonctionnalités
- **Impact**: Développement, maintenance, évolutivité

**Décision 2: Système de mémoire LTM avec optimisation continue**

- **Alignement**: AE - Principe d'apprentissage et d'adaptation
- **Justification**: Améliore la qualité des réponses et la personnalisation
- **Impact**: Performance, expérience utilisateur, données

**Décision 3: Intégration multi-APIs avec gestion d'erreurs**

- **Alignement**: AE - Principe de résilience et de robustesse
- **Justification**: Assure la fiabilité du service malgré les pannes tierces
- **Impact**: Disponibilité, expérience utilisateur, opérations

**Décision 4: LLM Gemini avec prompts optimisés TDAH**

- **Alignement**: AE - Principe d'innovation technologique
- **Justification**: Fournit des capacités d'IA de pointe spécialisées
- **Impact**: Qualité des réponses, différenciation, coûts

#### **1.2.4.2 Ébauche de la checklist de sécurité**

**Authentification et autorisation**:

- [ ] Système d'authentification multi-facteurs
- [ ] Gestion des sessions sécurisées
- [ ] Contrôle d'accès basé sur les rôles (RBAC)
- [ ] Isolation des données par utilisateur

**Protection des données**:

- [ ] Chiffrement des données en transit (TLS 1.3)
- [ ] Chiffrement des données au repos (AES-256)
- [ ] Gestion sécurisée des clés cryptographiques
- [ ] Classification et étiquetage des données

**Sécurité des APIs**:

- [ ] Validation des entrées et sorties
- [ ] Limitation des taux d'utilisation
- [ ] Monitoring des appels API suspects
- [ ] Gestion sécurisée des tokens d'accès

**Conformité et gouvernance**:

- [ ] Audit trail complet des actions
- [ ] Politique de rétention des données
- [ ] Conformité aux réglementations locales
- [ ] Tests de sécurité automatisés

**Monitoring et détection**:

- [ ] Surveillance continue de la sécurité
- [ ] Détection des anomalies comportementales
- [ ] Alertes en temps réel
- [ ] Plan de réponse aux incidents

## 1.3 Cas d'utilisation

### 1.3.1 Cas d'utilisation affaires

Cette vue montre les services d'affaires qui définissent les cas d'utilisation affaires, ainsi que leurs processus d'affaires associés. Les services applicatifs (cas d'utilisation systèmes) viennent réaliser les étapes de ces processus

**Vue - Cas d'utilisation affaires**

**Tableau 1.3.1 - Cas d'utilisation affaires et processus associés**

| Cas d'utilisation affaires                     | Défis TDAH                                                                         | Processus d'affaires                                                                              | Services applicatifs requis                                                    |
| ---------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Gestion des tâches et objectifs**            | Oubli des tâches, perte de motivation, difficulté à décomposer les projets         | Détection d'inactivité → Analyse du blocage → Décomposition en sous-tâches → Motivation adaptée   | Service de gestion des tâches, Système de rappels intelligents                 |
| **Planification et organisation du temps**     | Difficulté à estimer le temps, surcharge cognitive, procrastination                | Analyse des patterns → Création de plages de temps → Intégration calendrier → Rappels contextuels | Service de planification, Intégration calendrier, Système de time boxing       |
| **Gestion de la mémoire et du contexte**       | Perte de contexte, difficulté à maintenir la continuité, dispersion de l'attention | Capture des informations → Tagging intelligent → Récupération contextuelle → Maintien du focus    | Service LTM, Système de tags, Gestion des focus areas                          |
| **Communication et suivi**                     | Oubli des communications importantes, difficulté à suivre les conversations        | Analyse des emails → Identification des priorités → Création de tâches → Suivi des actions        | Service d'intégration emails, Système de suivi, Création automatique de tâches |
| **Recherche et organisation des informations** | Difficulté à organiser et retrouver les informations importantes                   | Capture des informations → Organisation automatique → Recherche intelligente → Contexte enrichi   | Service de notes, Système de tags, Recherche contextuelle                      |

**Explication des cas d'utilisation affaires**:

#### **Cas d'utilisation principal: Gestion de la productivité personnelle pour personnes TDAH**

**Service d'affaires**: Assistant personnel intelligent pour l'optimisation de la productivité et de l'organisation

**Processus d'affaires associés**:

**1. Gestion des tâches et objectifs**

- **Défi TDAH**: Oubli des tâches, perte de motivation, difficulté à décomposer les projets complexes
- **Solution**: Système de rappels intelligents avec décomposition automatique des tâches
- **Processus**: Détection d'inactivité → Analyse du blocage → Décomposition en sous-tâches → Motivation adaptée

**2. Planification et organisation du temps**

- **Défi TDAH**: Difficulté à estimer le temps, surcharge cognitive, procrastination
- **Solution**: Planification intelligente avec "time boxing" et pauses naturelles
- **Processus**: Analyse des patterns → Création de plages de temps → Intégration calendrier → Rappels contextuels

**3. Gestion de la mémoire et du contexte**

- **Défi TDAH**: Perte de contexte, difficulté à maintenir la continuité, dispersion de l'attention
- **Solution**: Système LTM avec récupération contextuelle et focus areas
- **Processus**: Capture des informations → Tagging intelligent → Récupération contextuelle → Maintien du focus

**4. Communication et suivi**

- **Défi TDAH**: Oubli des communications importantes, difficulté à suivre les conversations
- **Solution**: Intégration emails avec suivi et rappels intelligents
- **Processus**: Analyse des emails → Identification des priorités → Création de tâches → Suivi des actions

**5. Recherche et organisation des informations**

- **Défi TDAH**: Difficulté à organiser et retrouver les informations importantes
- **Solution**: Système de notes avec tags intelligents et recherche contextuelle
- **Processus**: Capture des informations → Organisation automatique → Recherche intelligente → Contexte enrichi

### 1.3.2 Cas d'utilisation applicatifs

Cette vue permet de représenter les cas d'utilisation applicatifs (services applicatifs théoriques requis par la solution) dans le contexte des acteurs impliqués

**Vue - Cas d'utilisation applicatifs**

```mermaid
graph TB
    subgraph "👥 Acteurs"
        USER[👤 Utilisateur TDAH]
        SYSTEM[🤖 Système Assistant<br/>Agent Core + Runner + Planner]
        EXTERNAL_APIS[🔌 APIs Externes]
    end

    subgraph "🛠️ Services applicatifs"
        AUTH_SERVICE[🔐 Service d'authentification]
        CONVERSATION_SERVICE[💬 Service de conversation]
        MEMORY_SERVICE[🧠 Service de mémoire LTM]
        INTEGRATION_SERVICE[🔗 Service d'intégration]
        PLANNING_SERVICE[📅 Service de planification]
        NOTIFICATION_SERVICE[🔔 Service de notifications]
        RAG_SERVICE[🔍 Service RAG<br/>Recherche sémantique]
        TOOL_SERVICE[🛠️ Service d'outils<br/>Registry des outils]
        API_SERVICE[🚀 Service d'API REST<br/>FastAPI Backend]
        WEBHOOK_SERVICE[📡 Service de webhooks<br/>Twilio SMS]
    end

    %% ===== FLUX PRINCIPAL : Conversation directe =====
    USER <--> CONVERSATION_SERVICE
    CONVERSATION_SERVICE <--> SYSTEM

    %% ===== FLUX API : Interface REST =====
    USER <--> API_SERVICE
    API_SERVICE <--> SYSTEM

    %% ===== FLUX WEBHOOK : Interface SMS =====
    USER <--> WEBHOOK_SERVICE
    WEBHOOK_SERVICE <--> SYSTEM

    %% ===== SYSTÈME ASSISTANT ORCHESTRE TOUS LES SERVICES =====
    SYSTEM --> MEMORY_SERVICE
    SYSTEM --> RAG_SERVICE
    SYSTEM --> TOOL_SERVICE
    SYSTEM --> PLANNING_SERVICE

    %% ===== SERVICES COMMUNIQUENT ENTRE EUX =====
    TOOL_SERVICE --> INTEGRATION_SERVICE
    INTEGRATION_SERVICE --> EXTERNAL_APIS

    %% ===== NOTIFICATIONS RETOURNENT À L'UTILISATEUR =====
    PLANNING_SERVICE --> NOTIFICATION_SERVICE
    NOTIFICATION_SERVICE --> USER

    %% ===== AUTHENTIFICATION POUR TOUS LES SERVICES =====
    AUTH_SERVICE --> SYSTEM
    AUTH_SERVICE --> MEMORY_SERVICE
    AUTH_SERVICE --> PLANNING_SERVICE

    %% ===== STYLE ET COULEURS =====
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef systemClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:1px
    classDef flowClass fill:#fff3e0,stroke:#e65100,stroke-width:1px

    class USER userClass
    class SYSTEM systemClass
    class CONVERSATION_SERVICE,API_SERVICE,WEBHOOK_SERVICE,MEMORY_SERVICE,RAG_SERVICE,TOOL_SERVICE,PLANNING_SERVICE,NOTIFICATION_SERVICE,INTEGRATION_SERVICE,AUTH_SERVICE serviceClass
    class EXTERNAL_APIS flowClass
```

**Explication des cas d'utilisation applicatifs**:

Les services applicatifs sont conçus pour supporter chaque étape du processus d'affaires, avec une **architecture modulaire centrée sur le Système Assistant** qui orchestre tout le flux :

### **🔄 Communication bidirectionnelle complète :**

#### **1. Interface Conversation (Directe) :**

- **USER ↔ CONVERSATION_SERVICE ↔ SYSTEM** : Communication bidirectionnelle directe
- **Messages entrent** : L'utilisateur envoie des requêtes
- **Réponses sortent** : Le système retourne des réponses via la même interface

#### **2. Interface API REST :**

- **USER ↔ API_SERVICE ↔ SYSTEM** : Communication bidirectionnelle via API
- **Messages entrent** : Requêtes HTTP vers l'API
- **Réponses sortent** : Réponses JSON/XML via l'API

#### **3. Interface SMS (Webhooks) :**

- **USER ↔ WEBHOOK_SERVICE ↔ SYSTEM** : Communication bidirectionnelle via SMS
- **Messages entrent** : SMS reçus via webhooks Twilio
- **Réponses sortent** : SMS envoyés via Twilio

### **🧠 Flux principal orchestré par le Système Assistant :**

1. **Utilisateur** ↔ **Interface** (Conversation/API/SMS) ↔ **Système Assistant**
2. **Système Assistant** → **Mémoire LTM** (récupération du contexte)
3. **Système Assistant** → **Service RAG** (recherche sémantique)
4. **Système Assistant** → **Service d'outils** (exécution des actions)
5. **Service d'outils** → **Service d'intégration** → **APIs externes**
6. **Système Assistant** → **Service de planification** (création/modification des plans)
7. **Service de planification** → **Service de notifications** → **Utilisateur**

### **🎯 Interfaces utilisateur multiples (Architecture hybride) :**

#### **Interface Conversation (Directe) - ✅ Implémentée :**

- **Communication bidirectionnelle** : Messages entrent et réponses sortent
- **Intégration directe** : Connexion directe au Système Assistant
- **Utilisation** : Tests, développement, administration

#### **Interface SMS (Principale) - ✅ Implémentée :**

- **Service de webhooks** : Gestion des messages SMS entrants via Twilio
- **Service de notifications** : Envoi de SMS de réponse via Twilio
- **Accessibilité universelle** : Fonctionne sans internet, simple d'usage
- **Communication bidirectionnelle** : SMS reçus → Traitement → SMS envoyés

#### **Interface CLI (Basique) - ✅ Implémentée :**

- **Commandes système** : Status, traitement de messages
- **Gestion administrative** : Commandes de base pour la maintenance
- **Communication bidirectionnelle** : Commandes entrent, résultats sortent

#### **Interface API (Partielle) - 🔄 Partiellement implémentée :**

- **Service d'API REST** : Backend FastAPI avec endpoints Twilio
- **Webhooks Twilio** : Gestion des SMS entrants et sortants
- **Communication bidirectionnelle** : Requêtes HTTP → Traitement → Réponses HTTP
- **Statut actuel** : API basique, endpoints utilisateurs manquants
- **Évolution prévue** : Interface web complète en Phase 2

### **🌟 Rôle central du Système Assistant :**

- **Orchestrateur principal** : Coordonne tous les services
- **Gestionnaire de contexte** : Maintient l'état de la conversation
- **Décideur d'actions** : Utilise le LLM pour choisir les actions
- **Exécuteur d'outils** : Lance les outils appropriés
- **Gestionnaire de mémoire** : Sauvegarde et récupère le contexte
- **Point d'unification** : Toutes les interfaces convergent vers lui
- **Générateur de réponses** : Crée les réponses qui retournent à l'utilisateur

### **💡 Avantages de l'architecture hybride bidirectionnelle :**

1. **SMS comme interface principale** : Simplicité, accessibilité, pas d'internet requis
2. **CLI pour la gestion système** : Maintenance et administration
3. **API pour l'extensibilité** : Intégrations futures et interface web
4. **Unification par le Système Assistant** : Cohérence des réponses et du contexte
5. **Communication complète** : Chaque interface supporte l'envoi ET la réception
6. **Flexibilité maximale** : L'utilisateur peut choisir l'interface qui lui convient

**Description des impacts des cas d'utilisation applicatifs**

| Acteur                   | Impacts                                                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| **Utilisateur TDAH**     | Interface adaptée, notifications contextuelles, support personnalisé, communication bidirectionnelle complète   |
| **Système Assistant**    | **Gestion de la mémoire, apprentissage continu, optimisation des réponses, orchestration de tous les services** |
| **APIs Externes**        | Intégration sécurisée, gestion des erreurs, fallback gracieux                                                   |
| **Interfaces multiples** | **Flexibilité d'accès, simplicité SMS, extensibilité API, maintenance CLI, communication bidirectionnelle**     |

## 1.4 Dépendances techniques et services externes

Cette section documente l'ensemble des dépendances techniques, bibliothèques et services externes nécessaires au fonctionnement de la solution.

### 1.4.1 Dépendances Python et bibliothèques

**Frameworks et bibliothèques principales**:

- **FastAPI** : Framework web asynchrone pour l'API backend
- **SQLAlchemy** : ORM pour la gestion de base de données
- **Pydantic** : Validation des données et sérialisation
- **Uvicorn** : Serveur ASGI pour FastAPI

**Bibliothèques d'intégration**:

- **notion_client** : Client officiel Notion pour la gestion des pages et notes
- **msal** : Microsoft Authentication Library pour l'authentification OAuth
- **youtube_transcript_api** : API pour récupérer les transcriptions YouTube
- **duckduckgo_search** : Client pour l'API de recherche DuckDuckGo
- **google-api-python-client** : Client Google pour YouTube Data API v3
- **twilio** : Client pour l'API SMS et communications Twilio

**Bibliothèques de support**:

- **asyncpg** : Driver PostgreSQL asynchrone
- **redis** : Client Redis pour le cache et les queues
- **celery** : Gestion des tâches asynchrones en arrière-plan
- **aiohttp** : Client HTTP asynchrone pour les appels API

**Bibliothèques de sécurité**:

- **PyJWT** : Gestion des JWT tokens pour l'authentification
- **passlib** : Hachage sécurisé des mots de passe
- **cryptography** : Chiffrement AES-256 des données sensibles
- **python-jose** : Chiffrement JWE/JWS avancé

**Bibliothèques de monitoring**:

- **structlog** : Logging structuré pour l'observabilité
- **prometheus-client** : Métriques Prometheus
- **opentelemetry** : Traçage distribué des requêtes

**Bibliothèques de performance**:

- **aioredis** : Client Redis asynchrone haute performance
- **orjson** : Sérialisation JSON ultra-rapide
- **cachetools** : Cache en mémoire avec TTL

**Bibliothèques de développement**:

- **alembic** : Gestion des migrations de base de données
- **factory-boy** : Factories pour les tests
- **black** : Formatage automatique du code
- **mypy** : Vérification de types statique

**Gestion des migrations**:

- **Alembic** : Migrations de base de données versionnées
- **PostgreSQL Extensions** : pg_trgm, pg_stat_statements, pgcrypto

**Monitoring et observabilité**:

- **Prometheus** : Collecte des métriques
- **Grafana** : Visualisation des métriques
- **OpenTelemetry** : Traçage distribué

**Sécurité et conformité**:

- **HashiCorp Vault** : Gestion des secrets
- **Chiffrement AES-256** : Protection des données sensibles
- **Audit trail** : Traçabilité complète des actions

### 1.4.2 Services externes et APIs

**Google Services**:

- **Gemini API** : LLM principal pour l'assistance conversationnelle

  - Endpoint : `https://generativelanguage.googleapis.com/`
  - Authentification : Clé API
  - Limites : Quotas par token, coûts par requête
  - Utilisation : Génération de réponses, analyse de contexte

- **YouTube Data API v3** : Métadonnées et informations vidéo

  - Endpoint : `https://www.googleapis.com/youtube/v3/`
  - Authentification : Clé API
  - Limites : 10,000 requêtes/jour, quotas quotidiens
  - Utilisation : Extraction d'informations vidéo, recherche de contenu

- **YouTube Transcript API** : Transcriptions vidéo
  - Endpoint : Service tiers non officiel
  - Authentification : Aucune (service public)
  - Limites : Rate limiting, disponibilité variable
  - Utilisation : Récupération de transcriptions pour analyse

**Microsoft Services**:

- **Microsoft Graph API** : Calendrier, emails et authentification

  - Endpoint : `https://graph.microsoft.com/v1.0/`
  - Authentification : OAuth 2.0 avec MSAL
  - Scopes : Calendars.ReadWrite, Mail.ReadWrite, User.Read
  - Utilisation : Gestion calendrier, emails, profil utilisateur

- **MSAL (Microsoft Authentication Library)** : Authentification OAuth
  - Endpoint : `https://login.microsoftonline.com/consumers/`
  - Authentification : OAuth 2.0 avec refresh tokens
  - Stockage : Fichier local refresh_token.txt
  - Utilisation : Gestion des sessions Microsoft

**Services de communication**:

- **Twilio API** : SMS et communications
  - Endpoint : `https://api.twilio.com/`
  - Authentification : Account SID + Auth Token
  - Limites : Quotas par compte, coûts par SMS
  - Utilisation : Notifications, rappels, communications

**Services de productivité**:

- **Notion API** : Gestion des notes et pages
  - Endpoint : `https://api.notion.com/v1/`
  - Authentification : Token d'intégration
  - Limites : Rate limiting, quotas par workspace
  - Utilisation : Création de notes, gestion des pages, liens bidirectionnels

**Services de recherche**:

- **DuckDuckGo Search API** : Recherche web et actualités
  - Endpoint : Service public via bibliothèque Python
  - Authentification : Aucune
  - Limites : Rate limiting, pas de quotas officiels
  - Utilisation : Recherche web, actualités, images

### 1.4.3 Dépendances d'infrastructure

**Base de données**:

- **PostgreSQL** : Base de données principale
  - Version : 15+ (recommandé 16+)
  - Extensions : jsonb, uuid, pg_trgm
  - Performance : Indexation, connexions poolées

**Cache et queues**:

- **Redis** : Cache et gestion des queues
  - Version : 6.2+
  - Utilisation : Cache des réponses, sessions, queues de tâches

**Stockage de fichiers**:

- **Système de fichiers local** : Stockage des images et documents
  - Structure : Organisée par utilisateur et type
  - Sécurité : Isolation des données par utilisateur

### 1.4.4 Gestion des dépendances

**Variables d'environnement requises**:

```bash
# Google Services
GOOGLE_API_KEY=your_gemini_api_key
YOUTUBE_API_KEY=your_youtube_api_key

# Microsoft Services
MICROSOFT_APPLICATION_ID=your_app_id
MICROSOFT_CLIENT_SECRET=your_client_secret

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# Notion
NOTION_API_KEY=your_notion_integration_token

# Base de données
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# Redis
REDIS_URL=redis://localhost:6379
```

**Gestion des tokens et authentification**:

- **Refresh tokens** : Stockage sécurisé des tokens de renouvellement
- **Rotation des clés** : Processus de rotation des clés API
- **Monitoring** : Surveillance des quotas et limites d'API
- **Fallback** : Stratégies de dégradation en cas d'indisponibilité

**Limites et quotas**:

- **Gemini API** : Quotas par projet, coûts par token
- **YouTube API** : 10,000 requêtes/jour, quotas quotidiens
- **Microsoft Graph** : Rate limiting, quotas par application
- **Twilio** : Quotas par compte, coûts par SMS
- **Notion** : Rate limiting, quotas par workspace

### 1.4.5 Risques et mitigation

**Risques identifiés**:

- **Dépendance aux APIs tierces** : Indisponibilité des services externes
- **Limites de taux** : Dépassement des quotas et limitations
- **Coûts variables** : Fluctuation des coûts des APIs
- **Évolution des APIs** : Changements dans les interfaces externes

**Stratégies de mitigation**:

- **Cache intelligent** : Mise en cache des réponses pour réduire les appels API
- **Fallback gracieux** : Dégradation des fonctionnalités en cas d'indisponibilité
- **Monitoring proactif** : Surveillance des quotas et alertes préventives
- **Architecture résiliente** : Gestion des erreurs et retry automatique
- **Documentation des dépendances** : Mise à jour continue des intégrations
