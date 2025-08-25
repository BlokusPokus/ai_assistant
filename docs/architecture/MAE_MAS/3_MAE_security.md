# 3. Sécurité

## 3.1 Risques et conformité

### 3.1.1 Requis de conformité

**Tableau 3.1.1 - Exigences de conformité et réglementations**

| Réglementation/Standard | Applicabilité     | Exigences clés                                                                                                                                                        | Statut de conformité         |
| ----------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| **GDPR (UE)**           | ✅ Obligatoire    | • Consentement explicite<br>• Droit à l'oubli<br>• Portabilité des données<br>• Notification des violations<br>• **Isolation stricte des données multi-utilisateurs** | 🔄 En cours d'implémentation |
| **CCPA (Californie)**   | ✅ Obligatoire    | • Transparence des données<br>• Droit de suppression<br>• Non-discrimination<br>• **Isolation des données par utilisateur**                                           | 🔄 En cours d'implémentation |
| **PIPEDA (Canada)**     | ✅ Obligatoire    | • Consentement<br>• Limitation de la collecte<br>• Accès et correction<br>• **Séparation des données utilisateur**                                                    | 🔄 En cours d'implémentation |
| **SOC 2 Type II**       | 🎯 Cible 2025     | • Sécurité<br>• Disponibilité<br>• Traitement<br>• Confidentialité<br>• Intégrité<br>• **Gestion multi-utilisateurs**                                                 | ❌ Non implémenté            |
| **ISO 27001**           | 🎯 Cible 2026     | • Système de gestion de la sécurité<br>• Contrôles de sécurité<br>• Évaluation des risques<br>• **Isolation des données**                                             | ❌ Non implémenté            |
| **HIPAA**               | ❌ Non applicable | • Pas de données médicales sensibles<br>• Assistant de productivité uniquement<br>• **Données utilisateur isolées**                                                   | ✅ Conforme par design       |

**Exigences de conformité détaillées:**

#### **GDPR (Règlement Général sur la Protection des Données)**

- **Article 5 - Principes de traitement**: Licéité, loyauté, transparence, limitation des finalités, minimisation des données, exactitude, limitation de la conservation, intégrité et confidentialité
- **Article 6 - Base légale**: Consentement explicite de l'utilisateur pour le traitement des données **et pour chaque intégration OAuth**
- **Article 17 - Droit à l'oubli**: Suppression complète des données utilisateur sur demande **avec isolation stricte multi-utilisateurs**
- **Article 20 - Portabilité**: Export des données dans un format structuré et lisible par machine **par utilisateur isolé**
- **Article 25 - Protection des données dès la conception**: **Isolation stricte des données par utilisateur dès la conception**
- **Article 32 - Sécurité**: Chiffrement des données, authentification forte, audit trail, **isolation stricte des données multi-utilisateurs**

#### **CCPA (California Consumer Privacy Act)**

- **Section 1798.100**: Droit de savoir quelles données personnelles sont collectées **par utilisateur isolé**
- **Section 1798.105**: Droit de suppression des données personnelles **avec isolation stricte des données**
- **Section 1798.110**: Droit de connaître les catégories de données collectées **par utilisateur**
- **Section 1798.115**: Droit de connaître les catégories de données vendues **par utilisateur**
- **Section 1798.125**: Non-discrimination pour l'exercice des droits **avec isolation des données multi-utilisateurs**

### 3.1.2 Mitigation des risques de sécurité identifiés

**Tableau 3.1.2 - Analyse des risques de sécurité et mitigation**

| Risque                                  | Probabilité | Impact     | Niveau de risque | Mesures de mitigation                                                                                                                                    | Responsable  |
| --------------------------------------- | ----------- | ---------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| **Violation de données utilisateur**    | Moyenne     | Très élevé | **Élevé**        | • Chiffrement AES-256<br>• **Isolation stricte des données multi-utilisateurs**<br>• Audit trail complet<br>• Tests de pénétration                       | CISO         |
| **Attaque par injection SQL**           | Faible      | Élevé      | **Moyen**        | • Requêtes préparées<br>• Validation des entrées<br>• WAF avec règles OWASP<br>• Tests automatisés                                                       | Développeurs |
| **Exposition des clés API**             | Moyenne     | Élevé      | **Moyen**        | • Gestion des secrets Docker<br>• Rotation automatique<br>• Accès restreint<br>• Monitoring des accès                                                    | DevOps       |
| **Exposition des tokens OAuth**         | Moyenne     | Élevé      | **Moyen**        | • **Chiffrement des tokens OAuth par utilisateur**<br>• **Isolation stricte des tokens**<br>• Rotation automatique<br>• Audit des accès OAuth            | Développeurs |
| **Attaque par déni de service**         | Moyenne     | Moyen      | **Moyen**        | • Rate limiting Nginx<br>• Protection DDoS<br>• Monitoring des ressources<br>• Auto-scaling                                                              | DevOps       |
| **Violation de l'authentification**     | Faible      | Très élevé | **Moyen**        | • MFA optionnel<br>• Sessions sécurisées<br>• Gestion des tokens JWT<br>• Détection d'anomalies                                                          | Développeurs |
| **Exposition des données LTM**          | Faible      | Élevé      | **Moyen**        | • Chiffrement au repos<br>• **Isolation stricte par utilisateur**<br>• Audit des accès<br>• Tests de sécurité                                            | Développeurs |
| **Fuite de données entre utilisateurs** | Faible      | Très élevé | **Moyen**        | • **Isolation stricte des données par utilisateur**<br>• **Validation des accès multi-utilisateurs**<br>• Tests d'isolation<br>• Audit des accès croisés | CISO         |

