import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Tableau de bord unifié", layout="wide")

# === Chargement des données depuis le dossier courant ===
try:
    df_ab = pd.read_csv("tests_par_semaine_antibiotiques_2024.csv")
    df_other = pd.read_excel("other Antibiotiques staph aureus.xlsx")
    df_pheno = pd.read_excel("staph_aureus_pheno_final.xlsx")
    df_service = pd.read_excel("staph aureus hebdomadaire excel.xlsx")
    df_bact = pd.read_excel("TOUS les bacteries a etudier.xlsx")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement automatique des fichiers : {e}")
    st.stop()

# Nettoyage des colonnes
for df in [df_ab, df_other, df_pheno, df_service, df_bact]:
    df.columns = df.columns.str.strip()

# Prétraitement services
df_service['DATE_ENTREE'] = pd.to_datetime(df_service['DATE_ENTREE'], errors='coerce')
df_service['Week'] = df_service['DATE_ENTREE'].dt.isocalendar().week

# Tabs
onglets = [
    "Antibiotiques 2024",
    "Autres Antibiotiques",
    "Phénotypes Staph aureus",
    "Fiches Bactéries",
    "Alertes par service"
]
tab1, tab2, tab3, tab4, tab5 = st.tabs(onglets)

# === Onglet 1 ===
with tab1:
    st.header("📌 Antibiotiques - Données 2024")
    week_col = "Semaine"
    df_ab = df_ab[df_ab[week_col].apply(lambda x: str(x).isdigit())]
    df_ab[week_col] = df_ab[week_col].astype(int)
    ab_cols = [col for col in df_ab.columns if col.startswith('%')]
    selected_ab = st.selectbox("Sélectionner un antibiotique", ab_cols)
    min_week, max_week = df_ab[week_col].min(), df_ab[week_col].max()
    week_range = st.slider("Plage de semaines", min_week, max_week, (min_week, max_week))

    df_filtered = df_ab[(df_ab[week_col] >= week_range[0]) & (df_ab[week_col] <= week_range[1])]
    values = pd.to_numeric(df_filtered[selected_ab], errors='coerce').dropna()
    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lower, upper = max(q1 - 1.5 * iqr, 0), q3 + 1.5 * iqr

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered[week_col], y=df_filtered[selected_ab], mode='lines+markers', name=selected_ab))
    fig.add_trace(go.Scatter(x=df_filtered[week_col], y=[upper]*len(df_filtered), mode='lines', name="Seuil haut", line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=df_filtered[week_col], y=[lower]*len(df_filtered), mode='lines', name="Seuil bas", line=dict(dash='dot')))
    fig.update_layout(yaxis=dict(range=[0, 30]), xaxis_title="Semaine", yaxis_title="Résistance (%)")
    st.plotly_chart(fig, use_container_width=True)

    # Résumé
    st.markdown("### 🧾 Résumé")
    st.write(f"🔢 Nombre de semaines analysées : {df_filtered[selected_ab].count()}")
    st.write(f"📊 Moyenne de résistance : {df_filtered[selected_ab].mean():.2f} %")
    st.write(f"💥 Semaine avec le pic de résistance : Semaine {df_filtered.loc[df_filtered[selected_ab].idxmax(), week_col]}")

    # Semaines avec alerte
    st.markdown("### 🚨 Semaines avec alerte de résistance")
    alert_df = df_filtered[df_filtered[selected_ab] > upper]
    if not alert_df.empty:
        alert_weeks = sorted(alert_df[week_col].unique())
        selected_alert_week = st.selectbox("📆 Choisir une semaine d'alerte :", alert_weeks)

        services = df_service[df_service['Week'] == selected_alert_week]['LIBELLE_DEMANDEUR'].dropna().unique()
        if len(services) > 0:
            st.markdown(f"### 🏥 Services concernés en semaine {selected_alert_week} :")
            for s in services:
                st.write(f"🔸 {s}")
        else:
            st.info("Aucun service enregistré cette semaine.")
    else:
        st.info("✅ Aucune semaine avec résistance au-dessus du seuil.")
