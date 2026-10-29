import streamlit as st
from database import create_table, get_patients
from auth import login, logout, is_logged_in
import pandas as pd
import plotly.express as px
import os

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Urgences Hospitalières",
    layout="wide"
)

create_table()

# ======================
# CHARGER LE STYLE CSS
# ======================
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ======================
# LOGIN
# ======================
login()

if is_logged_in():

    # ======================
    # HEADER
    # ======================
    st.title("Systeme de Gestion des Urgences")
    st.markdown(f"Bienvenue **{st.session_state['user']}** — Role : **{st.session_state['role']}**")

    # ======================
    # SIDEBAR
    # ======================
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")
    st.sidebar.success(f"Connecte : {st.session_state['user']}")
    st.sidebar.info(f"Role : {st.session_state['role']}")
    st.sidebar.markdown("---")
    logout()

    # ======================
    # DONNEES
    # ======================
    data = get_patients()

    st.markdown("---")

    # ======================
    # CAS : AUCUN PATIENT
    # ======================
    if not data:

        st.subheader("Tableau de bord")

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total patients", "0")
        col2.metric("Critiques", "0")
        col3.metric("Urgents", "0")
        col4.metric("Age moyen", "—")
        col5.metric("Attente moyenne", "—")

        st.markdown("---")
        st.warning("Aucun patient dans la base de donnees.")
        st.info("Allez sur Import Export pour importer un fichier CSV.")

    # ======================
    # CAS : PATIENTS EXISTANTS
    # ======================
    else:

        df = pd.DataFrame(data, columns=[
            "ID", "Prenom", "Nom", "Age", "Genre",
            "Departement", "Temps Attente", "Priorite"
        ])

        critiques = len(df[df["Priorite"].isin(["P1", "Critique"])])
        urgents   = len(df[df["Priorite"].isin(["P2", "Urgent"])])
        normaux   = len(df[df["Priorite"].isin(["P3", "P4", "Normal"])])
        age_moy   = round(df["Age"].mean(), 1) if df["Age"].sum() > 0 else 0
        att_moy   = round(df["Temps Attente"].mean(), 1) if df["Temps Attente"].sum() > 0 else 0

        # ======================
        # METRIQUES
        # ======================
        st.subheader("Tableau de bord")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "Total patients",
            len(df)
        )
        col2.metric(
            "Critiques (P1)",
            critiques,
            delta=f"{round(critiques/len(df)*100, 1)}%" if len(df) > 0 else None
        )
        col3.metric(
            "Urgents (P2)",
            urgents,
            delta=f"{round(urgents/len(df)*100, 1)}%" if len(df) > 0 else None
        )
        col4.metric(
            "Age moyen",
            f"{age_moy} ans" if age_moy > 0 else "—"
        )
        col5.metric(
            "Attente moyenne",
            f"{att_moy} min" if att_moy > 0 else "—"
        )

        st.markdown("---")

        # ======================
        # ALERTES
        # ======================
        if critiques > 5:
            st.error(f"ALERTE : {critiques} cas critiques detectes — renforcement du personnel recommande.")
        elif critiques > 0:
            st.warning(f"Attention : {critiques} cas critique(s) en cours de prise en charge.")
        else:
            st.success("Situation stable — aucun cas critique detecte.")

        st.markdown("---")

        # ======================
        # GRAPHIQUES
        # ======================
        st.subheader("Apercu rapide")

        col1, col2, col3 = st.columns(3)

        with col1:
            fig_pie = px.pie(
                df,
                names="Priorite",
                title="Repartition par priorite",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            dept_count = df["Departement"].value_counts().reset_index()
            dept_count.columns = ["Departement", "Patients"]
            fig_dept = px.bar(
                dept_count,
                x="Departement",
                y="Patients",
                title="Patients par departement",
                text_auto=True,
                color="Patients",
                color_continuous_scale="Blues"
            )
            fig_dept.update_layout(
                margin=dict(t=40, b=0, l=0, r=0),
                showlegend=False
            )
            st.plotly_chart(fig_dept, use_container_width=True)

        with col3:
            genre_count = df["Genre"].value_counts().reset_index()
            genre_count.columns = ["Genre", "Patients"]
            fig_genre = px.pie(
                genre_count,
                names="Genre",
                title="Repartition par genre",
                hole=0.4,
                color_discrete_sequence=["#0b3d91", "#4a90d9"]
            )
            fig_genre.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_genre, use_container_width=True)

        st.markdown("---")

        # ======================
        # RESUME PAR PRIORITE
        # ======================
        st.subheader("Resume par priorite")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div style='background:#fee2e2;border-left:5px solid #dc2626;
                border-radius:8px;padding:14px;'>
                <h4 style='color:#dc2626;margin:0'>Critiques (P1)</h4>
                <p style='font-size:2rem;font-weight:bold;color:#dc2626;margin:4px 0'>{critiques}</p>
                <p style='color:#7f1d1d;margin:0'>Prise en charge immediate</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style='background:#ffedd5;border-left:5px solid #ea580c;
                border-radius:8px;padding:14px;'>
                <h4 style='color:#ea580c;margin:0'>Urgents (P2)</h4>
                <p style='font-size:2rem;font-weight:bold;color:#ea580c;margin:4px 0'>{urgents}</p>
                <p style='color:#7c2d12;margin:0'>Prise en charge rapide</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div style='background:#dcfce7;border-left:5px solid #16a34a;
                border-radius:8px;padding:14px;'>
                <h4 style='color:#16a34a;margin:0'>Normaux (P3/P4)</h4>
                <p style='font-size:2rem;font-weight:bold;color:#16a34a;margin:4px 0'>{normaux}</p>
                <p style='color:#14532d;margin:0'>Situation stable</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ======================
        # DERNIERS PATIENTS
        # ======================
        st.subheader("10 derniers patients ajoutes")

        st.dataframe(
            df.sort_values("ID", ascending=False).head(10),
            use_container_width=True
        )

        st.markdown("---")

        # ======================
        # EXPORT RAPIDE
        # ======================
        st.subheader("Export rapide")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Telecharger tous les patients (CSV)",
            data=csv,
            file_name="patients_export.csv",
            mime="text/csv"
        )

else:
    st.markdown("""
    <div style='text-align:center; padding:60px 20px;'>
        <h2 style='color:#0b3d91;'>Systeme de Gestion des Urgences Hospitalieres</h2>
        <p style='color:#6b7280; font-size:1.1rem;'>
            Veuillez vous connecter depuis le menu a gauche pour acceder au systeme.
        </p>
    </div>
    """, unsafe_allow_html=True)