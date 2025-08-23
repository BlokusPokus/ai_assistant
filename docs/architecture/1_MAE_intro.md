# 1. Introduction

## 1.1 Objective du livrable

Le modèle d'architecture d'exploitation permet de définir les changements à apporter aux plateformes d'infrastructure technologiques de la solution, de la conception à l'exploitation de celle-ci, **en supportant une architecture multi-utilisateurs avec authentification OAuth progressive**.

## 1.2 But du projet

**Objectif principal** : Transformer l'infrastructure technologique de l'assistant personnel TDAH d'un environnement de développement local vers une plateforme d'exploitation de production robuste et sécurisée, **supportant une architecture multi-utilisateurs avec authentification OAuth progressive**.

**Contexte** : L'assistant personnel TDAH nécessite une infrastructure d'exploitation de niveau entreprise pour supporter la production multi-utilisateurs, incluant la conteneurisation, la sécurité renforcée, l'observabilité et la haute disponibilité. **Chaque utilisateur doit pouvoir connecter ses propres comptes de services externes (Notion, Google, Microsoft, etc.) via OAuth, avec activation granulaire des fonctionnalités**.

**Solution** : Mise en place d'une architecture conteneurisée avec Docker, migration vers PostgreSQL, ajout de Redis, implémentation d'un proxy inverse sécurisé, **système d'authentification OAuth progressif par service**, **stratégie de numéro Twilio unique avec identification utilisateur**, et déploiement d'une stack de monitoring complète pour l'exploitation en production multi-utilisateurs.

## 1.3 Documents de référence

Fichier intrants de couts du project
Calculatrice des coûts pour les services du PaaS
**Documentation Twilio sur les limites de taux et files d'attente de messages**

## 1.4 Responsabilité de production du document

Conseiller en architecture de solutions d'exploitation
Analyste technologique d'exploitation
Expert d'architecture technologique
**Architecte d'authentification et d'intégration OAuth**
