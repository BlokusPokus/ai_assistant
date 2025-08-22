# 1. Définition

## 1.1 But, contexte affaires, portée et exclusions

Ce document présente les modèles servant à former et orienter la solution. Dans le but de comprendre le contexte de l'initiative, sa portée ainsi que ses exclusions

### 1.1.1 But du projet

## 1.2 But du projet

**Objectif principal** : Transformer l'infrastructure technologique de l'assistant personnel TDAH d'un environnement de développement local vers une plateforme d'exploitation de production robuste et sécurisée, **supportant une architecture multi-utilisateurs avec authentification OAuth progressive**.

**Contexte** : L'assistant personnel TDAH nécessite une infrastructure d'exploitation de niveau entreprise pour supporter la production multi-utilisateurs, incluant la conteneurisation, la sécurité renforcée, l'observabilité et la haute disponibilité. **Chaque utilisateur doit pouvoir connecter ses propres comptes de services externes (Notion, Google, Microsoft, etc.) via OAuth**.

**Solution** : Mise en place d'une architecture conteneurisée avec Docker, migration vers PostgreSQL, ajout de Redis, implémentation d'un proxy inverse sécurisé, **système d'authentification OAuth progressif par service**, et déploiement d'une stack de monitoring complète pour l'exploitation en production multi-utilisateurs.

**Valeur ajoutée**: Utiliser les technologies LLM (Large Language Models) de pointe pour créer un système d'assistance qui intègre les techniques et stratégies spécifiques au TDAH, augmentant significativement les chances de succès dans l'atteinte des objectifs personnels.

### 1.1.2 Contexte affaires

**Problématique identifiée** : Les personnes atteintes de TDAH rencontrent des défis uniques dans la gestion du temps, l'organisation des tâches, la planification à long terme et le maintien de la motivation. Les solutions existantes ne sont souvent pas adaptées à leurs besoins cognitifs spécifiques. **De plus, l'architecture actuelle en développement ne supporte qu'un seul utilisateur, limitant la scalabilité et la viabilité commerciale**.

**Opportunité technologique** : L'émergence des LLM avancés permet de créer un assistant intelligent capable de :

- Comprendre le contexte cognitif unique de chaque utilisateur
- Adapter les stratégies d'organisation selon les patterns TDAH
- Fournir un support personnalisé et contextuel
- Intégrer des données provenant de multiples applications pour une vue holistique
- **Supporter une architecture multi-utilisateurs avec authentification OAuth progressive**
- **Permettre l'activation granulaire des fonctionnalités selon les besoins de chaque utilisateur**

**Marché cible** : Individus diagnostiqués avec TDAH ou présentant des traits TDAH, cherchant à améliorer leur productivité personnelle et leur accomplissement d'objectifs. **L'architecture multi-utilisateurs permet de cibler des organisations, des praticiens de santé mentale, et des plateformes éducatives**.

### 1.1.3 Portée de la solution

**Fonctionnalités incluses**:

- Assistant conversationnel intelligent basé sur LLM
- Système de mémoire à long terme (LTM) pour la continuité des interactions
- **Intégration multi-utilisateurs avec authentification OAuth progressive**
- **Activation granulaire des fonctionnalités par service connecté**
- Intégration avec des APIs tierces (calendrier, emails, notes, etc.) **via OAuth utilisateur**
- Outils de planification et de suivi d'objectifs
- Système de rappels et notifications intelligents
- Analyse des patterns comportementaux et optimisation continue
- Interface adaptée aux besoins cognitifs TDAH
- **Accès direct des données personnelles aux utilisateurs avec isolation stricte**
- **Synchronisation cross-platform entre interface SMS et web dashboard**

**Capacités techniques**:

- Architecture modulaire avec système d'outils extensibles
- **Architecture multi-utilisateurs avec isolation stricte des données**
- **Système d'authentification OAuth progressif par service**
- **Gestion granulaire des fonctionnalités et permissions**
- Gestion intelligente de la mémoire et du contexte
- Intégration sécurisée avec des services externes
- Système de tags et de catégorisation intelligent
- Optimisation continue basée sur l'apprentissage machine
- **Synchronisation en temps réel entre interfaces SMS et web**
- **Stratégie de numéro Twilio unique avec identification utilisateur**

**APIs et services externes intégrés**:

- **Google Gemini API** : LLM principal pour l'assistance conversationnelle
- **Microsoft Graph API** : Intégration calendrier et emails **via OAuth utilisateur**
- **Twilio API** : **Interface SMS principale avec numéro unique et identification utilisateur**
- **Notion API** : Gestion des notes et pages **via OAuth utilisateur**
- **YouTube Data API v3** : Extraction de métadonnées et informations vidéo **via OAuth utilisateur**
- **YouTube Transcript API** : Récupération des transcriptions vidéo
- **DuckDuckGo Search API** : Recherche web et actualités
- **MSAL (Microsoft Authentication Library)** : Authentification OAuth Microsoft **par utilisateur**

