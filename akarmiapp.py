import streamlit as st
import google.generativeai as genai
from streamlit.components.v1 import html
import requests

# Hosted with Streamlit és profil jelvény eltüntetése
html("""
<script>
const hideStreamlitBadge = () => {
    try {
        const badges = window.top.document.querySelectorAll('[href*="streamlit.io"], [class*="viewerBadge"]');
        badges.forEach(el => el.style.setProperty("display", "none", "important"));
    } catch (e) {}
};
window.addEventListener('load', hideStreamlitBadge);
setInterval(hideStreamlitBadge, 500);
</script>
""", height=0, width=0)

# ==========================================
# 1. GOOGLE GEMINI KONFIGURÁCIÓ
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ==========================================
# 2. ADATBÁZIS KEZELÉS (Közvetlen Web API kapcsolat)
# ==========================================
API_URL = "https://script.google.com/macros/s/AKfycbyxrS7YzliiFl6qOWIl0v0kNM4kDFIBS_c3Mcxpw0IH90R2mBHBpk6QGuaPhAjKfhWu/exec"

def get_user_credits(email, code):
    try:
        res = requests.get(API_URL, params={
            "action": "login",
            "email": str(email).strip().lower(),
            "code": str(code).strip()
        }, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                return int(data.get("credits", 0))
        return None
    except Exception as e:
        st.error(f"Hálózati hiba: {e}")
        return None

def deduct_one_credit(email):
    try:
        res = requests.get(API_URL, params={
            "action": "deduct",
            "email": str(email).strip().lower()
        }, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            return data.get("status") == "success"
        return False
    except Exception as e:
        st.error(f"Hiba a kredit levonásakor: {e}")
        return False

# ==========================================
# 3. GENERÁLÓ MOTOR (Dinamikus Hossz)
# ==========================================
def generate_faceless_script(tema, kategoria, hossz):
    model = genai.GenerativeModel("gemini-3.6-flash")
    
    if "10" in hossz:
        struktura_utasitas = """
        CÉLHOSSZ: PONTOSAN 10 MÁSODPERC (Ultra-rövid, végtelenített loop videó).
        - Narráció: Összesen 15-20 szó! Egyetlen brutális felütés és egy sokkoló tény, ami az utolsó szóval visszautal az elsőre (hogy végtelenül lehessen ismételni).
        - Képprompt: 1 vagy maximum 2 db ultra-realisztikus angol Midjourney képleírás (--ar 9:16 --style raw).
        - CTA: Rövid kérdés a képernyőre írva.
        """
    elif "30" in hossz:
        struktura_utasitas = """
        CÉLHOSSZ: KB. 30 MÁSODPERC (Pörgős, figyelemfenntartó ritmus).
        - 🪝 Hook (0-3 mp): 1 erős, provokatív mondat.
        - 🎬 Történet (3-25 mp): 2 tömör, feszes jelenet természetes magyar narrációval és 2 db angol fotorealisztikus képprompttal (--ar 9:16).
        - 📢 CTA (25-30 mp): Kommentkérdés.
        """
    else:  # 60 másodperc
        struktura_utasitas = """
        CÉLHOSSZ: 50-60 MÁSODPERC (Részletes storytelling / Toplista formátum).
        - 🪝 Hook (0-3 mp): Görgetésmegállító felütés beszélt magyar nyelven + 1 angol képprompt.
        - 🎬 Jelenetek (3-50 mp): 3 különálló, részletes jelenet természetes, ritmusos magyar narrációval és jelenetenként 1-1 angol képprompttal (--ar 9:16).
        - 📢 CTA (50-60 mp): Vita- vagy megosztásindító zárszó.
        """

    prompt = f"""
    Te egy elit szintű TikTok és YouTube Shorts Faceless videó forgatókönyvíró és AI képprompt specialista vagy.
    Készíts egy virális Faceless videótervezetet az alábbi paraméterek szerint:
    - Téma: {tema}
    - Kategória: {kategoria}
    - Választott hossz: {hossz}

    IRÁNYELVEK:
    {struktura_utasitas}

    KÖVETELMÉNYEK:
    1. A narráció természetes, modern, beszélt magyar nyelven szóljon (ne legyen robotikus vagy Google Fordító-szerű).
    2. A képpromptok MINDIG részletes, fotorealisztikus ANGOL nyelvű promptok legyenek, a végükön kötelezően: '--ar 9:16 --style raw'.
    """
    
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 4. STREAMLIT FELÜLET ÉS STÍLUSOK
# ==========================================
st.set_page_config(page_title="Faceless Videó Generátor", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    button[data-testid="baseButton-primary"], button[kind="primary"] {
        background-color: #22c55e !important;
        border-color: #22c55e !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
    }
    button[data-testid="baseButton-primary"]:hover, button[kind="primary"]:hover {
        background-color: #16a34a !important;
        border-color: #16a34a !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"],
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        color: #ef4444 !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover,
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: rgba(239, 68, 68, 0.28) !important;
        border-color: rgba(239, 68, 68, 0.7) !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "credits" not in st.session_state:
    st.session_state.credits = 0

# --- OLDALSÁV (BEJELENTKEZÉS) ---
with st.sidebar:
    st.header("🔑 Fiók & Hozzáférés")
    
    if not st.session_state.logged_in:
        st.write("Jelentkezz be a hozzáférési kódoddal:")
        login_email = st.text_input("E-mail cím", placeholder="pelda@gmail.com")
        login_code = st.text_input("Licenckód", type="password")
        
        if st.button("Belépés", type="primary", use_container_width=True):
            creds = get_user_credits(login_email, login_code)
            if creds is not None:
                st.session_state.logged_in = True
                st.session_state.user_email = login_email.strip().lower()
                st.session_state.credits = creds
                st.success("Sikeres belépés!")
                st.rerun()
            else:
                st.error("Érvénytelen e-mail cím vagy licenckód!")
    else:
        st.success(f"Bejelentkezve:\n**{st.session_state.user_email}**")
        st.metric(label="Elérhető kreditek", value=f"{st.session_state.credits} db")
        
        if st.session_state.credits <= 5:
            st.warning("Fogytán vannak a kreditjeid!")
            st.markdown("[👉 **Kreditek újratöltése itt**](https://digitalproduct-store.com)")
            
        if st.button("Kijelentkezés", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.credits = 0
            st.rerun()

# --- FŐOLDAL ---
st.title("🎬 Faceless Videó Forgatókönyv Generátor")
st.caption("Készíts virális magyar narrációt és hollywoodi angol képpromptokat 10, 30 vagy 60 másodperces hosszban.")

if not st.session_state.logged_in:
    st.divider()
    st.markdown("""
    ### 🔥 Szeretnél te is arcmutatás nélkül nézettséget építeni?
    
    * 🚫 **Nulla kamera és arcmutatás:** Nem kell szerepelned, a videók 100%-ban automatizált képekkel és feliratokkal készülnek.
    * 🇭🇺 **Valódi, ritmusos beszélt magyar nyelv:** Nem robotszöveg – azonnal másolható, dinamikus felolvasást kapsz.
    * ⚡ **Hollywoodi minőségű képpromptok angolul:** Egyetlen gombnyomásra megkapod a tökéletes Midjourney és Leonardo leírásokat nyelvtudás nélkül.
    """)
    
    st.write("")
    st.markdown("""
    <div style="margin: 15px 0;">
        <a href="https://digitalproduct-store.com" target="_blank" style="
            display: inline-block;
            background-color: #22c55e;
            color: #ffffff;
            text-align: center;
            padding: 12px 28px;
            font-size: 16px;
            font-weight: 700;
            border-radius: 6px;
            text-decoration: none;
            box-shadow: 0 4px 10px rgba(34, 197, 94, 0.3);
        ">👉 KÉREM A HOZZÁFÉRÉST</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.info("👈 **Már van licenckódod?** Add meg az e-mail címedet és a kódodat a bal oldali sávban a szoftver azonnali indításához!")

else:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        tema = st.text_input("Miről szóljon a videó? (Téma / Cím)", placeholder="pl. A 3 legveszélyesebb hely a Földön, ahová tilos belépni")
    with col2:
        kategoria = st.selectbox("Kategória / Nise", ["Érdekességek & Rejtélyek", "Pszichológia & Önfejlesztés", "Pénz, Siker & Történetek", "Történelem & Legendák", "Sci-Fi & Jövő"])
    with col3:
        hossz = st.selectbox("Videó hossza", ["10 másodperc (Gyors / Loop)", "30 másodperc (Pörgős sztori)", "60 másodperc (Teljes történet)"])

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        start_generation = st.button("🚀 Generálás (1 kredit)", type="primary")

    if start_generation:
        if not tema.strip():
            st.error("Kérlek, adj meg egy témát a generáláshoz!")
        elif st.session_state.credits <= 0:
            st.error("Elfogyott az összes kredited! Töltsd újra az egyenleged a bal oldali linken.")
        else:
            with st.spinner("Kérlek várj, azonnal kész..."):
                try:
                    eredmeny = generate_faceless_script(tema, kategoria, hossz)
                    deduct_one_credit(st.session_state.user_email)
                    st.session_state.credits -= 1
                    
                    st.success("A forgatókönyv elkészült! (1 kredit levonva)")
                    st.markdown(eredmeny)
                    
                    st.download_button(
                        label="📥 Forgatókönyv letöltése (.txt)",
                        data=eredmeny,
                        file_name=f"faceless_{hossz[:2]}mp_{tema[:15].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Hiba történt a generálás közben: {e}")
