# 📤 Guide de Push vers GitHub

## Méthode 1 : Interface VS Code (Recommandée)

### Étape 1 : Ouvrir la vue Source Control
1. Cliquez sur l'icône **Source Control** dans la barre latérale gauche (Ctrl+Shift+G)
2. Ou allez dans `View > Source Control`

### Étape 2 : Vérifier les changements
Vous devriez voir tous vos fichiers modifiés :
- ✅ `app_meteo.py` (design moderne)
- ✅ `.streamlit/config.toml` (thème)
- ✅ `README.md` (documentation)
- ✅ `entrainer_modele.ipynb` (modèle optimisé)

### Étape 3 : Stage les fichiers
1. Cliquez sur le **+** à côté de chaque fichier
2. Ou cliquez sur le **+** en haut pour tout stager

### Étape 4 : Commit
1. Tapez un message dans la zone de texte en haut :
   ```
   ✨ Design moderne 2026 + optimisations ML
   
   - Interface responsive mobile/PC
   - Gradients et glassmorphism
   - Cartes métriques interactives
   - Sidebar informative
   - 24 features avancées
   - Gradient Boosting optimisé
   ```

2. Cliquez sur **Commit** (ou Ctrl+Enter)

### Étape 5 : Push vers GitHub
1. Cliquez sur le bouton **Sync Changes** ou **Push**
2. Si demandé, entrez vos identifiants GitHub

### Étape 6 : Vérification
Allez sur https://github.com/rayanefennane/Prediction-Meteo-Rabat pour voir vos changements !

---

## Méthode 2 : Ligne de Commande (Alternative)

Si VS Code ne fonctionne pas, utilisez Git Bash ou PowerShell :

```bash
# Se positionner dans le dossier
cd "c:\Users\User\OneDrive\Bureau\projetDATAMAINING\Prediction-Meteo-Rabat"

# Vérifier le statut
git status

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "✨ Design moderne 2026 + optimisations ML"

# Push vers GitHub
git push origin version-2
```

---

## Méthode 3 : GitHub Desktop (Visuel)

1. Téléchargez [GitHub Desktop](https://desktop.github.com/)
2. Ouvrez le repository
3. Sélectionnez les fichiers
4. Entrez un message de commit
5. Cliquez sur **Commit to version-2**
6. Cliquez sur **Push origin**

---

## ⚠️ Problèmes Courants

### Git n'est pas reconnu dans PowerShell
- **Solution** : Utilisez Git Bash ou l'interface VS Code

### Conflits de merge
```bash
git pull origin version-2
# Résoudre les conflits dans VS Code
git add .
git commit -m "Résolution des conflits"
git push origin version-2
```

### Authentification GitHub
Si GitHub demande un token :
1. Allez sur https://github.com/settings/tokens
2. Générez un **Personal Access Token**
3. Utilisez-le comme mot de passe

---

## ✅ Checklist Finale

- [ ] Tous les fichiers sont stagés
- [ ] Message de commit descriptif
- [ ] Push réussi vers `version-2`
- [ ] Vérification sur GitHub.com
- [ ] README.md est à jour
- [ ] Application fonctionne localement

---

## 🚀 Déploiement sur Streamlit Cloud (Optionnel)

Après le push sur GitHub :

1. Allez sur https://share.streamlit.io
2. Connectez-vous avec GitHub
3. Cliquez sur **New app**
4. Sélectionnez votre repository
5. Branche : `version-2`
6. Fichier : `app_meteo.py`
7. Cliquez sur **Deploy**

Votre app sera publique en ~2 minutes ! 🎉

---

**Bonne chance !** 🌟