### 1.1.4 Exclusions explicites

**Fonctionnalités non incluses**:

- Diagnostic médical ou évaluation clinique du TDAH
- Conseils médicaux ou thérapeutiques
- Gestion de projets d'équipe ou collaboration organisationnelle
- Intégration avec des systèmes ERP ou CRM d'entreprise
- Fonctionnalités de conformité réglementaire (SOX, GDPR, etc.)
- Support multilingue (version initiale en anglais uniquement)
- Applications mobiles natives (interface web responsive uniquement)
- **Gestion d'équipe ou collaboration multi-utilisateurs partagés**
- **Partage de données entre utilisateurs**

**Limitations techniques**:

- Pas de stockage de données médicales sensibles
- Pas d'intégration avec des systèmes de santé
- Pas de certification HIPAA ou équivalente
- **Pas de support pour des environnements multi-utilisateurs partagés** (remplacé par architecture multi-utilisateurs isolés)
- Pas de fonctionnalités de sauvegarde automatique cloud
- **Pas de gestion centralisée des clés API** (remplacé par OAuth utilisateur)

**Contraintes réglementaires**:

- Conformité aux standards de protection des données personnelles
- Respect des réglementations sur l'accessibilité numérique
- Conformité aux standards de sécurité informatique de base
- **Isolation stricte des données utilisateur** (principe fondamental)
- **Gestion des consentements OAuth** par utilisateur et par service

## 1.2 Stratégie, besoins et exigences

### 1.2.1 Stratégie

**Vue - Stratégique**

**Vision stratégique**: Devenir l'assistant personnel de référence pour les personnes atteintes de TDAH, en créant une plateforme qui unifie et analyse les données de multiples applications pour fournir des insights personnalisés et des recommandations adaptées aux besoins cognitifs spécifiques.

**Objectifs stratégiques à 5 ans**:

1. **Leadership du marché**: Positionner l'assistant comme la solution de référence pour la productivité TDAH **avec support multi-utilisateurs**
2. **Expansion internationale**: Déployer dans les marchés anglophones puis francophones **avec architecture OAuth locale**
3. **Écosystème d'intégration**: Développer des partenariats avec les principales applications de productivité **via OAuth standardisé**
4. **Modèle d'affaires durable**: Transition vers un modèle SaaS avec plans premium **et facturation par utilisateur**
5. **Architecture multi-utilisateurs**: **Support de 1000+ utilisateurs simultanés avec isolation stricte des données**

**Positionnement stratégique**:

- **Différenciateur clé**: Intégration intelligente multi-apps avec analyse contextuelle TDAH **et authentification OAuth progressive**
- **Avantage concurrentiel**: LLM spécialisé dans la compréhension des patterns cognitifs TDAH **avec architecture multi-utilisateurs**
- **Barrière à l'entrée**: Accumulation de données comportementales et d'apprentissage continu **par utilisateur**
- **Scalabilité**: **Architecture conçue pour passer de l'usage individuel à l'usage organisationnel via OAuth**

**Explication de la stratégie**:
La stratégie repose sur trois piliers fondamentaux :

1. **Unification des données**: Agréger les informations de multiples applications (calendrier, emails, notes, tâches) pour créer une vue holistique de l'utilisateur **via OAuth**
2. **Intelligence contextuelle**: Utiliser l'IA pour analyser les patterns et fournir des recommandations adaptées aux défis TDAH **avec contexte utilisateur isolé**
3. **Propriété des données**: Garantir que chaque utilisateur conserve le contrôle total sur ses données personnelles **avec isolation stricte multi-utilisateurs**
4. **Authentification progressive**: **Permettre aux utilisateurs d'activer les fonctionnalités selon leurs besoins via OAuth**

### 1.2.2 Positionnement du projet

**Positionnement dans l'écosystème TDAH**:

- **Niveau**: Assistant personnel intelligent (niveau individuel) **avec support multi-utilisateurs**
- **Rôle**: Facilitateur de productivité et d'organisation **via authentification OAuth progressive**
- **Différenciation**: Approche technologique avancée vs. solutions traditionnelles **avec architecture multi-utilisateurs**

**Positionnement technologique**:

- **Architecture**: Système modulaire basé sur LLM avec intégration API **et authentification OAuth par utilisateur**
- **Innovation**: Première solution à combiner multi-apps, IA contextuelle, spécialisation TDAH **et architecture multi-utilisateurs avec OAuth**
- **Évolutivité**: Conçu pour passer de l'usage individuel à l'usage organisationnel **via authentification OAuth progressive**

**Positionnement concurrentiel**:

