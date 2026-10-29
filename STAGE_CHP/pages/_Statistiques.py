import streamlit as st
from database import get_patients
import pandas as pd
import plotly.express as px

if "user" not in st.session_state:
    st.warning("Veuillez vous connecter")
    st.stop()

st.title("Statistiques")

data = get_patients()

if not data:
    st.info("Aucun patient dans la base de données. Importez un fichier CSV depuis Import / Export.")
    st.stop()

df = pd.DataFrame(data, columns=[
    "ID", "Prénom", "Nom", "Age", "Genre", "Département", "Temps Attente", "Priorité"
])

# =========================================
# FILTRES GLOBAUX
# =========================================

st.subheader("Filtres")

col1, col2, col3 = st.columns(3)

with col1:
    priorites = ["Toutes"] + sorted(df["Priorité"].dropna().unique().tolist())
    filtre_priorite = st.selectbox("Priorité", priorites)

with col2:
    departements = ["Tous"] + sorted(df["Département"].dropna().unique().tolist())
    filtre_dept = st.selectbox("Département", departements)

with col3:
    genres = ["Tous"] + sorted(df["Genre"].dropna().unique().tolist())
    filtre_genre = st.selectbox("Genre", genres)

# Application des filtres
df_filtre = df.copy()

if filtre_priorite != "Toutes":
    df_filtre = df_filtre[df_filtre["Priorité"] == filtre_priorite]

if filtre_dept != "Tous":
    df_filtre = df_filtre[df_filtre["Département"] == filtre_dept]

if filtre_genre != "Tous":
    df_filtre = df_filtre[df_filtre["Genre"] == filtre_genre]

if df_filtre.empty:
    st.warning("Aucun patient ne correspond aux filtres sélectionnés.")
    st.stop()

st.markdown("---")

# =========================================
# MÉTRIQUES
# =========================================

st.subheader("Vue globale")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total patients", len(df_filtre))

col2.metric("Age moyen", f"{round(df_filtre['Age'].mean(), 1)} ans" if df_filtre['Age'].mean() > 0 else "N/A")

col3.metric("Attente moyenne",
    f"{round(df_filtre['Temps Attente'].mean(), 1)} min" if df_filtre['Temps Attente'].mean() > 0 else "N/A")

critiques = len(df_filtre[df_filtre["Priorité"].isin(["P1", "Critique"])])
col4.metric("Critiques", critiques)

urgents = len(df_filtre[df_filtre["Priorité"].isin(["P2", "Urgent"])])
col5.metric("Urgents", urgents)

st.markdown("---")

# =========================================
# PRIORITÉ
# =========================================

st.subheader("Répartition par priorité")

col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        df_filtre,
        names="Priorité",
        title="Répartition des priorités",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    priority_count = df_filtre["Priorité"].value_counts().reset_index()
    priority_count.columns = ["Priorité", "Patients"]
    fig_bar_prio = px.bar(
        priority_count,
        x="Priorité",
        y="Patients",
        title="Nombre de patients par priorité",
        text_auto=True,
        color="Priorité"
    )
    st.plotly_chart(fig_bar_prio, use_container_width=True)

st.markdown("---")

# =========================================
# AGE
# =========================================

if df_filtre["Age"].sum() > 0:
    st.subheader("Distribution des âges")

    col1, col2 = st.columns(2)

    with col1:
        fig_hist = px.histogram(
            df_filtre,
            x="Age",
            nbins=20,
            title="Distribution des âges"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        fig_box_age = px.box(
            df_filtre,
            y="Age",
            color="Priorité",
            title="Age par priorité"
        )
        st.plotly_chart(fig_box_age, use_container_width=True)

    st.markdown("---")

# =========================================
# TEMPS D'ATTENTE
# =========================================

if df_filtre["Temps Attente"].sum() > 0:
    st.subheader("Temps d'attente")

    col1, col2 = st.columns(2)

    with col1:
        fig_box = px.box(
            df_filtre,
            y="Temps Attente",
            color="Priorité",
            title="Temps d'attente par priorité"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col2:
        fig_hist_att = px.histogram(
            df_filtre,
            x="Temps Attente",
            nbins=20,
            title="Distribution du temps d'attente"
        )
        st.plotly_chart(fig_hist_att, use_container_width=True)

    st.markdown("---")

# =========================================
# DÉPARTEMENT
# =========================================

if df_filtre["Département"].nunique() > 1:
    st.subheader("Patients par département")

    col1, col2 = st.columns(2)

    with col1:
        dept_count = df_filtre["Département"].value_counts().reset_index()
        dept_count.columns = ["Département", "Patients"]
        fig_dept = px.bar(
            dept_count,
            x="Département",
            y="Patients",
            title="Patients par département",
            text_auto=True,
            color="Département"
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    with col2:
        fig_dept_pie = px.pie(
            df_filtre,
            names="Département",
            title="Répartition par département",
            hole=0.4
        )
        st.plotly_chart(fig_dept_pie, use_container_width=True)

    st.markdown("---")

# =========================================
# GENRE
# =========================================

if df_filtre["Genre"].nunique() > 1:
    st.subheader("Répartition par genre")

    col1, col2 = st.columns(2)

    with col1:
        genre_count = df_filtre["Genre"].value_counts().reset_index()
        genre_count.columns = ["Genre", "Patients"]
        fig_genre = px.bar(
            genre_count,
            x="Genre",
            y="Patients",
            title="Patients par genre",
            text_auto=True,
            color="Genre"
        )
        st.plotly_chart(fig_genre, use_container_width=True)

    with col2:
        fig_genre_pie = px.pie(
            df_filtre,
            names="Genre",
            title="Répartition par genre",
            hole=0.4
        )
        st.plotly_chart(fig_genre_pie, use_container_width=True)

    st.markdown("---")

# =========================================
# AGE VS TEMPS D'ATTENTE
# =========================================

if df_filtre["Age"].sum() > 0 and df_filtre["Temps Attente"].sum() > 0:
    st.subheader("Relation Age / Temps d'attente")

    fig_scatter = px.scatter(
        df_filtre,
        x="Age",
        y="Temps Attente",
        color="Priorité",
        size="Age",
        hover_data=["Prénom", "Nom", "Département"],
        title="Relation entre Age et Temps d'attente"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

# =========================================
# TABLEAU RÉCAPITULATIF
# =========================================

st.subheader("Tableau récapitulatif")

recap = pd.DataFrame({
    "Indicateur": [
        "Total patients",
        "Age moyen",
        "Age minimum",
        "Age maximum",
        "Attente moyenne (min)",
        "Attente maximum (min)",
        "Cas critiques",
        "Cas urgents"
    ],
    "Valeur": [
        len(df_filtre),
        round(df_filtre["Age"].mean(), 1) if df_filtre["Age"].sum() > 0 else "N/A",
        df_filtre["Age"].min() if df_filtre["Age"].sum() > 0 else "N/A",
        df_filtre["Age"].max() if df_filtre["Age"].sum() > 0 else "N/A",
        round(df_filtre["Temps Attente"].mean(), 1) if df_filtre["Temps Attente"].sum() > 0 else "N/A",
        df_filtre["Temps Attente"].max() if df_filtre["Temps Attente"].sum() > 0 else "N/A",
        len(df_filtre[df_filtre["Priorité"].isin(["P1", "Critique"])]),
        len(df_filtre[df_filtre["Priorité"].isin(["P2", "Urgent"])])
    ]
})

st.dataframe(recap, use_container_width=True)