# app_meteo.py - Application Météo avec IA
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests

st.set_page_config(page_title="🌤️ Météo IA Rabat", layout="wide")
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
        model_data = joblib.load('cerveau_meteo_long_terme.pkl')
        
        # Vérifier le format des modèles
        if isinstance(model_data, dict):
            if 'model_temp' in model_data:
                # Nouveau format avec modèle pluie
                model_temp = model_data['model_temp']
                model_pluie = model_data['model_pluie']
                features = model_data['features']
            else:
                # Ancien format
                model_temp = model_data['model']
                model_pluie = None
                features = model_data['features']
        else:
            model_temp = model_data
            model_pluie = None
            features = ['day_cos', 'day_sin', 'heure', 'mois']
        
        # 2. On génère les N prochains jours selon le choix
        dates_semaine = pd.date_range(start=pd.Timestamp.now(), periods=nb_jours, freq='D')
        
        # 3. On prépare les features (version optimisée)
        df_semaine = pd.DataFrame({'date': dates_semaine})
        df_semaine['jour_annee'] = df_semaine['date'].dt.dayofyear
        df_semaine['mois'] = df_semaine['date'].dt.month
        df_semaine['heure'] = heure_selectionnee  # Heure choisie par l'utilisateur
        
        # Encodage cyclique COMPLET
        df_semaine['day_cos'] = np.cos(2 * np.pi * df_semaine['jour_annee'] / 365.25)
        df_semaine['day_sin'] = np.sin(2 * np.pi * df_semaine['jour_annee'] / 365.25)
        df_semaine['hour_cos'] = np.cos(2 * np.pi * df_semaine['heure'] / 24)
        df_semaine['hour_sin'] = np.sin(2 * np.pi * df_semaine['heure'] / 24)
        df_semaine['month_cos'] = np.cos(2 * np.pi * df_semaine['mois'] / 12)
        df_semaine['month_sin'] = np.sin(2 * np.pi * df_semaine['mois'] / 12)
        
        # 4. Prédiction température
        df_semaine['Prediction_IA'] = model_temp.predict(df_semaine[features])
        
        # 5. Prédiction probabilité de pluie
        if model_pluie is not None:
            df_semaine['Prob_Pluie'] = model_pluie.predict_proba(df_semaine[features])[:, 1] * 100
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
        df_affichage['🌧️ Pluie'] = df_affichage['Prob_Pluie'].round(0).astype(int).astype(str) + '%'
        df_affichage = df_affichage[['Jour', 'Date', 'Heure', 'Température', '🌧️ Pluie']]
        st.dataframe(df_affichage, hide_index=True)

    except Exception as e:
        st.error(f"Erreur modèle : {e}")

with col_graph:
    # 5. Comparaison avec la météo réelle
    try:
        # On récupère la vraie prévision météo pour comparer
        url_forecast = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 34.0209, "longitude": -6.8416,
            "daily": "temperature_2m_max",
            "timezone": "GMT"
        }
        res = requests.get(url_forecast, params=params).json()
        
        # On crée un DataFrame avec les données API
        df_api = pd.DataFrame({
            'date': pd.to_datetime(res['daily']['time']),
            'Météo_Réelle': res['daily']['temperature_2m_max']
        })
        
        # On fusionne avec vos données IA pour faire un beau graph
        # On limite aux jours communs (API ne donne que 7 jours max)
        df_semaine['date'] = df_semaine['date'].dt.normalize() # Enlever les heures pour matcher
        df_final = pd.merge(df_semaine, df_api, on='date', how='inner')
        
        if len(df_final) > 0:
            st.write("### ⚔️ Comparatif : Mon IA vs Météo Réelle")
            st.caption(f"*(Comparaison limitée à {len(df_final)} jours - données disponibles)*")
            
            # Graphique comparatif
            chart_data = df_final.set_index('date')[['Prediction_IA', 'Météo_Réelle']]
            st.line_chart(chart_data)
            
            # Calcul de l'écart moyen
            ecart = (df_final['Prediction_IA'] - df_final['Météo_Réelle']).abs().mean()
            st.info(f"Écart moyen entre votre modèle et la météo réelle : **{ecart:.2f}°C**")
        else:
            st.warning("Pas de données disponibles pour la comparaison")
        
    except Exception as e:
        st.warning(f"Impossible de récupérer l'API officielle pour comparaison : {e}")