- **Vs. Solutions générales**: Spécialisation TDAH et intégration multi-apps **avec support multi-utilisateurs**
- **Vs. Solutions TDAH traditionnelles**: Technologie de pointe et personnalisation continue **via OAuth et isolation des données**
- **Vs. Assistants IA génériques**: Expertise domain-specific et compréhension des défis cognitifs **avec architecture multi-utilisateurs**

### 1.2.3 Besoins et exigences

Cette vue présente les besoins et exigences, fonctionnels et non-fonctionnels, ainsi que les contraintes connues d'initiatives, d'entreprise, technologiques et de sécurité.

Les modèles de solutions présentés dans ce livrable répondent à ces éléments. Pour bien comprendre les orientations décrites et modélisées dans ce document il est important de comprendre l'entièreté de ces éléments

En faisabilité, seuls les besoins et contraintes à haut-niveau sont définis. Lors de la phase de conception, un raffinement est appliqué et ces besoins sont déclinés en exigences plus détaillées

**Vue - Besoins et exigences**

**Explications des besoins et exigences**:

#### **Besoins fonctionnels prioritaires**:

**1. Intégration multi-applications avec OAuth**:

- **Besoins**: Connexion avec calendrier, emails, notes, tâches, et autres applications de productivité **via OAuth utilisateur**
- **Exigences**: **APIs OAuth sécurisées par utilisateur**, synchronisation en temps réel, gestion des erreurs de connexion, **activation granulaire des fonctionnalités**
- **Capacités actuelles MVP**: ✅ Intégration calendrier, emails, notes, planning, LTM **pour utilisateur unique**
- **Capacités cibles Phase 2**: 🔄 **Architecture multi-utilisateurs avec OAuth progressif et activation granulaire**

**2. Unification et analyse des données multi-utilisateurs**:

- **Besoins**: Regroupement intelligent des données de multiples sources pour créer des insights contextuels **avec isolation stricte par utilisateur**
- **Exigences**: Algorithmes d'agrégation, détection de patterns, corrélation temporelle, **isolation des données utilisateur**
- **Capacités actuelles MVP**: ✅ Système LTM avec tags et catégorisation, RAG pour contexte **utilisateur unique**
- **Capacités cibles Phase 2**: 🔄 **LTM multi-utilisateurs avec isolation stricte et contexte utilisateur**

**3. Assistant conversationnel intelligent multi-utilisateurs**:

- **Besoins**: Interface naturelle et intuitive pour interagir avec l'assistant **avec support multi-utilisateurs**
- **Exigences**: Réponses rapides (<2 secondes), compréhension contextuelle, personnalisation continue, **identification et isolation utilisateur**
- **Capacités actuelles MVP**: ✅ LLM Gemini intégré, gestion d'état, prompts optimisés TDAH **pour utilisateur unique**
- **Capacités cibles Phase 2**: 🔄 **LLM multi-utilisateurs avec contexte utilisateur isolé et prompts personnalisés**

**4. Gestion de la mémoire et du contexte multi-utilisateurs**:

- **Besoins**: Système de mémoire à long terme pour la continuité des interactions **avec isolation stricte par utilisateur**
- **Exigences**: Persistance des données, optimisation continue, récupération contextuelle, **isolation des données utilisateur**
- **Capacités actuelles MVP**: ✅ Système LTM complet avec optimisation et cycle de vie **pour utilisateur unique**
- **Capacités cibles Phase 2**: 🔄 **LTM multi-utilisateurs avec isolation stricte et optimisation par utilisateur**

#### **Besoins non-fonctionnels critiques**:

**1. Performance et réactivité multi-utilisateurs**:

- **Besoins**: Réponses rapides comme une conversation humaine **avec support de 1000+ utilisateurs simultanés**
- **Exigences**: Latence <2 secondes, gestion optimisée des appels API, mise en cache intelligente, **isolation des performances par utilisateur**
- **Contraintes techniques**: Limitation des appels API, optimisation des prompts LLM, **gestion des ressources multi-utilisateurs**

**2. Sécurité et confidentialité multi-utilisateurs**:

- **Besoins**: Protection des données personnelles et professionnelles **avec isolation stricte entre utilisateurs**
- **Exigences**: Chiffrement des données, authentification robuste, **isolation stricte des données utilisateur**, **gestion OAuth sécurisée**
- **Risques identifiés**: Données sensibles (emails, calendrier, notes personnelles), **fuite de données entre utilisateurs**

**3. Disponibilité et fiabilité multi-utilisateurs**:

- **Besoins**: Service disponible 24/7 avec récupération automatique **pour tous les utilisateurs**
- **Exigences**: Uptime >99.5%, sauvegarde automatique, monitoring proactif, **isolation des pannes par utilisateur**
- **Contraintes opérationnelles**: Gestion des pannes API tierces, résilience système, **gestion des sessions multi-utilisateurs**

