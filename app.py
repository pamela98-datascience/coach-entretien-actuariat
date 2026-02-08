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
        st.error(f"❌ Fichier manquant : {path.name}")
        return {}
    except json.JSONDecodeError:
        st.error(f"❌ Erreur JSON : {path.name}")
        return {}
    except Exception:
        st.error(f"❌ Erreur lecture : {path.name}")
        return {}

def pick_random_question(block):
    """Fonction universelle pour TOUS tes formats JSON."""
    if isinstance(block, list):
        if not block:
            return None
        return random.choice(block)
    
    possible_keys = ["questions", "questionsentretiens"]
    for key in possible_keys:
        if key in block:
            questions = block[key]
            if questions:
                return random.choice(questions)
    
    return None

def pick_culture_block(data_culture):
    """Pour culture-G-actuariat.json."""
    blocs = data_culture.get("blocs", [])
    if not blocs:
        return None
    bloc = random.choice(blocs)
    sections = bloc.get("sections", [])
    section = random.choice(sections) if sections else None
    return bloc, section

def get_reponse(q):
    """Récupère la réponse sous tous les formats."""
    keys = ["reponse", "reponse_courte", "reponse_textuelle", "reponse_numerique", "resume"]
    for key in keys:
        if q and key in q and q[key]:
            return q[key]
    return ""

# Fichiers (adapte les noms exacts à ton repo GitHub)
projets_files = {
    "Tarification GLM Poisson": "Tarification-auto-GLM-Poisson-application-Streamlit.json",
    "Provisionnement Triangle": "Provisionnement_Non-Vie_Triangle_de_développement_Chain_Ladder.json", 
    "Gestion Actifs SFCR": "analyse-gestion-actifs-sfcr.json",
    "Détection Fraude": "detection-fraude.json"
}

culture_file = "culture-G-actuariat.json"
brain_file = "brain-teaser.json"

st.title("🤖 Coach entretien actuariat CFA")

tab1, tab2, tab3, tab4 = st.tabs(["💼 Mes projets", "📚 Culture G", "🧠 Brain teasers", "⏱️ Session 10 min"])

# ============================================================================
# TAB 1 : MES PROJETS
# ============================================================================
with tab1:
    st.header("Questions sur mes projets")
    
    data_projets = {nom: load_json(DATA_DIR / fichier) for nom, fichier in projets_files.items()}
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        projet_nom = st.selectbox("Projet :", list(projets_files.keys()))
        if st.button("🎲 Nouvelle question", key="btn_projets"):
            data = data_projets[projet_nom]
            q = pick_random_question(data)
            if q:
                st.session_state["projet_q"] = q
                st.session_state["projet_nom"] = projet_nom
            else:
                st.error("❌ Pas de questions dans ce projet")
    
    with col2:
        if "projet_q" in st.session_state:
            q = st.session_state["projet_q"]
            st.markdown("### ❓ Question")
            st.markdown(f"**Projet :** {st.session_state['projet_nom']}")
            st.write(q.get("question", ""))
            
            with st.expander("👁️ Réponse") :
                reponse = get_reponse(q)
                if reponse:
                    st.markdown(reponse)
                    if q.get("theme"):
                        st.caption(f"Thème : {q['theme']}")
                else:
                    st.info("Pas de réponse détaillée")
        else:
            st.info("👈 Choisis un projet et clique Nouvelle question")

# ============================================================================
# TAB 2 : CULTURE G  
# ============================================================================
with tab2:
    st.header("Culture générale actuariat")
    
    data_culture = load_json(DATA_DIR / culture_file)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📖 Nouvelle fiche", key="btn_culture"):
            bloc, section = pick_culture_block(data_culture)
            if bloc:
                st.session_state["culture_bloc"] = bloc
                st.session_state["culture_section"] = section
            else:
                st.error("❌ Problème culture-G-actuariat.json")
    
    with col2:
        if "culture_bloc" in st.session_state:
            bloc = st.session_state["culture_bloc"]
            st.markdown(f"### 📘 **{bloc.get('titre', 'N/A')}**")
            st.write(bloc.get("description", ""))
            
            section = st.session_state.get("culture_section")
            if section:
                st.markdown(f"**Section :** {section.get('nom')}")
                st.write(section.get("resume", ""))
                points = section.get("points", [])
                if points:
                    st.markdown("**Points clés :**")
                    for p in points:
                        st.write(f"• {p}")
        else:
            st.info("👈 Clique Nouvelle fiche")

# ============================================================================
# TAB 3 : BRAIN TEASERS
# ============================================================================
with tab3:
    st.header("🧠 Brain teasers actuariat")
    
    data_brain = load_json(DATA_DIR / brain_file)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🧩 Nouveau brain teaser", key="btn_brain"):
            q = pick_random_question(data_brain)
            if q:
                st.session_state["brain_q"] = q
            else:
                st.error("❌ Problème brain-teaser.json")
    
    with col2:
        if "brain_q" in st.session_state:
            q = st.session_state["brain_q"]
            st.markdown("### ❓ Question")
            st.write(q.get("intitule", q.get("question", "")))
            
            with st.expander("💡 Solution"):
                reponse = get_reponse(q)
                if reponse:
                    st.markdown(reponse)
                if q.get("raisonnement"):
                    st.markdown("**Raisonnement étape par étape :**")
                    for etape in q["raisonnement"]:
                        st.write(f"• {etape}")
        else:
            st.info("👈 Clique Nouveau brain teaser")

# ============================================================================
# TAB 4 : SESSION 10 MIN (BLINDÉE CONTRE ERREURS)
# ============================================================================
with tab4:
    st.header("⏱️ Session mixte 10 minutes")
    
    if st.button("🚀 Démarrer session (2 projets + 1 culture + 1 brain)"):
        session_questions = []
        
        # 2 projets aléatoires
        projets_list = [(nom, data) for nom, data in data_projets.items() if data]
        if len(projets_list) >= 2:
            p1_nom, p1_data = random.choice(projets_list)
            p2_nom, p2_data = random.choice([p for p in projets_list if p[0] != p1_nom])
            q1 = pick_random_question(p1_data)
            q2 = pick_random_question(p2_data)
            if q1: session_questions.append((p1_nom, q1))
            if q2: session_questions.append((p2_nom, q2))
        
        # 1 culture
        bloc, _ = pick_culture_block(data_culture)
        if bloc: session_questions.append(("Culture G", bloc))
        
        # 1 brain
        brain_q = pick_random_question(data_brain)
        if brain_q: session_questions.append(("Brain teaser", brain_q))
        
        st.session_state["session_questions"] = session_questions
        st.success(f"✅ Session prête : {len(session_questions)} questions !")
    
    if "session_questions" in st.session_state:
        questions = st.session_state["session_questions"]
        for i, (label, q_obj) in enumerate(questions):
            st.markdown(f"**Q{i+1} : {label}**")
            if isinstance(q_obj, dict) and "titre" in q_obj:
                st.write(q_obj.get("titre"))
            else:
                st.write(q_obj.get("question", q_obj.get("intitule", "")))
            
            with st.expander("👁️ Réponse"):
                reponse = get_reponse(q_obj)
                st.markdown(reponse)
            
            st.divider()
    else:
        st.info("👈 Clique 'Démarrer session'")

st.markdown("---")
st.caption("📁 Vérifie que tous les JSON sont dans le même dossier que app.py")
