import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

if "user" not in st.session_state:
    st.warning("Veuillez vous connecter")
    st.stop()

st.title("Analyse des donnees hospitalieres")

file = st.file_uploader("Importer un fichier CSV", type=["csv"])

if file is not None:

    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    st.success("Fichier charge avec succes")
    st.subheader("Apercu des donnees brutes")
    st.dataframe(df, use_container_width=True)
    st.markdown("---")

    # =========================================
    # MAPPING
    # =========================================

    mapping = {
        "age": "Age", "Age": "Age", "AGE": "Age",
        "Âge": "Age", "âge": "Age",
        "sexe": "Gender", "Sexe": "Gender",
        "genre": "Gender", "Genre": "Gender",
        "gender": "Gender",
        "provenance": "Department",
        "department": "Department", "Department": "Department",
        "departement": "Department", "Departement": "Department",
        "service": "Department", "Service": "Department",
        "triage_niveau": "Priority", "Triage_niveau": "Priority",
        "priority": "Priority", "Priority": "Priority",
        "priorite": "Priority", "Priorite": "Priority",
        "priorité": "Priority", "Priorité": "Priority",
        "temps_attente": "Waiting_Time",
        "waiting_time": "Waiting_Time",
        "temps attente": "Waiting_Time",
        "Temps Attente": "Waiting_Time",
        "attente": "Waiting_Time",
        "nom": "Nom", "Nom": "Nom",
        "prenom": "Prenom", "Prenom": "Prenom",
        "prénom": "Prenom", "Prénom": "Prenom",
    }

    df = df.rename(columns=mapping)
    colonnes_disponibles = ["Aucune"] + df.columns.tolist()
    st.markdown("---")

    # =========================================
    # GESTION COLONNE AGE
    # =========================================

    has_age = "Age" in df.columns and df["Age"].sum() > 0

    if not has_age:
        st.warning("La colonne Age n'existe pas dans votre fichier. Que voulez-vous faire ?")
        choix_age = st.radio(
            "Choisir une option pour Age",
            [
                "Ignorer cette colonne",
                "Entrer une valeur par defaut pour tous",
                "Choisir une autre colonne de mon fichier"
            ],
            key="choix_age"
        )

        if choix_age == "Ignorer cette colonne":
            df["Age"] = 0
            has_age = False

        elif choix_age == "Entrer une valeur par defaut pour tous":
            val_age = st.number_input("Age par defaut", min_value=0, max_value=120, value=30)
            df["Age"] = val_age
            has_age = True

        elif choix_age == "Choisir une autre colonne de mon fichier":
            col_age = st.selectbox("Colonne pour Age", colonnes_disponibles, key="col_age")
            if col_age != "Aucune":
                df["Age"] = pd.to_numeric(df[col_age], errors="coerce").fillna(0)
                has_age = True
            else:
                st.warning("Veuillez choisir une colonne ou selectionner une autre option.")
                df["Age"] = 0
                has_age = False
                st.stop()

    # =========================================
    # GESTION COLONNE TEMPS ATTENTE
    # =========================================

    has_waiting = "Waiting_Time" in df.columns and df["Waiting_Time"].sum() > 0

    if not has_waiting:
        st.warning("La colonne Temps d'attente n'existe pas dans votre fichier. Que voulez-vous faire ?")
        choix_att = st.radio(
            "Choisir une option pour Temps d'attente",
            [
                "Ignorer cette colonne",
                "Entrer une valeur par defaut pour tous",
                "Choisir une autre colonne de mon fichier"
            ],
            key="choix_att"
        )

        if choix_att == "Ignorer cette colonne":
            df["Waiting_Time"] = 0
            has_waiting = False

        elif choix_att == "Entrer une valeur par defaut pour tous":
            val_att = st.number_input("Temps d'attente par defaut (minutes)", min_value=0, max_value=600, value=30)
            df["Waiting_Time"] = val_att
            has_waiting = True

        elif choix_att == "Choisir une autre colonne de mon fichier":
            col_att = st.selectbox("Colonne pour Temps d'attente", colonnes_disponibles, key="col_att")
            if col_att != "Aucune":
                df["Waiting_Time"] = pd.to_numeric(df[col_att], errors="coerce").fillna(0)
                has_waiting = True
            else:
                st.warning("Veuillez choisir une colonne ou selectionner une autre option.")
                df["Waiting_Time"] = 0
                has_waiting = False
                st.stop()

    # =========================================
    # GESTION COLONNE GENRE
    # =========================================

    has_gender = "Gender" in df.columns

    if not has_gender:
        st.warning("La colonne Genre n'existe pas dans votre fichier. Que voulez-vous faire ?")
        choix_gender = st.radio(
            "Choisir une option pour Genre",
            [
                "Ignorer cette colonne",
                "Entrer une valeur par defaut pour tous",
                "Choisir une autre colonne de mon fichier"
            ],
            key="choix_gender"
        )

        if choix_gender == "Ignorer cette colonne":
            df["Gender"] = "Non renseigne"
            has_gender = False

        elif choix_gender == "Entrer une valeur par defaut pour tous":
            val_gender = st.selectbox("Genre par defaut", ["Homme", "Femme", "Non renseigne"])
            df["Gender"] = val_gender
            has_gender = True

        elif choix_gender == "Choisir une autre colonne de mon fichier":
            col_gender = st.selectbox("Colonne pour Genre", colonnes_disponibles, key="col_gender")
            if col_gender != "Aucune":
                df["Gender"] = df[col_gender]
                has_gender = True
            else:
                st.warning("Veuillez choisir une colonne ou selectionner une autre option.")
                df["Gender"] = "Non renseigne"
                has_gender = False
                st.stop()

    # =========================================
    # GESTION COLONNE DEPARTEMENT
    # =========================================

    has_dept = "Department" in df.columns

    if not has_dept:
        st.warning("La colonne Departement n'existe pas dans votre fichier. Que voulez-vous faire ?")
        choix_dept = st.radio(
            "Choisir une option pour Departement",
            [
                "Ignorer cette colonne",
                "Entrer une valeur par defaut pour tous",
                "Choisir une autre colonne de mon fichier"
            ],
            key="choix_dept"
        )

        if choix_dept == "Ignorer cette colonne":
            df["Department"] = "Non renseigne"
            has_dept = False

        elif choix_dept == "Entrer une valeur par defaut pour tous":
            val_dept = st.text_input("Departement par defaut", "Urgences")
            df["Department"] = val_dept
            has_dept = True

        elif choix_dept == "Choisir une autre colonne de mon fichier":
            col_dept = st.selectbox("Colonne pour Departement", colonnes_disponibles, key="col_dept")
            if col_dept != "Aucune":
                df["Department"] = df[col_dept]
                has_dept = True
            else:
                st.warning("Veuillez choisir une colonne ou selectionner une autre option.")
                df["Department"] = "Non renseigne"
                has_dept = False
                st.stop()

    # =========================================
    # GESTION COLONNE PRIORITE
    # =========================================

    has_priority = "Priority" in df.columns

    if not has_priority:
        st.warning("La colonne Priorite n'existe pas dans votre fichier. Que voulez-vous faire ?")
        choix_prio = st.radio(
            "Choisir une option pour Priorite",
            [
                "Ignorer cette colonne",
                "Entrer une valeur par defaut pour tous",
                "Choisir une autre colonne de mon fichier",
                "Calculer automatiquement depuis Age et Temps d'attente"
            ],
            key="choix_prio"
        )

        if choix_prio == "Ignorer cette colonne":
            df["Priority"] = "Normal"
            has_priority = False

        elif choix_prio == "Entrer une valeur par defaut pour tous":
            val_prio = st.selectbox("Priorite par defaut", ["Normal", "Urgent", "Critique"])
            df["Priority"] = val_prio
            has_priority = True

        elif choix_prio == "Choisir une autre colonne de mon fichier":
            col_prio = st.selectbox("Colonne pour Priorite", colonnes_disponibles, key="col_prio")
            if col_prio != "Aucune":
                df["Priority"] = df[col_prio]
                has_priority = True
            else:
                st.warning("Veuillez choisir une colonne ou selectionner une autre option.")
                df["Priority"] = "Normal"
                has_priority = False
                st.stop()

        elif choix_prio == "Calculer automatiquement depuis Age et Temps d'attente":
            def local_priority(age, waiting_time):
                if age > 65 or waiting_time > 120:
                    return "Critique"
                elif waiting_time > 60:
                    return "Urgent"
                else:
                    return "Normal"
            df["Priority"] = df.apply(
                lambda x: local_priority(x["Age"], x["Waiting_Time"]), axis=1
            )
            has_priority = True
            st.success("Priorite calculee automatiquement depuis Age et Temps d'attente")

    else:
        def convert_priority(p):
            p = str(p).strip()
            if "P1" in p or "Critique" in p or "critique" in p:
                return "Critique"
            elif "P2" in p or "Urgent" in p or "urgent" in p:
                return "Urgent"
            elif "P3" in p:
                return "Semi-urgent"
            else:
                return "Normal"
        df["Priority"] = df["Priority"].apply(convert_priority)

    st.markdown("---")

    # =========================================
    # SCORE DE RISQUE
    # =========================================

    def risk_score(age, waiting_time, priority):
        score = 0
        if age > 65:
            score += 40
        elif age > 40:
            score += 20
        if waiting_time > 120:
            score += 40
        elif waiting_time > 60:
            score += 20
        if priority == "Critique":
            score += 30
        elif priority == "Urgent":
            score += 15
        return score

    df["Risk_Score"] = df.apply(
        lambda x: risk_score(x["Age"], x["Waiting_Time"], x["Priority"]), axis=1
    )

    def risk_level(score):
        if score >= 70:
            return "Risque Eleve"
        elif score >= 40:
            return "Risque Moyen"
        else:
            return "Risque Faible"

    df["Risk_Level"] = df["Risk_Score"].apply(risk_level)

    # =========================================
    # KPI
    # =========================================

    st.subheader("Indicateurs hospitaliers")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total patients", len(df))
    col2.metric("Age moyen", round(df["Age"].mean(), 1) if has_age else "—")
    col3.metric("Attente moyenne", f"{round(df['Waiting_Time'].mean(), 1)} min" if has_waiting else "—")
    col4.metric("Cas critiques", len(df[df["Priority"] == "Critique"]))

    st.markdown("---")

    # =========================================
    # ALERTES ADAPTATIVES
    # =========================================

    st.subheader("Analyse automatique")

    risque_eleve  = len(df[df["Risk_Level"] == "Risque Eleve"])
    risque_moyen  = len(df[df["Risk_Level"] == "Risque Moyen"])
    cas_critiques = len(df[df["Priority"] == "Critique"])
    cas_urgents   = len(df[df["Priority"] == "Urgent"])

    if risque_eleve > 5:
        st.error(f"ALERTE CRITIQUE : {risque_eleve} patients a risque eleve — renforcement du personnel recommande.")
    elif risque_eleve > 0:
        st.warning(f"Attention : {risque_eleve} patient(s) a risque eleve — surveillance immediate recommandee.")
    elif risque_moyen > 5:
        st.warning(f"Attention : {risque_moyen} patients a risque moyen — surveillance renforcee recommandee.")
    else:
        st.success("Situation hospitaliere stable — aucun risque eleve detecte.")

    if has_priority:
        if cas_critiques > 0:
            st.error(f"{cas_critiques} cas critique(s) detecte(s) — prise en charge immediate requise.")
        if cas_urgents > 0:
            st.warning(f"{cas_urgents} cas urgent(s) en attente de prise en charge.")
    else:
        st.info("Alerte priorite non disponible — colonne Priorite absente du fichier.")

    if has_waiting:
        attente_elevee   = len(df[df["Waiting_Time"] > 60])
        attente_critique = len(df[df["Waiting_Time"] > 120])
        if attente_critique > 0:
            st.error(f"{attente_critique} patient(s) attendent depuis plus de 120 minutes — situation critique.")
        elif attente_elevee > 0:
            st.warning(f"{attente_elevee} patient(s) attendent depuis plus de 60 minutes.")
        else:
            st.success("Temps d'attente dans les normes pour tous les patients.")
    else:
        st.info("Alerte temps d'attente non disponible — colonne Temps Attente absente du fichier.")

    if has_age:
        patients_ages = len(df[df["Age"] > 65])
        if patients_ages > 0:
            st.warning(f"{patients_ages} patient(s) de plus de 65 ans — necessite une attention particuliere.")
    else:
        st.info("Alerte age non disponible — colonne Age absente du fichier.")

    st.markdown("---")

    # =========================================
    # FIABILITE DU SCORE
    # =========================================

    st.subheader("Fiabilite du score de risque")

    criteres_utilises  = []
    criteres_manquants = []

    if has_age:
        criteres_utilises.append("Age")
    else:
        criteres_manquants.append("Age")

    if has_waiting:
        criteres_utilises.append("Temps d'attente")
    else:
        criteres_manquants.append("Temps d'attente")

    if has_priority:
        criteres_utilises.append("Priorite")
    else:
        criteres_manquants.append("Priorite")

    if len(criteres_manquants) == 0:
        st.success(f"Score calcule sur 3 criteres : {', '.join(criteres_utilises)} — fiabilite maximale (100%).")
    elif len(criteres_manquants) == 1:
        st.warning(f"Score calcule sur 2 criteres : {', '.join(criteres_utilises)}. Critere manquant : {criteres_manquants[0]} — fiabilite reduite (66%).")
    elif len(criteres_manquants) == 2:
        st.warning(f"Score calcule sur 1 critere : {', '.join(criteres_utilises)}. Criteres manquants : {', '.join(criteres_manquants)} — fiabilite faible (33%).")
    else:
        st.error("Aucun critere disponible — score de risque non calculable.")

    st.markdown("---")

    # =========================================
    # GRAPHIQUES — PRIORITE
    # =========================================

    st.subheader("Repartition des priorites")

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(df, names="Priority", title="Repartition des priorites",
                         hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        priority_count = df["Priority"].value_counts().reset_index()
        priority_count.columns = ["Priority", "Patients"]
        fig_bar_prio = px.bar(priority_count, x="Priority", y="Patients",
                              title="Patients par priorite", text_auto=True, color="Priority")
        st.plotly_chart(fig_bar_prio, use_container_width=True)

    st.markdown("---")

    # =========================================
    # GRAPHIQUES — AGE
    # =========================================

    if has_age:
        st.subheader("Distribution des ages")
        col1, col2 = st.columns(2)
        with col1:
            fig_age = px.histogram(df, x="Age", nbins=20, title="Distribution des ages",
                                   color_discrete_sequence=["#0b3d91"])
            st.plotly_chart(fig_age, use_container_width=True)
        with col2:
            fig_box_age = px.box(df, y="Age", color="Priority", title="Age par priorite")
            st.plotly_chart(fig_box_age, use_container_width=True)
        st.markdown("---")
    else:
        st.info("Graphiques Age non affiches — colonne Age ignoree.")
        st.markdown("---")

    # =========================================
    # GRAPHIQUES — TEMPS ATTENTE
    # =========================================

    if has_waiting:
        st.subheader("Temps d'attente")
        col1, col2 = st.columns(2)
        with col1:
            fig_box_att = px.box(df, y="Waiting_Time", color="Priority",
                                 title="Temps d'attente par priorite")
            st.plotly_chart(fig_box_att, use_container_width=True)
        with col2:
            fig_hist_att = px.histogram(df, x="Waiting_Time", nbins=20,
                                        title="Distribution du temps d'attente",
                                        color_discrete_sequence=["#0b3d91"])
            st.plotly_chart(fig_hist_att, use_container_width=True)
        st.markdown("---")
    else:
        st.info("Graphiques Temps d'attente non affiches — colonne ignoree.")
        st.markdown("---")

    # =========================================
    # GRAPHIQUES — DEPARTEMENT
    # =========================================

    if has_dept and df["Department"].nunique() > 1:
        st.subheader("Patients par departement")
        col1, col2 = st.columns(2)
        with col1:
            dept_count = df["Department"].value_counts().reset_index()
            dept_count.columns = ["Department", "Patients"]
            fig_dept = px.bar(dept_count, x="Department", y="Patients",
                              title="Patients par departement", text_auto=True,
                              color="Patients", color_continuous_scale="Blues")
            st.plotly_chart(fig_dept, use_container_width=True)
        with col2:
            fig_dept_pie = px.pie(df, names="Department",
                                  title="Repartition par departement", hole=0.4)
            st.plotly_chart(fig_dept_pie, use_container_width=True)
        st.markdown("---")
    else:
        st.info("Graphiques Departement non affiches — colonne ignoree.")
        st.markdown("---")

    # =========================================
    # GRAPHIQUES — GENRE
    # =========================================

    if has_gender and df["Gender"].nunique() > 1:
        st.subheader("Repartition par genre")
        col1, col2 = st.columns(2)
        with col1:
            gender_count = df["Gender"].value_counts().reset_index()
            gender_count.columns = ["Gender", "Patients"]
            fig_gender = px.bar(gender_count, x="Gender", y="Patients",
                                title="Patients par genre", text_auto=True,
                                color_discrete_sequence=["#0b3d91", "#4a90d9"])
            st.plotly_chart(fig_gender, use_container_width=True)
        with col2:
            fig_gender_pie = px.pie(df, names="Gender", title="Repartition par genre",
                                    hole=0.4, color_discrete_sequence=["#0b3d91", "#4a90d9"])
            st.plotly_chart(fig_gender_pie, use_container_width=True)
        st.markdown("---")
    else:
        st.info("Graphiques Genre non affiches — colonne ignoree.")
        st.markdown("---")

    # =========================================
    # GRAPHIQUES — AGE VS ATTENTE
    # =========================================

    if has_age and has_waiting:
        st.subheader("Relation Age / Temps d'attente")
        fig_scatter = px.scatter(
            df, x="Age", y="Waiting_Time", color="Priority",
            trendline="ols", title="Relation entre age et temps d'attente",
            hover_data=["Nom", "Prenom"] if "Nom" in df.columns else None
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("---")
    else:
        st.info("Graphique Relation Age/Attente non affiche — donnees insuffisantes.")
        st.markdown("---")

    # =========================================
    # GRAPHIQUES — RISQUE
    # =========================================

    st.subheader("Analyse des risques")

    col1, col2 = st.columns(2)

    with col1:
        risk_count = df["Risk_Level"].value_counts().reset_index()
        risk_count.columns = ["Niveau", "Patients"]
        fig_risk = px.bar(risk_count, x="Niveau", y="Patients", color="Niveau",
                          text_auto=True, title="Niveaux de risque",
                          color_discrete_map={
                              "Risque Eleve": "#dc2626",
                              "Risque Moyen": "#ea580c",
                              "Risque Faible": "#16a34a"
                          })
        st.plotly_chart(fig_risk, use_container_width=True)

    with col2:
        fig_risk_pie = px.pie(df, names="Risk_Level",
                              title="Repartition des niveaux de risque", hole=0.4,
                              color_discrete_map={
                                  "Risque Eleve": "#dc2626",
                                  "Risque Moyen": "#ea580c",
                                  "Risque Faible": "#16a34a"
                              })
        st.plotly_chart(fig_risk_pie, use_container_width=True)

    st.markdown("---")

    # =========================================
    # TABLEAU RECAP
    # =========================================

    st.subheader("Tableau recapitulatif")

    recap = {
        "Indicateur": [
            "Total patients", "Cas critiques", "Cas urgents",
            "Risque eleve", "Risque moyen", "Risque faible"
        ],
        "Valeur": [
            len(df),
            len(df[df["Priority"] == "Critique"]),
            len(df[df["Priority"] == "Urgent"]),
            len(df[df["Risk_Level"] == "Risque Eleve"]),
            len(df[df["Risk_Level"] == "Risque Moyen"]),
            len(df[df["Risk_Level"] == "Risque Faible"])
        ]
    }

    if has_age:
        recap["Indicateur"] += ["Age moyen", "Age minimum", "Age maximum"]
        recap["Valeur"] += [round(df["Age"].mean(), 1), df["Age"].min(), df["Age"].max()]

    if has_waiting:
        recap["Indicateur"] += ["Attente moyenne (min)", "Attente maximum (min)"]
        recap["Valeur"] += [round(df["Waiting_Time"].mean(), 1), df["Waiting_Time"].max()]

    st.dataframe(pd.DataFrame(recap), use_container_width=True)

    st.markdown("---")

    # =========================================
    # RAPPORT PDF
    # =========================================

    st.subheader("Generer un rapport PDF")

    if st.button("Telecharger le rapport PDF"):

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(tmp_file.name, pagesize=letter)
        width, height = letter

        c.setFillColorRGB(0.04, 0.24, 0.57)
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "Rapport des Urgences Hospitalieres")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 68, f"Genere par : {st.session_state['user']}")

        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 110, "Indicateurs principaux")

        c.setFont("Helvetica", 12)
        y = height - 135
        c.drawString(50, y, f"Total patients      : {len(df)}")
        y -= 20
        if has_age:
            c.drawString(50, y, f"Age moyen           : {round(df['Age'].mean(), 1)} ans")
            y -= 20
        if has_waiting:
            c.drawString(50, y, f"Attente moyenne     : {round(df['Waiting_Time'].mean(), 1)} min")
            y -= 20
        c.drawString(50, y, f"Cas critiques       : {len(df[df['Priority'] == 'Critique'])}")
        y -= 20
        c.drawString(50, y, f"Cas urgents         : {len(df[df['Priority'] == 'Urgent'])}")
        y -= 20
        c.drawString(50, y, f"Risque eleve        : {len(df[df['Risk_Level'] == 'Risque Eleve'])}")
        y -= 20
        c.drawString(50, y, f"Risque moyen        : {len(df[df['Risk_Level'] == 'Risque Moyen'])}")
        y -= 20
        c.drawString(50, y, f"Risque faible       : {len(df[df['Risk_Level'] == 'Risque Faible'])}")
        y -= 40

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Recommandations")
        y -= 25
        c.setFont("Helvetica", 12)

        if cas_critiques > 5:
            c.setFillColorRGB(0.86, 0.15, 0.15)
            c.drawString(50, y, f"ALERTE : {cas_critiques} cas critiques — renforcement personnel requis.")
        elif cas_critiques > 0:
            c.setFillColorRGB(0.92, 0.36, 0.05)
            c.drawString(50, y, f"Attention : {cas_critiques} cas critique(s) en cours.")
        else:
            c.setFillColorRGB(0.09, 0.64, 0.29)
            c.drawString(50, y, "Situation stable — aucun cas critique detecte.")

        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.setFont("Helvetica", 9)
        c.drawString(50, 30, "Systeme de Gestion des Urgences Hospitalieres — Document confidentiel")

        c.save()

        with open(tmp_file.name, "rb") as f:
            st.download_button(
                label="Telecharger le rapport PDF",
                data=f,
                file_name="rapport_urgences.pdf",
                mime="application/pdf"
            )

else:
    st.info("Importez un fichier CSV pour commencer l'analyse")