# Projet: Vérificateur d'avis Google Maps

## Vue d'ensemble
Application Streamlit permettant d'organiser et de faciliter la vérification manuelle d'avis Google Maps à partir de fichiers Excel.

## Date de création
18 novembre 2025

## Objectif du projet
Créer un outil de vérification mensuelle permettant de:
1. Uploader un fichier Excel avec des liens GMB (Google My Business) et Review Links
2. Rechercher des listings spécifiques (fonction similaire à Ctrl+F)
3. Afficher tous les liens de manière cliquable
4. Permettre la vérification manuelle avec marquage ✅/❌
5. Exporter les résultats avec les statuts enregistrés

## Architecture du projet

### Structure des fichiers
```
/
├── app.py                    # Application Streamlit principale
├── attached_assets/          # Dossier contenant les fichiers téléchargés
│   └── France Agency_*.xlsx  # Fichier Excel exemple
├── README.md                 # Documentation utilisateur
└── replit.md                 # Documentation projet (ce fichier)
```

### Dépendances Python
- streamlit: Interface web avec éditeur de données interactif
- pandas: Manipulation de données Excel
- openpyxl: Lecture/écriture Excel

### Configuration Streamlit
- Port: 5000 (requis par Replit)
- Adresse: 0.0.0.0 (accessible depuis l'extérieur)
- Mode headless: activé

## Fonctionnalités implémentées

### 1. Upload de fichiers
- Support des formats .xlsx et .xls
- Validation des colonnes requises
- Affichage des informations du fichier

### 2. Recherche de GMB listings
- Méthode 1: Sélection dans une liste déroulante
- Méthode 2: Recherche par texte (style Ctrl+F)
- Filtrage dynamique des résultats

### 3. Affichage des données
- Tableau interactif avec `st.data_editor`
- Liens cliquables pour Review Links et GMB listings
- Colonne "Statut" éditable pour marquer ✅/❌/⚪

### 4. Vérification manuelle
- Clic sur lien → Ouverture dans navigateur
- Vérification visuelle par l'utilisateur
- Marquage manuel du statut dans le tableau

### 5. Statistiques en temps réel
- Total d'avis
- Nombre d'avis présents (✅)
- Nombre d'avis supprimés (❌)
- Nombre d'avis à vérifier (⚪)

### 6. Export de données
- Téléchargement Excel avec statuts
- Nom de fichier avec timestamp
- Conservation de toutes les données originales + colonne Statut

## Décisions techniques

### Approche choisie: Vérification manuelle
Après analyse des contraintes:
- **Rejet de la vérification automatique HTTP**: Google Maps utilise JavaScript pour charger le contenu, les requêtes HTTP simples ne peuvent pas détecter fiablement les avis supprimés
- **Rejet de Playwright/Selenium**: Nécessite des dépendances système (sudo) non disponibles sur Replit
- **Rejet de Browserless.io**: Service externe nécessitant une clé API, ajoutant de la complexité

**Solution retenue**: Outil d'aide à la vérification manuelle
- ✅ 100% fiable (vérification humaine)
- ✅ Pas de blocage Google
- ✅ Pas de dépendances externes
- ✅ Gratuit
- ✅ Simple à utiliser

### Utilisation de st.data_editor
- Permet l'édition directe dans le tableau
- Configuration des colonnes avec LinkColumn pour liens cliquables
- TextColumn éditable pour la colonne Statut
- Interface intuitive sans JavaScript custom

## Structure du fichier Excel attendu

Colonnes requises:
- `GMB listings link`: URL de la page Google Maps Business
- `Review Links`: URL de l'avis spécifique

Colonnes optionnelles (pour affichage):
- `GMB listings Name`: Nom du business
- `Name`: Auteur de l'avis
- `Date`: Date de l'avis
- `Content`: Contenu de l'avis
- `Quantity`: Note en étoiles
- `Number`: Numéro de l'avis

## Workflow Replit
Nom: "Streamlit App"
Commande: `streamlit run app.py --server.port=5000 --server.address=0.0.0.0 --server.headless=true`
Type de sortie: webview
Port: 5000

## Workflow utilisateur recommandé

### Check mensuel
1. Télécharger le fichier Excel du mois dernier (ou créer nouveau)
2. Sélectionner un GMB listing à vérifier
3. Cliquer sur chaque Review Link pour ouvrir dans navigateur
4. Vérifier visuellement si message "Cet avis n'est plus disponible"
5. Marquer ✅ (présent) ou ❌ (supprimé) dans la colonne Statut
6. Télécharger le fichier Excel mis à jour
7. Répéter pour autres GMB listings
8. Conserver l'historique mois par mois

## Préférences utilisateur
- Langue: Français
- Interface: Simple et intuitive
- Recherche: Similaire à Ctrl+F pour facilité d'utilisation
- Approche: Manuelle et fiable plutôt qu'automatique et incertaine
- Affichage: Liens regroupés avec possibilité de marquer check/croix

## Historique des versions

### Version 1.0 (18 novembre 2025)
- Vérification manuelle avec tableau interactif
- Recherche par GMB listing (liste ou texte)
- Liens cliquables
- Export Excel avec statuts
- Statistiques en temps réel
