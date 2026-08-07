# AI Agency

AI Agency est une application de prospection commerciale intelligente destinée aux petites entreprises locales.

Elle permet de rechercher une entreprise, analyser sa présence en ligne, identifier l'opportunité commerciale la plus pertinente et générer une proposition adaptée.

## Fonctionnalités

- Recherche d'entreprises locales
- Gestion des entreprises
- Audit automatique d'un site internet
- Score technique et commercial
- Détection automatique d'opportunités commerciales
- Génération d'emails commerciaux
- Proposition de création de site pour les entreprises sans site
- Contrôle qualité des emails
- Rapports PDF professionnels
- Historique des audits et scores
- Dashboard React
- API FastAPI
- Base PostgreSQL
- Intégration Ollama
- Tests automatisés

## Architecture

Le workflow principal suit cette logique :

```text
Entreprise
   |
   +-- Site existant
   |      |
   |      v
   |    Audit
   |      |
   |      v
   |    Score
   |      |
   |      v
   |    OpportunityAgent
   |      |
   |      v
   |    Writer spécialisé
   |
   +-- Aucun site
          |
          v
     OpportunityAgent
          |
          v
     Offre de création de site