**4. Évolutivité et extensibilité multi-utilisateurs**:

- **Besoins**: Capacité à ajouter de nouveaux utilisateurs et de nouvelles intégrations **via OAuth progressif**
- **Exigences**: Architecture modulaire, APIs extensibles, gestion des versions, **scalabilité horizontale des utilisateurs**
- **Capacités actuelles MVP**: ✅ Système d'outils extensible, architecture modulaire **pour utilisateur unique**
- **Capacités cibles Phase 2**: 🔄 **Architecture multi-utilisateurs avec OAuth progressif et activation granulaire**

#### **Contraintes identifiées**:

**Contraintes technologiques**:

- **LLM** : Dépendance aux APIs Gemini, coûts par token, **gestion multi-utilisateurs**
- **APIs tierces** : **Limites OAuth par utilisateur**, disponibilité des services, **gestion des refresh tokens**
- **Performance** : Équilibre entre rapidité et qualité des réponses, **isolation des ressources par utilisateur**

**Dépendances techniques détaillées**:

- **Google Services** : Gemini API, YouTube Data API v3, YouTube Transcript API **via OAuth utilisateur**
- **Microsoft Services** : Graph API, MSAL authentication, **OAuth flows par utilisateur**
- **Communication** : **Twilio SMS API avec numéro unique et identification utilisateur**
- **Productivité** : Notion API, **gestion des pages et liens bidirectionnels via OAuth utilisateur**
- **Recherche** : DuckDuckGo Search API, gestion des limites de taux
- **Authentification** : **MSAL OAuth par utilisateur**, refresh tokens, stockage sécurisé, **gestion des sessions multi-utilisateurs**
- **Bibliothèques Python** : notion_client, msal, youtube_transcript_api, duckduckgo_search, googleapiclient

**Contraintes de sécurité multi-utilisateurs**:

- **Données sensibles** : Emails professionnels, informations personnelles, **isolation stricte entre utilisateurs**
- **Conformité** : Respect des réglementations de protection des données, **gestion des consentements OAuth**
- **Authentification** : **Gestion sécurisée des accès multi-utilisateurs**, **OAuth progressif par service**
- **Tokens** : **Stockage sécurisé des refresh tokens OAuth par utilisateur**, rotation des clés

**Contraintes opérationnelles multi-utilisateurs**:

- **Monitoring**: Suivi des appels API et de la performance **par utilisateur**
- **Support**: Gestion des erreurs et assistance utilisateur **avec isolation des problèmes**
- **Évolutivité**: **Passage de l'usage individuel à l'usage multi-utilisateurs via OAuth**
- **Synchronisation**: **Gestion de la synchronisation cross-platform entre SMS et web dashboard**

### 1.2.4 Réalisation des exigences

Cette vue permet de déterminer les exigences et contraintes significatives à la solution d'architecture, qui seront répondues dans l'architecture de la solution. Elle identifie également les capacités impactées par la solution

**Vue - Réalisation des exigences**

#### **1.2.4.1 Ébauche du registre des décisions d'architecture (alignements)**

**Décision 1: Architecture multi-utilisateurs avec isolation stricte**

- **Alignement**: Architecture d'entreprise (AE) - Principe de modularité et isolation
- **Justification**: Permet le support de multiples utilisateurs avec sécurité et isolation des données
- **Impact**: Développement, maintenance, évolutivité, **sécurité multi-utilisateurs**

**Décision 2: Authentification OAuth progressive par service**

- **Alignement**: AE - Principe de sécurité et d'authentification
- **Justification**: Chaque utilisateur connecte ses propres comptes de services externes
- **Impact**: Sécurité, isolation des données, **activation granulaire des fonctionnalités**

**Décision 3: Système de mémoire LTM multi-utilisateurs avec optimisation continue**

- **Alignement**: AE - Principe d'apprentissage et d'adaptation
- **Justification**: Améliore la qualité des réponses et la personnalisation **par utilisateur**
- **Impact**: Performance, expérience utilisateur, données, **isolation des contextes**

**Décision 4: Intégration multi-APIs avec gestion d'erreurs et OAuth**

- **Alignement**: AE - Principe de résilience et de robustesse
- **Justification**: Assure la fiabilité du service malgré les pannes tierces **avec authentification OAuth**
- **Impact**: Disponibilité, expérience utilisateur, opérations, **gestion des sessions OAuth**

**Décision 5: LLM Gemini multi-utilisateurs avec prompts optimisés TDAH**

- **Alignement**: AE - Principe d'innovation technologique
- **Justification**: Fournit des capacités d'IA de pointe spécialisées **avec contexte utilisateur isolé**
- **Impact**: Qualité des réponses, différenciation, coûts, **personnalisation par utilisateur**

