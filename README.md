# 🌤️ Météo IA - Rabat

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52.0-red.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7.2-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Application web moderne de prédiction météorologique pour Rabat (Maroc) utilisant l'intelligence artificielle et le machine learning.

## ✨ Fonctionnalités

- 🎯 **Prédictions IA précises** : Gradient Boosting avec 24 features avancées
- 📊 **Historique 5 ans** : Consultation des données météo passées
- 🌈 **Saisons colorées** : Indicateurs visuels avec emojis
- 📱 **Design 2026** : Interface moderne et responsive (mobile/PC)
- 🔄 **Comparaison temps réel** : Vérification avec API météo officielle
- 💧 **Humidité intelligente** : Prévisions d'humidité par régression non-linéaire
- 🎨 **Dark Mode** : Thème sombre optimisé

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Étapes

1. **Cloner le repository**
```bash
git clone https://github.com/rayanefennane/Prediction-Meteo-Rabat.git
cd Prediction-Meteo-Rabat
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
```

3. **Activer l'environnement**
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Entraîner le modèle** (première utilisation)

Ouvrez `entrainer_modele.ipynb` dans Jupyter et exécutez toutes les cellules.

6. **Lancer l'application**
```bash
streamlit run app_meteo.py
```

L'application sera accessible sur **http://localhost:8501**

## 📦 Dépendances

```txt
streamlit==1.52.0
pandas==2.3.3
numpy==2.2.2
scikit-learn==1.7.2
joblib==1.4.2
requests==2.32.3
```

## 🤖 Architecture

### Modèle de Machine Learning

- **Algorithme** : Gradient Boosting Regressor
- **Estimateurs** : 300 arbres
- **Learning Rate** : 0.05
- **Max Depth** : 7
- **Subsample** : 0.8

### Features Engineerées (24 au total)

1. **Cycliques** : sin/cos du jour, heure, mois
2. **Rolling** : moyennes mobiles 24h et 7 jours
3. **Polynomiales** : carrés de température, humidité, etc.
4. **Interactions** : heure×mois, jour×heure, cloud×heure
5. **Indicateurs binaires** : hiver, été, nuit, midi

### Source des Données

- **API** : [Open-Meteo](https://open-meteo.com/)
- **Période** : 5 ans (2020-2025)
- **Fréquence** : Horaire
- **Points de données** : 43,848 observations

## 📊 Performance

- **Écart moyen** : < 2°C (excellent)
- **Précision** : > 90%
- **Temps de prédiction** : < 100ms

## 🎨 Design Moderne 2026

L'interface utilise :
- **Gradients dynamiques** : Violet/Bleu pour un look moderne
- **Glassmorphism** : Effets de transparence et flou
- **Animations fluides** : Transitions CSS3
- **Responsive** : Mobile-first avec breakpoints adaptatifs
- **Typography** : Google Fonts Poppins
- **Dark Mode** : Palette optimisée pour les yeux

## 📱 Utilisation

1. **Sélectionnez le nombre de jours** (1-30)
2. **Choisissez l'heure** (0-23)
3. **Consultez les prévisions** dans le tableau
4. **Cliquez sur une ligne** pour voir l'historique 5 ans
5. **Comparez avec la météo réelle** dans les graphiques

## 📂 Structure du Projet

```
Prediction-Meteo-Rabat/
├── app_meteo.py                    # Application Streamlit
├── entrainer_modele.ipynb          # Notebook d'entraînement
├── entrainer_modele_v2.ipynb       # Version avancée
├── entrainer_modele.py             # Script Python
├── cerveau_meteo_long_terme.pkl    # Modèle sauvegardé
├── requirements.txt                # Dépendances
├── .streamlit/
│   └── config.toml                 # Configuration Streamlit
├── apple-touch-icon.png            # Icône PWA
└── README.md                       # Documentation
```

## 🛠️ Technologies Utilisées

- **Frontend** : Streamlit (CSS moderne embarqué)
- **Backend** : Python 3.14
- **ML** : scikit-learn (Gradient Boosting)
- **Data** : pandas, numpy
- **API** : requests (Open-Meteo)
- **Sérialisation** : joblib

## 🌍 Déploiement

### Streamlit Cloud (Recommandé)

1. Push sur GitHub
2. Connectez-vous sur [share.streamlit.io](https://share.streamlit.io)
3. Déployez depuis votre repository

## 📈 Améliorations Futures

- [ ] Ajout de prévisions de précipitations
- [ ] Notifications push pour alertes météo
- [ ] Multi-villes (autres villes du Maroc)
- [ ] Export PDF des prévisions

## 🤝 Contribution

Les contributions sont les bienvenues ! Créez une Pull Request.

## 📝 Licence

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

**Rayane Fennane**

- GitHub: [@rayanefennane](https://github.com/rayanefennane)
- Repository: [Prediction-Meteo-Rabat](https://github.com/rayanefennane/Prediction-Meteo-Rabat)

## 🙏 Remerciements

- [Open-Meteo](https://open-meteo.com/) pour l'API météo gratuite
- [Streamlit](https://streamlit.io/) pour le framework web
- [scikit-learn](https://scikit-learn.org/) pour les outils ML

---

⭐ **Si ce projet vous a plu, n'hésitez pas à lui donner une étoile !**
