# Vérificateur d'avis Google Maps

Application Streamlit pour organiser et vérifier manuellement si les avis Google Maps sont toujours présents.

## Fonctionnalités

- **Upload de fichiers Excel**: Téléchargez vos fichiers Excel contenant les liens GMB et les avis
- **Recherche avancée**: Recherchez par GMB listing (sélection ou texte libre style Ctrl+F)
- **Liens cliquables**: Tous les liens Review Links et GMB listings sont cliquables
- **Vérification manuelle facilitée**: Marquez manuellement les avis comme ✅ (présent) ou ❌ (supprimé)
- **Statistiques en temps réel**: Voir combien d'avis sont présents, supprimés ou à vérifier
- **Export Excel**: Téléchargez les résultats avec vos vérifications enregistrées

## Structure du fichier Excel requis

Votre fichier Excel doit contenir au minimum les colonnes suivantes:

- `GMB listings link`: Lien vers la page Google Maps Business
- `Review Links`: Liens vers les avis individuels

Colonnes optionnelles (pour affichage):
- `GMB listings Name`: Nom du listing
- `Name`: Nom de l'auteur de l'avis
- `Date`: Date de l'avis
- `Content`: Contenu de l'avis

## Comment utiliser

1. **Démarrez l'application** (elle s'exécute automatiquement sur Replit)
2. **Téléchargez votre fichier Excel**
3. **Sélectionnez un GMB listing** spécifique ou recherchez par texte
4. **Vérifiez les avis manuellement**:
   - Cliquez sur chaque lien "Review Links" pour l'ouvrir dans votre navigateur
   - Vérifiez si le message "Cet avis n'est plus disponible" apparaît
5. **Marquez le statut** en double-cliquant sur la cellule "Statut":
   - Tapez `✅` si l'avis est présent
   - Tapez `❌` si l'avis est supprimé
   - Laissez `⚪` si vous n'avez pas encore vérifié
6. **Téléchargez vos résultats** en cliquant sur "Télécharger les résultats (Excel)"

## Workflow recommandé pour check mensuel

1. 📁 Téléchargez votre fichier Excel du mois dernier
2. 🔍 Sélectionnez le premier GMB listing à vérifier
3. 🖱️ Cliquez sur chaque lien "Review Links" pour vérifier les avis
4. ✍️ Marquez ✅ ou ❌ selon ce que vous voyez
5. 💾 Téléchargez le fichier Excel mis à jour
6. 🔁 Répétez pour les autres GMB listings le mois prochain

## Raccourcis clavier utiles

- **Double-clic** sur une cellule pour modifier
- **Tab** pour passer à la cellule suivante
- **Entrée** pour valider et passer à la ligne suivante
- **Ctrl+C / Ctrl+V** pour copier/coller

## Technologies utilisées

- **Streamlit**: Framework d'application web avec éditeur de données interactif
- **Pandas**: Manipulation de données Excel
- **OpenPyXL**: Lecture/écriture de fichiers Excel

## Déploiement

Cette application est configurée pour fonctionner sur Replit avec le workflow suivant:
```bash
streamlit run app.py --server.port=5000 --server.address=0.0.0.0 --server.headless=true
```

## Avantages de cette approche

✅ **Fiable à 100%** - Vous vérifiez vous-même avec vos yeux

✅ **Pas de blocage Google** - Vous utilisez votre navigateur normalement

✅ **Flexible** - Vous pouvez prendre des notes supplémentaires

✅ **Simple** - Pas besoin d'API ou de services externes

✅ **Gratuit** - Aucun frais de service tiers
