import streamlit as st
import json
import random
from pathlib import Path

# -----------------------------
# Configuration générale
# -----------------------------
st.set_page_config(
    page_title="Coach entretien actuariat",
    layout="wide"
)

DATA_DIR = Path(__file__).parent

# -----------------------------
# Fonctions utilitaires
# -----------------------------
@st.cache_data
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_random_question(block):
    """Format: questions classiques (projets ou brain-teasers)."""
    if isinstance(block, list):
        if not block:
            return None
        return random.choice(block)

    questions = block.get("questions", [])
    if not questions:
        return None
    return random.choice(questions)


def pick_random_culture(culture_dict):
    """
    Pour culture-G-actuariat.json
    Structure :
      { "theme": "...", "description": "...", "blocs": [ {...}, ... ] }
    On renvoie un (bloc, section) aléatoire.
    """
    blocs = culture_dict.get("blocs", [])
    if not blocs:
        return None, None

    bloc = random.choice(blocs)
    sections = bloc.get("sections", [])
    if not sections:
        return bloc, None

    section = random.choice(sections)
    return bloc, section


# -----------------------------
# Mapping fichiers
# -----------------------------
projets_files = {
    "Tarification auto – GLM Poisson": "Tarification-auto-GLM-Poisson-application-Streamlit.json",
    "Provisionnement Non-Vie – Triangle de développement": "Provisionnement_Non-Vie_Triangle_de_développement_Chain_Ladder.json",
    "Analyse gestion d'actifs / SFCR": "analyse-gestion-actifs-sfcr.json",
    "Détection de fraude": "detection-fraude.json",
}

culture_file = "culture-G-actuariat.json"
brain_file = "brain-teaser.json"

# -----------------------------
# Interface
# -----------------------------
st.title("Coach d’entretien actuarial – Pamela")

st.markdown(
"""
Application personnelle pour réviser **mes projets**, la **culture actuariat**
et les **brain-teasers** d’entretien.

Conseil d’utilisation :
1. Choisir un onglet (Projet, Culture, Brain-teaser).
2. Laisser l’app poser une question.
3. Répondre **à voix haute**, puis comparer avec les éléments de réponse.
"""
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Mes projets", "Culture actuariat", "Brain-teasers", "Session 10 minutes"]
)


# -----------------------------
# Onglet 1 : Projets
# -----------------------------
with tab1:
    st.subheader("Questions sur mes projets")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        projet_nom = st.selectbox("Choisir un projet", list(projets_files.keys()))
        data_projet = load_json(DATA_DIR / projets_files[projet_nom])

        st.markdown(f"**Titre :** {data_projet.get('titre', projet_nom)}")
        desc = data_projet.get("description", "")
        if desc:
            st.write(desc)

        st.markdown("**Objectif de ce bloc :** être capable d’expliquer le projet en 1 minute, puis de répondre à des questions de détail (méthode, difficultés, résultats).")

        if st.button("Question sur ce projet"):
            q = pick_random_question(data_projet)
            st.session_state["last_project_question"] = q

    with col_right:
        q = st.session_state.get("last_project_question")
        if q:
            st.markdown("### Question")
            st.write(q["question"])

            with st.expander("Afficher une réponse possible"):
                st.write(q.get("reponse", ""))
        else:
            st.info("Clique sur « Question sur ce projet » pour commencer.")

# -----------------------------
# Onglet 2 : Culture actuariat
# -----------------------------
with tab2:
    st.subheader("Culture générale actuariat / réglementation")

    data_culture = load_json(DATA_DIR / culture_file)

    st.markdown(
    """
    Ici tu révises les notions type **Solvabilité II, IFRS, SCR, MCR, provisions, ALM**, etc.
    Objectif : donner une **définition simple**, expliquer **pourquoi c’est important**
    et donner **un exemple**.
    """
    )

    col1, col2 = st.columns([1,2])

    with col1:
        if st.button("Nouvelle question de culture", key="btn_culture"):
            q = pick_random_question(data_culture)
            st.session_state["last_culture_question"] = q

    with col2:
        q = st.session_state.get("last_culture_question")
        if q:
            st.markdown("### Question")
            st.write(q["question"])
            with st.expander("Afficher une réponse possible"):
                st.write(q.get("reponse", ""))
        else:
            st.info("Clique sur « Nouvelle question de culture ».")

# -----------------------------
# Onglet 3 : Brain-teasers
# -----------------------------
with tab3:
    st.subheader("Brain-teasers / petites questions logiques")

    data_brain = load_json(DATA_DIR / brain_file)

    st.markdown(
    """
    Ici tu t'entraînes sur les questions de raisonnement / logique.
    Objectif : structurer ta réponse, expliquer ton raisonnement étape par étape,
    même si tu n’es pas sûre du résultat.
    """
    )

    col1, col2 = st.columns([1,2])

    with col1:
        if st.button("Nouvelle question brain-teaser", key="btn_brain"):
            q = pick_random_question(data_brain)
            st.session_state["last_brain_question"] = q

    with col2:
        q = st.session_state.get("last_brain_question")
        if q:
            st.markdown("### Question")
            st.write(q["question"])
            with st.expander("Afficher une piste de réponse"):
                st.write(q.get("reponse", ""))
        else:
            st.info("Clique sur « Nouvelle question brain-teaser ».")

# -----------------------------
# Onglet 4 : Session 10 minutes
# -----------------------------
with tab4:
    st.subheader("Session mixte 10 minutes")

    st.markdown(
    """
    Cette session alterne **projets**, **culture actuariat** et **brain-teasers**.
    Idéal pour simuler un entretien : tu dois répondre à tout ce qui vient.

    1. Clique sur « Nouvelle question ».
    2. Réponds à voix haute (tu peux te chronométrer 1–2 minutes).
    3. Ouvre les éléments de réponse pour vérifier.
    """
    )

    mode = st.selectbox(
        "Type de questions à inclure",
        ["Mixte (tout)", "Projets uniquement", "Culture uniquement", "Brain-teasers uniquement"],
    )

    # Préparer les pools
    questions_pool = []

    if mode in ("Mixte (tout)", "Projets uniquement"):
        for fname in projets_files.values():
            d = load_json(DATA_DIR / fname)
            for q in d.get("questions", []):
                questions_pool.append(("Projet", q))

    if mode in ("Mixte (tout)", "Culture uniquement"):
        d_culture = load_json(DATA_DIR / culture_file)
        for q in d_culture.get("questions", []):
            questions_pool.append(("Culture", q))

    if mode in ("Mixte (tout)", "Brain-teasers uniquement"):
        d_brain = load_json(DATA_DIR / brain_file)
        for q in d_brain.get("questions", []):
            questions_pool.append(("Brain-teaser", q))

    if st.button("Nouvelle question mixte"):
        if questions_pool:
            cat, q = random.choice(questions_pool)
            st.session_state["last_mix_question"] = (cat, q)
        else:
            st.warning("Aucune question disponible (vérifie tes fichiers JSON).")

    last = st.session_state.get("last_mix_question")
    if last:
        cat, q = last
        st.markdown(f"**Catégorie : {cat}**")
        st.markdown("### Question")
        st.write(q["question"])
        with st.expander("Afficher une réponse possible"):
            st.write(q.get("reponse", ""))
    else:
        st.info("Clique sur « Nouvelle question mixte » pour commencer.")