**Stratégie de mitigation globale:**

1. **Prévention**: Implémentation de contrôles de sécurité robustes
2. **Détection**: Monitoring continu et détection d'anomalies
3. **Réponse**: Procédures d'incident et plans de reprise
4. **Récupération**: Sauvegardes sécurisées et plans de restauration

## 3.2 Classification et gestion des données informationnelles

### 3.2.1 Classification et catégorisation des données

**Tableau 3.2.1 - Classification des données par niveau de sensibilité**

| Niveau de sensibilité    | Description                                       | Exemples de données                                                                                                       | Contrôles de sécurité requis                                                                                    | Rétention                   |
| ------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | --------------------------- |
| **Données publiques**    | Informations non sensibles                        | • Documentation produit<br>• Guides utilisateur<br>• Informations marketing                                               | • Validation des entrées<br>• Protection contre le spam                                                         | Illimitée                   |
| **Données internes**     | Informations de l'organisation                    | • Métriques de performance<br>• Logs système<br>• Configuration                                                           | • Accès authentifié<br>• Audit des accès                                                                        | 2 ans                       |
| **Données personnelles** | Informations identifiant l'utilisateur            | • Nom, email, profil<br>• Préférences utilisateur<br>• Historique des interactions<br>• **Numéros de téléphone SMS**      | • Chiffrement en transit et au repos<br>• **Isolation stricte multi-utilisateurs**<br>• Consentement explicite  | Selon demande utilisateur   |
| **Données sensibles**    | Informations nécessitant une protection renforcée | • **Tokens OAuth par utilisateur**<br>• **Refresh tokens OAuth**<br>• Clés de chiffrement<br>• Données d'authentification | • Chiffrement AES-256<br>• **Isolation stricte par utilisateur**<br>• Accès restreint<br>• Rotation automatique | Selon politique de sécurité |
| **Données critiques**    | Informations essentielles au fonctionnement       | • Configuration système<br>• Clés de chiffrement maîtres<br>• Sauvegardes système                                         | • Chiffrement maximum<br>• Accès privilégié<br>• Sauvegarde sécurisée                                           | Permanente                  |

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

- **Tokens d'accès**: **Tokens OAuth par utilisateur et par service**, refresh tokens, clés API
- **Configuration**: Paramètres de connexion OAuth, endpoints, scopes autorisés
- **Métadonnées**: Statut de synchronisation, dernière mise à jour, **activation granulaire des fonctionnalités**
- **Consentements OAuth**: **Gestion des consentements par utilisateur et par service**, révocations

#### **Données système (Infrastructure)**

- **Logs**: Journaux d'audit, logs d'erreur, métriques
- **Configuration**: Variables d'environnement, paramètres
- **Monitoring**: Métriques de performance, alertes

### 3.2.2 Gestion des mécanismes et cycle de vie des données

**Tableau 3.2.2 - Cycle de vie des données et mécanismes de gestion**

| Phase du cycle de vie | Mécanismes de gestion                                                                                                                          | Contrôles de sécurité                                                                                                                        | Rétention             | Disposition                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------ |
| **Collecte**          | • Consentement explicite<br>• Minimisation des données<br>• Validation des entrées<br>• **Consentement OAuth par service**                     | • Chiffrement en transit (TLS 1.3)<br>• Validation des sources<br>• Audit de la collecte<br>• **Validation des consentements OAuth**         | N/A                   | N/A                                                                                  |
| **Traitement**        | • **Isolation stricte par utilisateur**<br>• Chiffrement au repos<br>• Contrôle d'accès<br>• **Validation des tokens OAuth**                   | • Chiffrement AES-256<br>• **RBAC strict multi-utilisateurs**<br>• Audit des opérations<br>• **Isolation des contextes OAuth**               | Selon type de données | N/A                                                                                  |
| **Stockage**          | • Base de données chiffrée<br>• Sauvegardes sécurisées<br>• Réplication sécurisée<br>• **Isolation des tokens OAuth**                          | • Chiffrement au repos<br>• **Accès restreint par utilisateur**<br>• Monitoring continu<br>• **Validation des accès OAuth**                  | Selon politique       | N/A                                                                                  |
| **Partage**           | • **Isolation stricte multi-utilisateurs**<br>• Pas de partage inter-utilisateur<br>• Export contrôlé<br>• **Pas de partage des tokens OAuth** | • **Validation des destinataires par utilisateur**<br>• Chiffrement des exports<br>• Audit des partages<br>• **Isolation des données OAuth** | N/A                   | N/A                                                                                  |
| **Archivage**         | • Chiffrement des archives<br>• Accès restreint<br>• Rotation automatique                                                                      | • Chiffrement AES-256<br>• Contrôle d'accès<br>• Monitoring des accès                                                                        | Selon politique       | N/A                                                                                  |
| **Suppression**       | • Suppression sécurisée<br>• Audit de suppression<br>• Confirmation utilisateur                                                                | • Overwriting sécurisé<br>• Audit trail<br>• Validation de suppression                                                                       | N/A                   | • Suppression physique<br>• Overwriting des données<br>• Confirmation de destruction |

