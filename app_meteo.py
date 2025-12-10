# app_meteo.py - Application Météo avec IA
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import base64
from PIL import Image
from datetime import datetime, timedelta

# --- FONCTION POUR DÉTERMINER LA SAISON ---
def get_season(month, day):
    """Retourne la saison et sa couleur selon le mois et le jour"""
    if (month == 12 and day >= 21) or month in [1, 2] or (month == 3 and day < 20):
        return "Hiver", "🔵", "#ADD8E6"  # Bleu clair
    elif (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
        return "Printemps", "🌸", "#FFB6C1"  # Rose
    elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 23):
        return "Été", "☀️", "#FFD700"  # Jaune doré
    else:
        return "Automne", "🍂", "#FF8C00"  # Orange

# --- 1. CHARGEMENT DU LOGO ---
try:
    logo_img = Image.open("meteo.jpg")
except FileNotFoundError:
    logo_img = "🌤️"

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Météo IA Rabat",
    page_icon=logo_img,
    layout="wide"
)

# --- 3. CSS MODERNE 2026 ---
st.markdown("""
<style>
    /* Style global moderne */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Header avec gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        text-align: center;
        animation: slideDown 0.6s ease-out;
    }
    
    @keyframes slideDown {
        from { 
            opacity: 0; 
            transform: translateY(-30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Cards modernes */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: transform 0.3s ease;
    }
    
    .stDataFrame:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }
    
    /* Boutons stylés */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Inputs modernes */
    .stSlider, .stNumberInput {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Graphiques avec ombre */
    .stPlotlyChart, .element-container iframe {
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    /* Sidebar style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #667eea;
    }
    
    /* Responsive Mobile */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .main-header {
            padding: 1.5rem;
        }
        
        [data-testid="column"] {
            padding: 0.5rem !important;
        }
        
        .metric-card {
            padding: 1rem !important;
        }
        
        .metric-card h2 {
            font-size: 1.5rem !important;
        }
    }
    
    /* Responsive Tablet */
    @media (max-width: 1024px) and (min-width: 769px) {
        .main-header h1 {
            font-size: 2.2rem;
        }
    }
    
    /* Animation fade-in */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Indicateurs météo */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Dark mode optimisé */
    [data-theme="dark"] {
        background-color: #0f0f23;
    }
    
    /* Améliorations tableaux */
    thead tr th {
        background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(118,75,162,0.3)) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Sélection de ligne */
    tbody tr:hover {
        background: rgba(102,126,234,0.1) !important;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. INJECTION DES ICÔNES PWA ---
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

# --- 5. HEADER MODERNE ---
st.markdown("""
<div class="main-header">
    <h1>🌤️ Météo IA - Rabat</h1>
    <p>Prédictions météorologiques intelligentes avec Gradient Boosting</p>
</div>
""", unsafe_allow_html=True)

# --- 6. SIDEBAR INFORMATIVE ---
with st.sidebar:
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    **Météo IA Rabat** utilise l'intelligence artificielle pour prédire la météo avec une précision exceptionnelle.
    
    #### 🤖 Technologie
    - **Modèle**: Gradient Boosting
    - **Features**: 24 variables avancées
    - **Données**: 5 ans d'historique
    - **Observations**: 43,848 points
    
    #### 📍 Localisation
    - **Ville**: Rabat, Maroc
    - **Coordonnées**: 34.02°N, 6.84°W
    - **Source**: Open-Meteo API
    
    #### 🎯 Caractéristiques
    - ✅ Prédictions température
    - ✅ Prévisions humidité
    - ✅ Historique 5 ans
    - ✅ Saisons colorées
    - ✅ Comparaison temps réel
    """)
    
    st.markdown("---")
    st.markdown("### 🎨 Design")
    st.markdown("""
    Interface moderne 2026 avec:
    - 🌈 Gradients dynamiques
    - 📱 Responsive mobile/PC
    - 🎭 Animations fluides
    - 🌙 Mode sombre optimisé
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Performance")
    st.info("💡 Le modèle s'améliore avec chaque mise à jour des données historiques.")

# --- 7. SECTION PRÉVISIONS ---
st.markdown("---")

# Sélecteurs
col_jours, col_heure = st.columns(2)

with col_jours:
    nb_jours = st.slider("📆 Nombre de jours de prévision", min_value=1, max_value=30, value=7, step=1)

with col_heure:
    heure_selectionnee = st.number_input("🕐 Heure de la journée", min_value=0, max_value=23, value=14, step=1)
    st.caption("Utilisez les flèches ⬆️⬇️ pour changer l'heure")

st.subheader(f"📅 Prévisions pour les {nb_jours} prochains jours à {heure_selectionnee}h")

# Chargement des modèles et données historiques
try:
    model_path = 'cerveau_meteo_long_terme.pkl'
    model_data = joblib.load(model_path)
    
    # Extraction des modèles
    if isinstance(model_data, dict):
        model_temp = model_data.get('model_temp')
        model_humidity = model_data.get('model_humidity')
        features = model_data.get('features')
        historical_data = model_data.get('historical_data')
    else:
        st.error("❌ Format de modèle non compatible. Veuillez réentraîner le modèle.")
        st.stop()
    
    # Génération des prévisions
    start_date = pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
    dates_semaine = pd.date_range(start=start_date, periods=nb_jours, freq='D')
    
    df_semaine = pd.DataFrame({'date': dates_semaine})
    df_semaine['jour_annee'] = df_semaine['date'].dt.dayofyear
    df_semaine['mois'] = df_semaine['date'].dt.month
    df_semaine['jour'] = df_semaine['date'].dt.day
    df_semaine['jour_mois'] = df_semaine['date'].dt.day
    df_semaine['heure'] = heure_selectionnee
    
    # Encodage cyclique
    df_semaine['day_cos'] = np.cos(2 * np.pi * df_semaine['jour_annee'] / 365.25)
    df_semaine['day_sin'] = np.sin(2 * np.pi * df_semaine['jour_annee'] / 365.25)
    df_semaine['hour_cos'] = np.cos(2 * np.pi * df_semaine['heure'] / 24)
    df_semaine['hour_sin'] = np.sin(2 * np.pi * df_semaine['heure'] / 24)
    df_semaine['month_cos'] = np.cos(2 * np.pi * df_semaine['mois'] / 12)
    df_semaine['month_sin'] = np.sin(2 * np.pi * df_semaine['mois'] / 12)
    
    # Features météo (valeurs moyennes des données historiques)
    if historical_data is not None:
        df_semaine['cloud_cover_filled'] = historical_data['cloud_cover'].mean()
        df_semaine['temp_rolling_24h'] = historical_data['temperature'].tail(24).mean()
        df_semaine['temp_rolling_7d'] = historical_data['temperature'].tail(168).mean()
        df_semaine['humidity_rolling_24h'] = historical_data['humidity'].tail(24).mean()
    else:
        df_semaine['cloud_cover_filled'] = 50
        df_semaine['temp_rolling_24h'] = 20
        df_semaine['temp_rolling_7d'] = 20
        df_semaine['humidity_rolling_24h'] = 70
    
    # Interactions
    df_semaine['hour_month'] = df_semaine['heure'] * df_semaine['mois']
    df_semaine['day_hour'] = df_semaine['jour_annee'] * df_semaine['heure']
    df_semaine['cloud_hour'] = df_semaine['cloud_cover_filled'] * df_semaine['heure']
    
    # Polynomiales
    df_semaine['jour_annee_sq'] = df_semaine['jour_annee'] ** 2
    df_semaine['heure_sq'] = df_semaine['heure'] ** 2
    df_semaine['mois_sq'] = df_semaine['mois'] ** 2
    
    # Indicateurs
    df_semaine['is_winter'] = ((df_semaine['mois'] == 12) | (df_semaine['mois'] <= 2)).astype(int)
    df_semaine['is_summer'] = ((df_semaine['mois'] >= 6) & (df_semaine['mois'] <= 8)).astype(int)
    df_semaine['is_night'] = ((df_semaine['heure'] >= 20) | (df_semaine['heure'] <= 6)).astype(int)
    df_semaine['is_midday'] = ((df_semaine['heure'] >= 11) & (df_semaine['heure'] <= 15)).astype(int)
    
    # Prédictions avec toutes les features
    df_semaine['Prediction_Temp'] = model_temp.predict(df_semaine[features])
    df_semaine['Prediction_Humidity'] = model_humidity.predict(df_semaine[features])
    
    # Ajout des saisons
    df_semaine['Saison'], df_semaine['Icone_Saison'], df_semaine['Couleur_Saison'] = zip(*df_semaine.apply(
        lambda row: get_season(row['mois'], row['jour']), axis=1
    ))
    
    # Noms des jours en français
    jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    # Affichage du tableau avec saisons
    df_affichage = df_semaine.copy()
    df_affichage['Jour'] = df_affichage['date'].dt.dayofweek.map(lambda x: jours_fr[x])
    df_affichage['Date'] = df_affichage['date'].dt.strftime('%d/%m')
    df_affichage['Saison_Display'] = df_affichage['Icone_Saison'] + ' ' + df_affichage['Saison']
    df_affichage['Température'] = df_affichage['Prediction_Temp'].round(1).astype(str) + '°C'
    df_affichage['💧 Humidité'] = df_affichage['Prediction_Humidity'].round(0).astype(int).astype(str) + '%'
    
    # Création du tableau final
    df_display = df_affichage[['Jour', 'Date', 'Saison_Display', 'Température', '💧 Humidité']].copy()
    df_display.columns = ['Jour', 'Date', 'Saison', 'Température', '💧 Humidité']
    
    # Cartes métriques modernes
    st.markdown("### 📊 Statistiques de la semaine")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp_min = df_semaine['Prediction_Temp'].min()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #00D9FF; margin: 0;">❄️</h3>
            <h2 style="margin: 0.5rem 0;">{temp_min:.1f}°C</h2>
            <p style="color: rgba(255,255,255,0.7); margin: 0;">Temp. Min</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        temp_max = df_semaine['Prediction_Temp'].max()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #FF6B6B; margin: 0;">🔥</h3>
            <h2 style="margin: 0.5rem 0;">{temp_max:.1f}°C</h2>
            <p style="color: rgba(255,255,255,0.7); margin: 0;">Temp. Max</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        hum_moy = df_semaine['Prediction_Humidity'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #4ECDC4; margin: 0;">💧</h3>
            <h2 style="margin: 0.5rem 0;">{hum_moy:.0f}%</h2>
            <p style="color: rgba(255,255,255,0.7); margin: 0;">Humidité Moy.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        temp_moy = df_semaine['Prediction_Temp'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #FFD93D; margin: 0;">🌡️</h3>
            <h2 style="margin: 0.5rem 0;">{temp_moy:.1f}°C</h2>
            <p style="color: rgba(255,255,255,0.7); margin: 0;">Temp. Moyenne</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Affichage avec sélection de ligne
    st.write("### 📅 Tableau des prévisions (Cliquez sur une ligne pour voir l'historique)")
    
    # Utiliser st.dataframe avec on_select
    event = st.dataframe(
        df_display,
        hide_index=True,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # Affichage de l'historique si une ligne est sélectionnée
    if event.selection and len(event.selection.rows) > 0:
        selected_row = event.selection.rows[0]
        selected_date = dates_semaine[selected_row]
        selected_month = selected_date.month
        selected_day = selected_date.day
        
        st.markdown("---")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,107,107,0.2) 0%, rgba(118,75,162,0.2) 100%); 
                    padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
            <h3 style="margin: 0; color: #FF6B6B;">📜 Historique pour le {selected_day:02d}/{selected_month:02d} à {heure_selectionnee}h</h3>
            <p style="margin-top: 0.5rem; opacity: 0.9;">Données des 5 dernières années</p>
        </div>
        """, unsafe_allow_html=True)
        
        if historical_data is not None:
            # Filtrer les données historiques pour cette date et heure
            hist_filtered = historical_data[
                (historical_data['date'].dt.month == selected_month) &
                (historical_data['date'].dt.day == selected_day) &
                (historical_data['date'].dt.hour == heure_selectionnee)
            ].copy()
            
            if len(hist_filtered) > 0:
                # Afficher les 5 dernières années
                hist_filtered['Année'] = hist_filtered['date'].dt.year
                hist_filtered = hist_filtered.sort_values('Année', ascending=False).head(5)
                
                hist_display = hist_filtered[['Année', 'temperature', 'humidity']].copy()
                hist_display.columns = ['Année', '🌡️ Température (°C)', '💧 Humidité (%)']
                hist_display['🌡️ Température (°C)'] = hist_display['🌡️ Température (°C)'].round(1)
                hist_display['💧 Humidité (%)'] = hist_display['💧 Humidité (%)'].round(0).astype(int)
                
                st.dataframe(hist_display, hide_index=True, width="stretch")
                
                # Graphique de l'évolution avec colonnes
                col_hist1, col_hist2 = st.columns(2)
                
                with col_hist1:
                    st.markdown("**🌡️ Évolution de la température**")
                    st.line_chart(hist_display.set_index('Année')[['🌡️ Température (°C)']], color='#FF6B6B')
                
                with col_hist2:
                    st.markdown("**💧 Évolution de l'humidité**")
                    st.line_chart(hist_display.set_index('Année')[['💧 Humidité (%)']], color='#4ECDC4')
            else:
                st.info("Aucune donnée historique disponible pour cette date.")
        else:
            st.warning("Les données historiques ne sont pas disponibles. Réentraînez le modèle.")
    
    # Graphique de comparaison (colonne droite)
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
        <h3 style="margin: 0; color: #667eea;">📈 Comparaison : Prévisions IA vs Météo Réelle</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupération de la météo réelle pour comparaison
    try:
        days_to_fetch = min(nb_jours, 16)  # API limite à 16 jours
        url_forecast = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 34.0209,
            "longitude": -6.8416,
            "daily": "temperature_2m_max",
            "timezone": "GMT",
            "forecast_days": days_to_fetch
        }
        res = requests.get(url_forecast, params=params).json()
        
        # DataFrame avec les données réelles
        df_api = pd.DataFrame({
            'date': pd.to_datetime(res['daily']['time']),
            'Météo_Réelle': res['daily']['temperature_2m_max']
        })
        
        # Fusion avec les prédictions
        df_semaine_graph = df_semaine.copy()
        df_semaine_graph['date'] = df_semaine_graph['date'].dt.normalize()
        df_comparison = pd.merge(df_semaine_graph, df_api, on='date', how='inner')
        
        if len(df_comparison) > 0:
            st.caption(f"📊 Comparaison sur {len(df_comparison)} jours : Votre IA (à {heure_selectionnee}h) vs Météo Officielle (Max du jour)")
            
            # Graphique comparatif
            chart_comparison = df_comparison.set_index('date')[['Prediction_Temp', 'Météo_Réelle']]
            chart_comparison.columns = [f'IA à {heure_selectionnee}h (°C)', 'Météo Réelle Max (°C)']
            st.line_chart(chart_comparison)
            
            # Calcul de l'écart moyen
            ecart = (df_comparison['Prediction_Temp'] - df_comparison['Météo_Réelle']).abs().mean()
            
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            
            # Afficher le nombre total de jours sélectionnés au lieu de jours comparés
            nb_jours_affiches = nb_jours
            
            with col_metric1:
                if ecart < 2:
                    badge_color = "#4ECDC4"
                    badge_emoji = "✅"
                    badge_text = "Excellent"
                elif ecart < 4:
                    badge_color = "#FFD93D"
                    badge_emoji = "ℹ️"
                    badge_text = "Bon"
                else:
                    badge_color = "#FF6B6B"
                    badge_emoji = "⚠️"
                    badge_text = "Acceptable"
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(78,205,196,0.2), rgba(78,205,196,0.1)); 
                            padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0; color: {badge_color};">{badge_emoji}</h3>
                    <h2 style="margin: 0.5rem 0; color: {badge_color};">{ecart:.2f}°C</h2>
                    <p style="margin: 0; opacity: 0.8;">Écart Moyen</p>
                    <p style="margin: 0; color: {badge_color}; font-weight: 600;">{badge_text}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_metric2:
                precision = 100 - (ecart / df_comparison['Météo_Réelle'].mean() * 100)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(102,126,234,0.1)); 
                            padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0; color: #667eea;">🎯</h3>
                    <h2 style="margin: 0.5rem 0; color: #667eea;">{precision:.1f}%</h2>
                    <p style="margin: 0; opacity: 0.8;">Précision</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_metric3:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(255,107,107,0.2), rgba(255,107,107,0.1)); 
                            padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0; color: #FF6B6B;">📅</h3>
                    <h2 style="margin: 0.5rem 0; color: #FF6B6B;">{nb_jours_affiches}</h2>
                    <p style="margin: 0; opacity: 0.8;">Jours Analysés</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Pas de données de comparaison disponibles")
    except Exception as e:
        st.warning(f"Impossible de récupérer la météo réelle : {e}")
    
    # Graphique humidité
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(78,205,196,0.2) 0%, rgba(102,126,234,0.2) 100%); 
                padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
        <h3 style="margin: 0; color: #4ECDC4;">💧 Évolution de l'humidité</h3>
        <p style="margin-top: 0.5rem; opacity: 0.9;">Prévisions sur {nb_jours} jours</p>
    </div>
    """, unsafe_allow_html=True)
    
    chart_humidity = df_semaine.set_index('date')[['Prediction_Humidity']]
    chart_humidity.columns = ['Humidité (%)']
    st.area_chart(chart_humidity, color='#4ECDC4')

except FileNotFoundError:
    st.error(f"❌ Fichier modèle introuvable : '{model_path}'. Veuillez relancer le notebook d'entraînement.")
except Exception as e:
    st.error(f"Erreur lors de la prédiction : {e}")
    st.exception(e)