**Décision 6: Stratégie de numéro Twilio unique avec identification utilisateur**

- **Alignement**: AE - Principe de simplicité et de coût-efficacité
- **Justification**: Utilise les limites de taux élevées de Twilio pour supporter 1000+ utilisateurs
- **Impact**: Coûts, complexité opérationnelle, **scalabilité SMS**

#### **1.2.4.2 Ébauche de la checklist de sécurité**

**Authentification et autorisation multi-utilisateurs**:

- [ ] Système d'authentification multi-facteurs **par utilisateur**
- [ ] Gestion des sessions sécurisées **avec isolation utilisateur**
- [ ] Contrôle d'accès basé sur les rôles (RBAC) **par utilisateur**
- [ ] **Isolation stricte des données par utilisateur**
- [ ] **Gestion OAuth progressive par service et par utilisateur**

**Protection des données multi-utilisateurs**:

- [ ] Chiffrement des données en transit (TLS 1.3)
- [ ] Chiffrement des données au repos (AES-256) **avec isolation utilisateur**
- [ ] Gestion sécurisée des clés cryptographiques **par utilisateur**
- [ ] Classification et étiquetage des données **avec isolation utilisateur**
- [ ] **Isolation stricte des tokens OAuth par utilisateur**

**Sécurité des APIs multi-utilisateurs**:

- [ ] Validation des entrées et sorties **avec contexte utilisateur**
- [ ] Limitation des taux d'utilisation **par utilisateur**
- [ ] Monitoring des appels API suspects **par utilisateur**
- [ ] **Gestion sécurisée des tokens OAuth par utilisateur**
- [ ] **Isolation des appels API par utilisateur**

**Conformité et gouvernance multi-utilisateurs**:

- [ ] Audit trail complet des actions **par utilisateur**
- [ ] Politique de rétention des données **par utilisateur**
- [ ] Conformité aux réglementations locales **avec isolation utilisateur**
- [ ] Tests de sécurité automatisés **multi-utilisateurs**
- [ ] **Gestion des consentements OAuth par utilisateur et par service**

**Monitoring et détection multi-utilisateurs**:

