# app_meteo.py - Application Météo avec IA
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import base64
from PIL import Image # <-- Import nécessaire pour gérer les images

# --- 1. CHARGEMENT DU LOGO ---
# On essaie de charger l'image meteo.jpg comme logo uniquement
try:
    # Assurez-vous que 'meteo.jpg' est dans le même dossier que ce script
    logo_img = Image.open("meteo.jpg")
except FileNotFoundError:
    # Si l'image n'est pas trouvée, on utilise un émoji par défaut
    logo_img = "🌤️"

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Météo IA Rabat",
    page_icon=logo_img,  # <-- L'image est utilisée uniquement comme icône d'onglet
    layout="wide"
)

# --- 3. INJECTION DES ICÔNES POUR TÉLÉPHONE (PWA) ---
# Cela permet d'avoir le bon logo quand on ajoute l'app à l'écran d'accueil
try:
    with open("apple-touch-icon.png", "rb") as f:
        apple_icon = base64.b64encode(f.read()).decode()
    
    st.markdown(f'''
        <link rel="apple-touch-icon" href="data:image/png;base64,{apple_icon}">
        <link rel="icon" type="image/png" sizes="192x192" href="data:image/png;base64,{apple_icon}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="Météo Rabat">
    ''', unsafe_allow_html=True)
except:
    pass

st.title("🌤️ Application Météo IA - Rabat")

# --- SECTION PRÉVISIONS ---

st.markdown("---")

# Sélecteurs
col_jours, col_heure = st.columns(2)

with col_jours:
    nb_jours = st.slider("📆 Nombre de jours de prévision", min_value=1, max_value=30, value=7, step=1)

with col_heure:
    heure_selectionnee = st.number_input("🕐 Heure de la journée", min_value=0, max_value=23, value=14, step=1)
    st.caption("Utilisez les flèches ⬆️⬇️ pour changer l'heure")

st.subheader(f"📅 Prévisions pour les {nb_jours} prochains jours à {heure_selectionnee}h")

col_pred, col_graph = st.columns([1, 2])

with col_pred:
    st.write("Calcul des prédictions...")
    
    # 1. On charge les modèles (température + pluie)
    try:
        # ATTENTION : Assurez-vous que ce fichier existe bien !
        # Si vous n'avez que l'ancien modèle, remettez 'cerveau_meteo_long_terme.pkl'
        # Si vous avez suivi l'étape avec la pluie, utilisez le nouveau nom.
        # Pour ce test, je suppose que vous utilisez celui que vous m'avez indiqué.
        model_path = 'cerveau_meteo_long_terme.pkl' 
        model_data = joblib.load(model_path)
        
        # Vérifier le format des modèles (Gestion de compatibilité Ancien/Nouveau notebook)
        if isinstance(model_data, dict):
            if 'model_temp' in model_data:
                # Nouveau format avec modèle pluie
                model_temp = model_data['model_temp']
                model_pluie = model_data.get('model_pluie') # Utilise .get() pour éviter crash si absent
                features = model_data['features']
            else:
                # Format intermédiaire
                model_temp = model_data['model']
                model_pluie = None
                features = model_data['features']
        else:
            # Ancien format (juste le modèle sklearn)
            model_temp = model_data
            model_pluie = None
            # Features par défaut de l'ancien notebook
            features = ['day_cos', 'day_sin', 'heure', 'mois']
        
        # 2. On génère les N prochains jours selon le choix
        # On commence à demain pour la prévision
        start_date = pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
        dates_semaine = pd.date_range(start=start_date, periods=nb_jours, freq='D')
        
        # 3. On prépare les features (version optimisée)
        df_semaine = pd.DataFrame({'date': dates_semaine})
        df_semaine['jour_annee'] = df_semaine['date'].dt.dayofyear
        df_semaine['mois'] = df_semaine['date'].dt.month
        df_semaine['heure'] = heure_selectionnee  # Heure choisie par l'utilisateur
        
        # Encodage cyclique COMPLET (Doit correspondre exactement à l'entraînement)
        df_semaine['day_cos'] = np.cos(2 * np.pi * df_semaine['jour_annee'] / 365.25)
        df_semaine['day_sin'] = np.sin(2 * np.pi * df_semaine['jour_annee'] / 365.25)
        # Si votre modèle n'a pas été entraîné avec hour_cos/sin et month_cos/sin, 
        # ces colonnes seront ignorées lors de la prédiction si 'features' est correct.
        df_semaine['hour_cos'] = np.cos(2 * np.pi * df_semaine['heure'] / 24)
        df_semaine['hour_sin'] = np.sin(2 * np.pi * df_semaine['heure'] / 24)
        df_semaine['month_cos'] = np.cos(2 * np.pi * df_semaine['mois'] / 12)
        df_semaine['month_sin'] = np.sin(2 * np.pi * df_semaine['mois'] / 12)
        
        # 4. Prédiction température
        # On ne sélectionne QUE les features que le modèle connaît
        df_semaine['Prediction_IA'] = model_temp.predict(df_semaine[features])
        
        # 5. Prédiction probabilité de pluie
        if model_pluie is not None:
            # La pluie est plus complexe, souvent on prédit sur la journée entière, pas une heure précise.
            # Pour simplifier ici, on utilise les mêmes features.
            try:
                df_semaine['Prob_Pluie'] = model_pluie.predict_proba(df_semaine[features])[:, 1] * 100
            except:
                 df_semaine['Prob_Pluie'] = 0 # Si erreur sur le modèle pluie
        else:
            df_semaine['Prob_Pluie'] = 0
        
        # Noms des jours en français
        jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        # Affichage du tableau avec le nom du jour et la pluie
        df_affichage = df_semaine[['date', 'Prediction_IA', 'Prob_Pluie']].copy()
        df_affichage['Jour'] = df_affichage['date'].dt.dayofweek.map(lambda x: jours_fr[x])
        df_affichage['Date'] = df_affichage['date'].dt.strftime('%d/%m')
        df_affichage['Heure'] = f"{heure_selectionnee}h"
        df_affichage['Température'] = df_affichage['Prediction_IA'].round(1).astype(str) + '°C'
        
        # Gestion de l'affichage de la pluie (si 0%, on met juste un tiret pour faire propre)
        df_affichage['🌧️ Pluie'] = df_affichage['Prob_Pluie'].apply(lambda x: f"{int(x)}%" if x > 1 else "-")

        
        df_affichage_final = df_affichage[['Jour', 'Date', 'Heure', 'Température', '🌧️ Pluie']]
        st.dataframe(df_affichage_final, hide_index=True, width="stretch")

    except FileNotFoundError:
         st.error(f"❌ Fichier modèle introuvable : '{model_path}'. Veuillez relancer le notebook d'entraînement.")
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
        # st.exception(e) # Décommentez pour voir le détail de l'erreur si besoin

