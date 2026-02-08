import streamlit as st
import json
import random
from pathlib import Path

st.set_page_config(page_title="Coach entretien actuariat", layout="wide")

DATA_DIR = Path(__file__).parent

@st.cache_data
def load_json(path):
    """Charge un fichier JSON avec gestion d'erreur."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Fichier non trouvé : {path}")
        return {}
    except json.JSONDecodeError:
        st.error(f"Erreur JSON dans : {path}")
        return {}

def pick_random_question(block):
    """Fonction universelle pour TOUS tes formats de JSON."""
    if isinstance(block, list):
        if not block:
            return None
        return random.choice(block)
    
    # Chercher la liste de questions sous différents noms
    possible_keys = ["questions", "questionsentretiens"]
    for key in possible_keys:
        if key in block:
            questions = block[key]
            if questions:
                return random.choice(questions)
    
    return None

def pick_culture_block(data_culture):
    """Pour culture-G-actuariat.json spécifique."""
    blocs = data_culture.get("blocs", [])
    if not blocs:
        return None, None
    bloc = random.choice(blocs)
    sections = bloc.get("sections", [])
    section = random.choice(sections) if sections else None
    return bloc, section

def get_reponse(q):
    """Récupère la réponse sous tous les formats possibles."""
    return (q.get("reponse", "") or 
            q.get("reponse_courte", "") or 
            q.get("resume", "") or 
            q.get("reponse_textuelle", "") or 
            q.get("reponse_numerique", "") or "")

# Mapping des projets (adapte aux vrais noms de fichiers dans ton repo GitHub)
projets_files = {
    "Tarification auto – GLM Poisson": "Tarification-auto-GLM-Poisson-application-Streamlit.json",
    "Provisionnement Non-Vie – Triangle": "Provisionnement_Non-Vie_Triangle_de_développement_Chain_Ladder.json",
    "Analyse gestion d'actifs / SFCR": "analyse-gestion-actifs-sfcr.json",
    "Détection de fraude": "detection-fraude.json",
}

culture_file = "culture-G-actuariat.json"
brain_file = "brain-teaser.json"

st.title("🤖 Coach entretien actuariat CFA")

tab1, tab2, tab3, tab4 = st.tabs(["Mes projets", "Culture G", "Brain teasers", "Session 10 min"])

# ============================================================================
# TAB 1 : MES PROJETS
# ============================================================================
with tab1:
    st.header("Questions sur mes projets")
    
    data_projets = {}
    for nom, fichier in projets_files.items():
        data_projets[nom] = load_json(DATA_DIR / fichier)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        projet_nom = st.selectbox("Choisir un projet :", list(projets_files.keys()))
        if st.button("Nouvelle question", key="btn_projets"):
            data = data_projets[projet_nom]
            q = pick_random_question(data)
            if q:
                st.session_state["last_question"] = q
                st.session_state["projet_actuel"] = projet_nom
            else:
                st.error("Aucune question trouvée dans ce projet.")
    
    with col2:
        q = st.session_state.get("last_question")
        if q:
            st.markdown("### Question")
            st.write(f"**Projet :** {st.session_state['projet_actuel']}")
            st.write(q.get("question", ""))
            
            with st.expander("Afficher réponse possible"):
                reponse = get_reponse(q)
                if reponse:
                    st.write(reponse)
                    if q.get("theme"):
                        st.caption(f"Thème : {q['theme']}")
                else:
                    st.info("Pas de réponse détaillée.")
        else:
            st.info("Choisis un projet et clique « Nouvelle question ».")

# ============================================================================
# TAB 2 : CULTURE G
# ============================================================================
with tab2:
    st.header("Culture générale actuariat / réglementation")
    
    data_culture = load_json(DATA_DIR / culture_file)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Nouvelle fiche culture", key="btn_culture"):
            bloc, section = pick_culture_block(data_culture)
            st.session_state["culture_bloc"] = bloc
            st.session_state["culture_section"] = section
    
    with col2:
        bloc = st.session_state.get("culture_bloc")
        if bloc:
            st.markdown(f"### **Bloc :** {bloc.get('titre', bloc.get('id', 'N/A'))}")
            st.write(bloc.get("description", ""))
            
            section = st.session_state.get("culture_section")
            if section:
                st.markdown(f"**Section :** {section.get('nom', 'N/A')}")
                st.write(section.get("resume", ""))
                
                points = section.get("points", [])
                if points:
                    st.markdown("**Points clés :**")
                    for p in points:
                        st.write(f"• {p}")
        else:
            st.info("Clique « Nouvelle fiche culture ».")

# ============================================================================
# TAB 3 : BRAIN TEASERS
# ============================================================================
with tab3:
    st.header("Brain teasers actuariat")
    
    data_brain = load_json(DATA_DIR / brain_file)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Nouveau brain teaser", key="btn_brain"):
            q = pick_random_question(data_brain)
            if q:
                st.session_state["brain_q"] = q
            else:
                st.error("Aucune question trouvée dans brain-teaser.json")
    
    with col2:
        q = st.session_state.get("brain_q")
        if q:
            st.markdown("### Question")
            st.write(q.get("intitule", q.get("question", "")))
            
            with st.expander("Solution détaillée"):
                reponse = get_reponse(q)
                if reponse:
                    st.markdown(reponse)
                if q.get("raisonnement"):
                    st.markdown("**Raisonnement :**")
                    for etape in q["raisonnement"]:
                        st.write(f"• {etape}")
                if q.get("tags"):
                    st.caption(f"Tags : {', '.join(q['tags'])}")
        else:
            st.info("Clique « Nouveau brain teaser ».")

# ============================================================================
# TAB 4 : SESSION 10 MIN
# ============================================================================
with tab4:
    st.header("Session mixte 10 minutes")
    
    if st.button("Démarrer session 10 min", key="btn_session"):
        # Mélange aléatoire : 2 projets + 1 culture + 1 brain
        projets = []
        for nom, data in data_projets.items():
            q = pick_random_question(data)
            if q:
                projets.append((nom, q))
        
        if len(projets) >= 2:
            p1, p2 = random.sample(projets, 2)
            culture_q = pick_culture_block(data_culture)[0]  # Juste le bloc
            brain_q = st.session_state.get("brain_q") or pick_random_question(data_brain)
            
            st.session_state["session_questions"] = [p1, p2, (culture_q, "Culture"), (brain_q, "Brain teaser")]
    
    questions_session = st.session_state.get("session_questions", [])
    for i, q in enumerate(questions_session):
        label, question_obj = q
        st.markdown(f"**Q{i+1} : {label}**")
        if isinstance(question_obj, tuple):
            bloc = question_obj
            st.write(bloc.get("titre", ""))
        else:
            st.write(question_obj.get("question", ""))
        
        with st.expander("Réponse"):
            reponse = get_reponse(question_obj)
            st.write(reponse)
        
        st.divider()
