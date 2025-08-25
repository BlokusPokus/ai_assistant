# 6. Infrastructure de transport (suite)

## 6.1 Sécurité réseau avancée

### 6.1.1 Microsegmentation

**Tableau 6.1.1 - Règles de microsegmentation**

| Source              | Destination         | Protocole | Port            | Justification                         |
| ------------------- | ------------------- | --------- | --------------- | ------------------------------------- |
| **Internet**        | **Load Balancer**   | TCP       | 80, 443         | Accès public aux services             |
| **Load Balancer**   | **Nginx Proxy**     | TCP       | 80, 443         | Routage des requêtes                  |
| **Nginx Proxy**     | **FastAPI Backend** | TCP       | 8000            | Communication API                     |
| **Nginx Proxy**     | **Agent Service**   | TCP       | 8001            | Communication Agent                   |
| **Nginx Proxy**     | **OAuth Manager**   | TCP       | 8002            | **Gestion des intégrations OAuth**    |
| **FastAPI Backend** | **PostgreSQL**      | TCP       | 5432            | Accès base de données                 |
| **FastAPI Backend** | **Redis**           | TCP       | 6379            | Accès cache                           |
| **FastAPI Backend** | **OAuth Manager**   | TCP       | 8002            | **Validation des intégrations OAuth** |
| **Agent Service**   | **PostgreSQL**      | TCP       | 5432            | Accès base de données                 |
| **Agent Service**   | **Redis**           | TCP       | 6379            | Accès cache                           |
| **Agent Service**   | **OAuth Manager**   | TCP       | 8002            | **Accès aux intégrations OAuth**      |
| **OAuth Manager**   | **PostgreSQL**      | TCP       | 5432            | **Stockage des tokens OAuth**         |
| **OAuth Manager**   | **Redis**           | TCP       | 6379            | **Cache des tokens OAuth**            |
| **OAuth Manager**   | **Internet**        | TCP       | 443             | **Appels vers APIs externes OAuth**   |
| **Monitoring**      | **Tous services**   | TCP       | Ports métriques | Collecte de métriques                 |

### 6.1.2 Pare-feu applicatif

#### **6.1.2.1 Règles de filtrage**

**Règles entrantes**:

- **HTTP/HTTPS**: Ports 80 et 443 uniquement
- **SSH**: Port 22 depuis IPs d'administration
- **Monitoring**: Ports spécifiques depuis zone monitoring

**Règles sortantes**:

- **APIs externes**: Accès aux services tiers requis
- **APIs OAuth externes**: **Accès aux fournisseurs OAuth (Google, Microsoft, Notion, YouTube)**
- **DNS**: Résolution DNS externe
- **NTP**: Synchronisation temporelle
- **Logs**: Envoi des logs de sécurité

#### **6.1.2.2 Protection avancée**

- **Intrusion Detection**: Détection des tentatives d'intrusion
- **Anomaly Detection**: Détection des comportements anormaux
- **OAuth Abuse Detection**: **Détection de l'utilisation abusive des intégrations OAuth**
- **Cross-User Access Detection**: **Détection des tentatives d'accès croisé aux données utilisateur**
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
- **OAuth Intégrations**: **Nombre d'intégrations OAuth actives par utilisateur**
- **OAuth API Calls**: **Volume d'appels vers les APIs OAuth externes**
- **OAuth Token Refresh**: **Fréquence de renouvellement des tokens OAuth**
- **Cross-User Access Attempts**: **Tentatives d'accès croisé aux données utilisateur**

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

#### **6.3.1.3 Attaques OAuth et multi-utilisateurs**

- **Compromission des tokens OAuth**: **Révocation immédiate et régénération des tokens**
- **Fuite de données multi-utilisateurs**: **Isolation immédiate et investigation forensique**
- **Abus des intégrations OAuth**: **Limitation des appels API et investigation utilisateur**
- **Tentatives d'accès croisé**: **Blocage des utilisateurs suspects et audit complet**

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
