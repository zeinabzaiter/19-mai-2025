import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Tableau de bord unifié", layout="wide")

# === Chargement des données depuis un répertoire local ===
try:
    df_ab = pd.read_csv("data/tests_par_semaine_antibiotiques_2024.csv")
    df_other = pd.read_excel("data/other Antibiotiques staph aureus.xlsx")
    df_pheno = pd.read_excel("data/staph_aureus_pheno_final.xlsx")
    df_service = pd.read_excel("data/staph aureus hebdomadaire excel.xlsx")
    df_bact = pd.read_excel("data/TOUS les bacteries a etudier.xlsx")
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
with tab2:
    st.header("🧪 Autres Antibiotiques - Staph aureus")
    week_col = "Week"
    df_other = df_other[df_other[week_col].apply(lambda x: str(x).isdigit())]
    df_other[week_col] = df_other[week_col].astype(int)
    ab_cols = [col for col in df_other.columns if col.startswith('%')]

    selected_ab = st.selectbox("Sélectionner un antibiotique", ab_cols)
    min_week, max_week = df_other[week_col].min(), df_other[week_col].max()
    week_range = st.slider("Plage de semaines", min_week, max_week, (min_week, max_week))

    df_filtered = df_other[(df_other[week_col] >= week_range[0]) & (df_other[week_col] <= week_range[1])]
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
        selected_alert_week = st.selectbox("📆 Choisir une semaine d'alerte :", alert_weeks, key="alert_other")

        services = df_service[df_service['Week'] == selected_alert_week]['LIBELLE_DEMANDEUR'].dropna().unique()
        if len(services) > 0:
            st.markdown(f"### 🏥 Services concernés en semaine {selected_alert_week} :")
            for s in services:
                st.write(f"🔸 {s}")
        else:
            st.info("Aucun service enregistré cette semaine.")
    else:
        st.info("✅ Aucune semaine avec résistance au-dessus du seuil.")
with tab3:
    st.header("🧬 Phénotypes - Staph aureus")

    # Préparation des données
    df_pheno["week"] = pd.to_datetime(df_pheno["week"], errors="coerce")
    df_pheno = df_pheno.dropna(subset=["week"])
    df_pheno["WeekDate"] = df_pheno["week"].dt.date
    phenos = ["MRSA", "Other", "VRSA", "Wild"]
    df_pheno["Total"] = df_pheno[phenos].sum(axis=1)
    for pheno in phenos:
        df_pheno[f"% {pheno}"] = (df_pheno[pheno] / df_pheno["Total"]) * 100

    selected_pheno = st.selectbox("Sélectionner un phénotype", phenos)
    min_date, max_date = df_pheno["WeekDate"].min(), df_pheno["WeekDate"].max()
    date_range = st.slider("Plage de semaines", min_date, max_date, (min_date, max_date))

    filtered_pheno = df_pheno[(df_pheno["WeekDate"] >= date_range[0]) & (df_pheno["WeekDate"] <= date_range[1])]
    pct_col = f"% {selected_pheno}"
    values = filtered_pheno[pct_col].dropna()
    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lower, upper = max(q1 - 1.5 * iqr, 0), q3 + 1.5 * iqr

    # Graphique
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered_pheno["WeekDate"], y=filtered_pheno[pct_col],
                             mode='lines+markers', name=pct_col))
    fig.add_trace(go.Scatter(x=filtered_pheno["WeekDate"], y=[upper]*len(filtered_pheno),
                             mode='lines', name="Seuil haut", line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=filtered_pheno["WeekDate"], y=[lower]*len(filtered_pheno),
                             mode='lines', name="Seuil bas", line=dict(dash='dot')))
    fig.update_layout(yaxis=dict(range=[0, 100]), xaxis_title="Semaine", yaxis_title="Résistance (%)")
    st.plotly_chart(fig, use_container_width=True)

    # Résumé
    st.markdown("### 🧾 Résumé")
    st.write(f"🔢 Nombre de semaines analysées : {filtered_pheno[pct_col].count()}")
    st.write(f"📊 Moyenne de {selected_pheno} : {filtered_pheno[pct_col].mean():.2f} %")
    st.write(f"💥 Semaine avec le pic de {selected_pheno} : {filtered_pheno.loc[filtered_pheno[pct_col].idxmax(), 'WeekDate']}")

    # Alertes par pic
    st.markdown("### 🚨 Semaines avec alerte de phénotype")
    alert_df = filtered_pheno[filtered_pheno[pct_col] > upper]
    if not alert_df.empty:
        alert_weeks = sorted(alert_df["week"].dt.isocalendar().week.unique())
        selected_alert_week = st.selectbox("📆 Choisir une semaine d'alerte :", alert_weeks, key="alert_pheno")

        services = df_service[df_service['Week'] == selected_alert_week]['LIBELLE_DEMANDEUR'].dropna().unique()
        if len(services) > 0:
            st.markdown(f"### 🏥 Services concernés en semaine {selected_alert_week} :")
            for s in services:
                st.write(f"🔸 {s}")
        else:
            st.info("Aucun service enregistré cette semaine.")
    else:
        st.info("✅ Aucune semaine avec pic de {selected_pheno} au-dessus du seuil.")
with tab4:
    st.header("🧫 Détail des bactéries à étudier")

    search = st.text_input("🔍 Rechercher une bactérie :", "")
    filtered_df = df_bact[df_bact["Category"].str.contains(search, case=False, na=False)]

    st.subheader("📋 Liste des bactéries")
    st.dataframe(filtered_df[["Category", "Key Antibiotics"]])

    if not filtered_df.empty:
        selected = st.selectbox("📌 Sélectionner une bactérie :", filtered_df["Category"].unique())
        details = df_bact[df_bact["Category"] == selected].iloc[0]

        st.markdown(f"## 🧬 Détails : {selected}")

        st.write("**🔑 Key Antibiotics**")
        st.write(details["Key Antibiotics"])

        st.write("**💊 Other Antibiotics**")
        st.write(details["Other Antibiotics"])

        st.write("**🧬 Phénotype**")
        st.write(details["Phenotype"])
    else:
        st.info("Aucune bactérie ne correspond à votre recherche.")
with tab5:
    st.header("⚠️ Alertes par service")

    # Liste unique des semaines disponibles
    unique_weeks = sorted(df_service['Week'].dropna().unique().astype(int))
    selected_week = st.selectbox("📆 Choisir une semaine :", unique_weeks)

    # Extraire les services de la semaine sélectionnée
    services_week = df_service[df_service['Week'] == selected_week]['LIBELLE_DEMANDEUR'].dropna().unique()

    st.markdown(f"### 🏥 Services ayant généré des analyses en semaine {selected_week}")

    if len(services_week) > 0:
        for s in services_week:
            st.write(f"🔹 {s}")
    else:
        st.info("Aucun service enregistré cette semaine.")