- [ ] Surveillance continue de la sécurité **par utilisateur**
- [ ] Détection des anomalies comportementales **par utilisateur**
- [ ] Alertes en temps réel **avec contexte utilisateur**
- [ ] Plan de réponse aux incidents **multi-utilisateurs**
- [ ] **Isolation des alertes et incidents par utilisateur**

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
    subgraph "👥 Acteurs Multi-Utilisateurs"
        USER1[👤 Utilisateur TDAH 1]
        USER2[👤 Utilisateur TDAH 2]
        USER3[👤 Utilisateur TDAH 3]
        SYSTEM[🤖 Système Assistant<br/>Agent Core + Runner + Planner<br/>Multi-utilisateurs]
        EXTERNAL_APIS[🔌 APIs Externes<br/>OAuth par utilisateur]
    end

    subgraph "🛠️ Services applicatifs Multi-Utilisateurs"
        AUTH_SERVICE[🔐 Service d'authentification<br/>Multi-utilisateurs + MFA]
        USER_SERVICE[👤 Service de gestion utilisateur<br/>Isolation stricte des données]
        CONVERSATION_SERVICE[💬 Service de conversation<br/>Contexte utilisateur isolé]
        MEMORY_SERVICE[🧠 Service de mémoire LTM<br/>Isolation par utilisateur]
        INTEGRATION_SERVICE[🔗 Service d'intégration<br/>OAuth progressif par service]
        PLANNING_SERVICE[📅 Service de planification<br/>Données utilisateur isolées]
        NOTIFICATION_SERVICE[🔔 Service de notifications<br/>SMS + Web + Push]
        RAG_SERVICE[🔍 Service RAG<br/>Recherche sémantique par utilisateur]
        TOOL_SERVICE[🛠️ Service d'outils<br/>Registry des outils + OAuth]
        API_SERVICE[🚀 Service d'API REST<br/>FastAPI Backend Multi-utilisateurs]
        WEBHOOK_SERVICE[📡 Service de webhooks<br/>Twilio SMS + Identification utilisateur]
        OAUTH_MANAGER[🔑 Gestionnaire OAuth<br/>Progressive + Granular]
    end

    subgraph "🔄 Flux Multi-Interfaces"
        SMS_INTERFACE[📱 Interface SMS<br/>Numéro unique + Identification]
        WEB_INTERFACE[🌐 Interface Web<br/>Dashboard + OAuth Setup]
        SYNC_SERVICE[🔄 Service de synchronisation<br/>Cross-platform en temps réel]
    end

    %% ===== FLUX PRINCIPAL : Multi-utilisateurs avec OAuth =====
    USER1 --> AUTH_SERVICE
    USER2 --> AUTH_SERVICE
    USER3 --> AUTH_SERVICE

    AUTH_SERVICE --> OAUTH_MANAGER
    OAUTH_MANAGER --> INTEGRATION_SERVICE

    %% ===== FLUX OAuth Progressif =====
    INTEGRATION_SERVICE --> EXTERNAL_APIS
    EXTERNAL_APIS --> TOOL_SERVICE

    %% ===== FLUX CONVERSATION avec Isolation =====
    USER1 --> SMS_INTERFACE
    USER2 --> WEB_INTERFACE
    USER3 --> SMS_INTERFACE

    SMS_INTERFACE --> WEBHOOK_SERVICE
    WEB_INTERFACE --> API_SERVICE

    WEBHOOK_SERVICE --> CONVERSATION_SERVICE
    API_SERVICE --> CONVERSATION_SERVICE

    %% ===== SYSTÈME ASSISTANT ORCHESTRE TOUS LES SERVICES =====
    CONVERSATION_SERVICE --> SYSTEM
    SYSTEM --> MEMORY_SERVICE
    SYSTEM --> RAG_SERVICE
    SYSTEM --> TOOL_SERVICE
    SYSTEM --> PLANNING_SERVICE

    %% ===== SERVICES COMMUNIQUENT ENTRE EUX =====
    TOOL_SERVICE --> INTEGRATION_SERVICE
    INTEGRATION_SERVICE --> EXTERNAL_APIS

    %% ===== NOTIFICATIONS RETOURNENT À L'UTILISATEUR =====
    PLANNING_SERVICE --> NOTIFICATION_SERVICE
    NOTIFICATION_SERVICE --> USER1
    NOTIFICATION_SERVICE --> USER2
    NOTIFICATION_SERVICE --> USER3

    %% ===== SYNCHRONISATION CROSS-PLATFORM =====
    CONVERSATION_SERVICE --> SYNC_SERVICE
    MEMORY_SERVICE --> SYNC_SERVICE
    SYNC_SERVICE --> SMS_INTERFACE
    SYNC_SERVICE --> WEB_INTERFACE

    %% ===== AUTHENTIFICATION POUR TOUS LES SERVICES =====
    AUTH_SERVICE --> SYSTEM
    AUTH_SERVICE --> MEMORY_SERVICE
    AUTH_SERVICE --> PLANNING_SERVICE

    %% ===== STYLE ET COULEURS =====
    classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef systemClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:1px
    classDef flowClass fill:#fff3e0,stroke:#e65100,stroke-width:1px
    classDef oauthClass fill:#ffebee,stroke:#c62828,stroke-width:2px

    class USER1,USER2,USER3 userClass
    class SYSTEM systemClass
    class CONVERSATION_SERVICE,API_SERVICE,WEBHOOK_SERVICE,MEMORY_SERVICE,RAG_SERVICE,TOOL_SERVICE,PLANNING_SERVICE,NOTIFICATION_SERVICE,INTEGRATION_SERVICE,AUTH_SERVICE,USER_SERVICE serviceClass
    class EXTERNAL_APIS,OAUTH_MANAGER oauthClass
    class SMS_INTERFACE,WEB_INTERFACE,SYNC_SERVICE flowClass
```

**Explication des cas d'utilisation applicatifs**:

Les services applicatifs sont conçus pour supporter chaque étape du processus d'affaires, avec une **architecture modulaire centrée sur le Système Assistant multi-utilisateurs** qui orchestre tout le flux :

### **🔄 Communication multi-utilisateurs avec OAuth progressif :**

#### **1. Interface SMS (Principale) - Multi-utilisateurs :**

- **USER1/USER2/USER3 ↔ SMS_INTERFACE ↔ WEBHOOK_SERVICE ↔ SYSTEM** : Communication bidirectionnelle via SMS
- **Identification utilisateur** : Via numéro de téléphone ou code SMS
- **Isolation des données** : Chaque utilisateur accède uniquement à ses propres données
- **Synchronisation cross-platform** : Données SMS synchronisées avec le dashboard web

#### **2. Interface Web (Secondaire) - OAuth Setup :**

- **USER1/USER2/USER3 ↔ WEB_INTERFACE ↔ API_SERVICE ↔ SYSTEM** : Communication bidirectionnelle via API
- **Configuration OAuth** : Chaque utilisateur connecte ses propres comptes de services
- **Activation granulaire** : Fonctionnalités débloquées selon les services connectés
- **Dashboard personnalisé** : Interface adaptée aux services activés par l'utilisateur

#### **3. Synchronisation Cross-Platform :**

- **SYNC_SERVICE** : Synchronisation en temps réel entre SMS et web
- **Contexte unifié** : Mémoire LTM et contexte partagés entre interfaces
- **Données cohérentes** : Modifications via SMS reflétées immédiatement sur le web

### **🧠 Flux principal orchestré par le Système Assistant Multi-utilisateurs :**

1. **Authentification** : **USER1/USER2/USER3 → AUTH_SERVICE → OAUTH_MANAGER**
2. **Intégration OAuth** : **OAUTH_MANAGER → INTEGRATION_SERVICE → EXTERNAL_APIS**
3. **Conversation** : **Interface (SMS/Web) → CONVERSATION_SERVICE → SYSTEM**
4. **Contexte utilisateur** : **SYSTEM → MEMORY_SERVICE** (récupération du contexte isolé)
5. **Recherche sémantique** : **SYSTEM → RAG_SERVICE** (recherche dans les données utilisateur)
6. **Exécution d'outils** : **SYSTEM → TOOL_SERVICE** (outils activés via OAuth)
7. **Planification** : **SYSTEM → PLANNING_SERVICE** (données utilisateur isolées)
8. **Notifications** : **PLANNING_SERVICE → NOTIFICATION_SERVICE → Utilisateur spécifique**
9. **Synchronisation** : **SYNC_SERVICE** maintient la cohérence cross-platform

### **🎯 Interfaces utilisateur multiples (Architecture hybride multi-utilisateurs) :**

#### **Interface SMS (Principale) - ✅ Implémentée avec support multi-utilisateurs :**

- **Communication bidirectionnelle** : Messages entrent et réponses sortent **avec identification utilisateur**
- **Intégration directe** : Connexion directe au Système Assistant **multi-utilisateurs**
- **Identification utilisateur** : Via numéro de téléphone ou code SMS
- **Isolation des données** : Chaque utilisateur accède uniquement à ses propres données
- **Utilisation** : Interface principale pour tous les utilisateurs, **sans internet requis**

#### **Interface Web (Secondaire) - 🔄 Planifiée Phase 2 avec OAuth :**

- **Service d'API REST** : Backend FastAPI avec **support multi-utilisateurs**
- **Configuration OAuth** : Chaque utilisateur connecte ses propres comptes de services
- **Activation granulaire** : Fonctionnalités débloquées selon les services connectés
- **Communication bidirectionnelle** : Requêtes HTTP → Traitement → Réponses HTTP
- **Statut actuel** : API basique, **endpoints multi-utilisateurs en développement**
- **Évolution prévue** : Interface web complète avec **OAuth progressif et activation granulaire**

#### **Interface CLI (Basique) - ✅ Implémentée pour administration :**

- **Commandes système** : Status, traitement de messages, **gestion multi-utilisateurs**
- **Gestion administrative** : Commandes de base pour la maintenance
- **Communication bidirectionnelle** : Commandes entrent, résultats sortent
- **Utilisation** : Administration système et **gestion des utilisateurs**

#### **Interface API (Partielle) - 🔄 En développement multi-utilisateurs :**

- **Service d'API REST** : Backend FastAPI avec **endpoints multi-utilisateurs**
- **Webhooks Twilio** : Gestion des SMS entrants et sortants **avec identification utilisateur**
- **Communication bidirectionnelle** : Requêtes HTTP → Traitement → Réponses HTTP
- **Statut actuel** : API basique, **endpoints utilisateurs multi-utilisateurs en développement**
- **Évolution prévue** : **Interface web complète avec OAuth progressif et activation granulaire**

### **🌟 Rôle central du Système Assistant Multi-utilisateurs :**

- **Orchestrateur principal** : Coordonne tous les services **avec isolation utilisateur**
- **Gestionnaire de contexte** : Maintient l'état de la conversation **par utilisateur**
- **Décideur d'actions** : Utilise le LLM pour choisir les actions **avec contexte utilisateur**
- **Exécuteur d'outils** : Lance les outils appropriés **activés via OAuth**
- **Gestionnaire de mémoire** : Sauvegarde et récupère le contexte **par utilisateur**
- **Point d'unification** : Toutes les interfaces convergent vers lui **avec isolation des données**
- **Générateur de réponses** : Crée les réponses qui retournent à l'utilisateur **spécifique**
- **Gestionnaire OAuth** : **Gère les intégrations progressives par utilisateur et par service**

### **💡 Avantages de l'architecture hybride multi-utilisateurs :**

1. **SMS comme interface principale** : Simplicité, accessibilité, **pas d'internet requis, support multi-utilisateurs**
2. **Web pour la configuration OAuth** : **Setup des intégrations et activation granulaire des fonctionnalités**
3. **API pour l'extensibilité** : **Intégrations futures et interface web multi-utilisateurs**
4. **Unification par le Système Assistant** : **Cohérence des réponses et du contexte par utilisateur**
5. **Communication complète** : Chaque interface supporte l'envoi ET la réception **avec isolation utilisateur**
6. **Flexibilité maximale** : L'utilisateur peut choisir l'interface qui lui convient **et activer les fonctionnalités souhaitées**
7. **Scalabilité** : **Support de 1000+ utilisateurs simultanés avec isolation stricte des données**
8. **OAuth progressif** : **Chaque utilisateur connecte ses propres comptes selon ses besoins**

**Description des impacts des cas d'utilisation applicatifs**

| Acteur                   | Impacts                                                                                                                                                                                                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Utilisateur TDAH**     | **Interface adaptée multi-utilisateurs**, **notifications contextuelles personnalisées**, **support personnalisé avec OAuth**, **communication bidirectionnelle complète avec isolation des données**                                                           |
| **Système Assistant**    | **Gestion de la mémoire multi-utilisateurs**, **apprentissage continu par utilisateur**, **optimisation des réponses avec contexte utilisateur isolé**, **orchestration de tous les services avec isolation stricte**                                           |
| **APIs Externes**        | **Intégration sécurisée via OAuth par utilisateur**, **gestion des erreurs avec contexte utilisateur**, **fallback gracieux avec isolation des données**                                                                                                        |
| **Interfaces multiples** | **Flexibilité d'accès multi-utilisateurs**, **simplicité SMS avec identification utilisateur**, **extensibilité API avec OAuth progressif**, **maintenance CLI avec gestion multi-utilisateurs**, **communication bidirectionnelle avec isolation des données** |
| **Système OAuth**        | **Authentification progressive par service**, **activation granulaire des fonctionnalités**, **gestion des consentements par utilisateur**, **isolation stricte des tokens et données**                                                                         |
| **Synchronisation**      | **Synchronisation cross-platform en temps réel**, **cohérence des données entre SMS et web**, **contexte utilisateur unifié avec isolation stricte**                                                                                                            |

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
  - Authentification : **Clé API (gérée par l'organisation)**
  - Limites : Quotas par token, coûts par requête
  - Utilisation : Génération de réponses, analyse de contexte **multi-utilisateurs**

- **YouTube Data API v3** : Métadonnées et informations vidéo

  - Endpoint : `https://www.googleapis.com/youtube/v3/`
  - Authentification : **OAuth 2.0 par utilisateur**
  - Limites : **Quotas par utilisateur OAuth**, 10,000 requêtes/jour par utilisateur
  - Utilisation : Extraction d'informations vidéo, recherche de contenu **avec contexte utilisateur**

- **YouTube Transcript API** : Transcriptions vidéo
  - Endpoint : Service tiers non officiel
  - Authentification : Aucune (service public)
  - Limites : Rate limiting, disponibilité variable
  - Utilisation : Récupération de transcriptions pour analyse **par utilisateur**

**Microsoft Services**:

- **Microsoft Graph API** : Calendrier, emails et authentification

  - Endpoint : `https://graph.microsoft.com/v1.0/`
  - Authentification : **OAuth 2.0 avec MSAL par utilisateur**
  - Scopes : Calendars.ReadWrite, Mail.ReadWrite, User.Read
  - Utilisation : Gestion calendrier, emails, profil utilisateur **avec isolation stricte des données**

- **MSAL (Microsoft Authentication Library)** : Authentification OAuth
  - Endpoint : `https://login.microsoftonline.com/consumers/`
  - Authentification : **OAuth 2.0 avec refresh tokens par utilisateur**
  - Stockage : **Fichier local refresh_token.txt par utilisateur**
  - Utilisation : Gestion des sessions Microsoft **avec isolation utilisateur**

**Services de communication**:

- **Twilio API** : **SMS et communications avec numéro unique et identification utilisateur**
  - Endpoint : `https://api.twilio.com/`
  - Authentification : Account SID + Auth Token (gérés par l'organisation)
  - Limites : **Quotas par compte, coûts par SMS, limites de taux élevées (1000+ utilisateurs)**
  - Utilisation : **Notifications, rappels, communications avec identification utilisateur**

**Services de productivité**:

- **Notion API** : Gestion des notes et pages
  - Endpoint : `https://api.notion.com/v1/`
  - Authentification : **Token d'intégration OAuth par utilisateur**
  - Limites : **Rate limiting par utilisateur, quotas par workspace utilisateur**
  - Utilisation : Création de notes, gestion des pages, liens bidirectionnels **avec isolation des données**

**Services de recherche**:

- **DuckDuckGo Search API** : Recherche web et actualités
  - Endpoint : Service public via bibliothèque Python
  - Authentification : Aucune
  - Limites : Rate limiting, pas de quotas officiels
  - Utilisation : Recherche web, actualités, images **avec contexte utilisateur**

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