with col_graph:
    # 5. Comparaison avec la météo réelle
    try:
        # On récupère la vraie prévision météo pour comparer
        # NOTE: L'API gratuite Forecast donne 7 jours max.
        days_to_fetch = min(nb_jours, 7)

        url_forecast = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 34.0209, "longitude": -6.8416,
            "daily": "temperature_2m_max", # On compare avec le MAX journalier officiel
            "timezone": "GMT",
            "days": days_to_fetch
        }
        res = requests.get(url_forecast, params=params).json()
        
        # On crée un DataFrame avec les données API
        df_api = pd.DataFrame({
            'date': pd.to_datetime(res['daily']['time']),
            # On renomme pour que ce soit clair sur le graphique
            'Météo_Officielle (Max Jour)': res['daily']['temperature_2m_max']
        })
        
        # On fusionne avec vos données IA pour faire un beau graph
        # On limite aux jours communs
        df_semaine_graph = df_semaine.copy()
        df_semaine_graph['date'] = df_semaine_graph['date'].dt.normalize() # Enlever les heures pour matcher
        
        # Merge inner pour ne garder que les dates présentes dans les deux
        df_final = pd.merge(df_semaine_graph, df_api, on='date', how='inner')
        
        if len(df_final) > 0:
            st.write(f"### ⚔️ Comparatif sur {len(df_final)} jours")
            st.caption(f"Comparaison : Votre IA à {heure_selectionnee}h VS Météo Officielle (Max de la journée)")
            
            # Graphique comparatif
            # On renomme votre colonne pour le graphique
            df_final = df_final.rename(columns={'Prediction_IA': f'Votre IA ({heure_selectionnee}h)'})
            chart_data = df_final.set_index('date')[[f'Votre IA ({heure_selectionnee}h)', 'Météo_Officielle (Max Jour)']]
            
            # Affichage avec des couleurs personnalisées si possible, sinon defaut
            st.line_chart(chart_data)
            
            # Calcul de l'écart moyen
            ecart = (df_final[f'Votre IA ({heure_selectionnee}h)'] - df_final['Météo_Officielle (Max Jour)']).abs().mean()
            
            # Interprétation de l'écart
            if ecart < 2:
                 st.success(f"✅ Excellent ! Écart moyen très faible : **{ecart:.2f}°C**")
            elif ecart < 4:
                 st.info(f"ℹ️ Bon résultat. Écart moyen raisonnable : **{ecart:.2f}°C**")
            else:
                 st.warning(f"⚠️ Écart moyen important : **{ecart:.2f}°C**. (Normal si vous comparez 8h du matin avec le max de la journée)")

        else:
            st.warning("Pas de données communes disponibles pour la comparaison (Vérifiez les dates).")
        
    except Exception as e:
        st.warning(f"Impossible de récupérer l'API officielle pour comparaison : {e}")