**Mécanismes de gestion spécifiques:**

#### **Gestion du consentement**

- **Interface de consentement**: Formulaire clair et compréhensible
- **Granularité**: Consentement par type de données et finalité
- **Révocation**: Possibilité de retirer le consentement à tout moment
- **Audit**: Traçabilité complète des consentements et révocations
- **Consentement OAuth**: **Consentement explicite par service OAuth et par utilisateur**
- **Activation granulaire**: **Activation des fonctionnalités selon les services OAuth connectés**
- **Révocation OAuth**: **Possibilité de révoquer l'accès à chaque service OAuth individuellement**

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

| Ressource                 | Rôle Standard              | Rôle Premium               | Rôle Administrateur          |
| ------------------------- | -------------------------- | -------------------------- | ---------------------------- |
| **Profil utilisateur**    | R/W (propre profil)        | R/W (propre profil)        | R/W (tous les profils)       |
| **Données LTM**           | R/W (propres données)      | R/W (propres données)      | R (toutes les données)       |
| **Objectifs et tâches**   | R/W (propres données)      | R/W (propres données)      | R (toutes les données)       |
| **Intégrations externes** | R/W (propres données)      | R/W (propres données)      | R (toutes les données)       |
| **Intégrations OAuth**    | R/W (propres intégrations) | R/W (propres intégrations) | R (toutes les intégrations)  |
| **Tokens OAuth**          | R (propres tokens)         | R (propres tokens)         | R (tous les tokens)          |
| **Métriques système**     | Aucun accès                | R (métriques utilisateur)  | R/W (toutes les métriques)   |
| **Logs système**          | Aucun accès                | Aucun accès                | R (tous les logs)            |
| **Configuration**         | Aucun accès                | Aucun accès                | R/W (toute la configuration) |

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

    # Politique: Accès aux fonctionnalités OAuth selon les services connectés
    if (resource.type == "oauth_feature" and
        resource.service not in user.connected_oauth_services):
        return False, "Fonctionnalité non disponible - service OAuth non connecté"

    # Politique: Validation des tokens OAuth pour les actions sensibles
    if (action.sensitivity == "high" and
        not user.has_valid_oauth_token(resource.service)):
        return False, "Token OAuth expiré ou invalide pour cette action"

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
# Configuration de protection DDoS et OAuth
http {
    # Limitation du nombre de connexions par IP
    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
    limit_conn conn_limit_per_ip 10;

    # Limitation du nombre de requêtes par IP
    limit_req_zone $binary_remote_addr zone=req_limit_per_ip:10m rate=10r/s;
    limit_req zone=req_limit_per_ip burst=20 nodelay;

    # Limitation spécifique pour les endpoints OAuth
    limit_req_zone $binary_remote_addr zone=oauth_limit_per_ip:10m rate=2r/s;
    limit_req zone=oauth_limit_per_ip burst=5 nodelay;

    # Blocage des User-Agents suspects
    if ($http_user_agent ~* (bot|crawler|spider|scraper)) {
        return 403;
    }

    # Blocage des méthodes HTTP dangereuses
    if ($request_method !~ ^(GET|POST|PUT|DELETE)$) {
        return 405;
    }

    # Protection contre les attaques OAuth
    if ($request_uri ~* "/oauth/.*callback") {
        limit_req zone=oauth_limit_per_ip burst=3 nodelay;
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
        elif event.type == 'oauth_token_exposure' and event.user_id != event.token_owner:
            self.send_alert('critical', 'Exposition de token OAuth non autorisée', event)
        elif event.type == 'oauth_integration_abuse' and event.rate > 50:
            self.send_alert('high', 'Utilisation abusive des intégrations OAuth', event)
        elif event.type == 'cross_user_data_access' and event.source_user != event.target_user:
            self.send_alert('critical', 'Tentative d\'accès croisé aux données utilisateur', event)
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
