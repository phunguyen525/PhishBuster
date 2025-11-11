import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PhishBuster", page_icon="🔐", layout="centered")

@st.cache_data
def load_samples(path: str = "phishing_samples.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize
    df.columns = [c.strip().lower() for c in df.columns]
    required = {"sender","subject","body","link","label","clue"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    df["label"] = df["label"].str.strip().str.lower()
    df = df[df["label"].isin(["phish","safe"])].reset_index(drop=True)
    return df

def new_round():
    """Pick a new random sample and reset per-round state."""
    st.session_state.current = random.randrange(len(st.session_state.samples))
    st.session_state.answered = False
    st.session_state.feedback = ""

def init_state():
    if "samples" not in st.session_state:
        st.session_state.samples = load_samples()
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "rounds" not in st.session_state:
        st.session_state.rounds = 0
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""
    if "current" not in st.session_state:
        new_round()

def render_email_card(row):
    with st.container(border=True):
        st.markdown(f"**From:** {row['sender']}")
        st.markdown(f"**Subject:** {row['subject']}")
        st.write(row["body"])
        st.write(f"**Link shown:** {row['link']}")

def answer(choice: str):
    if st.session_state.answered:
        return
    row = st.session_state.samples.iloc[st.session_state.current]
    correct = row["label"]
    st.session_state.rounds += 1
    if choice == correct:
        st.session_state.score += 1
        st.session_state.feedback = f"✅ Correct — {row['clue']}"
    else:
        human = {"phish":"Phishing", "safe":"Safe"}
        st.session_state.feedback = (
            f"❌ Not quite. It was **{human[correct]}** — {row['clue']}"
        )
    st.session_state.answered = True

init_state()

st.title("🔐 PhishBuster")
st.caption("Learn to spot phishing emails with quick, interactive rounds.")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Score", f"{st.session_state.score}")
with col_b:
    st.metric("Rounds", f"{st.session_state.rounds}")
with col_c:
    pct = 0 if st.session_state.rounds == 0 else round(100*st.session_state.score/st.session_state.rounds, 1)
    st.metric("Accuracy", f"{pct}%")

row = st.session_state.samples.iloc[st.session_state.current]
st.subheader("Is this message Phishing or Safe?")
render_email_card(row)

c1, c2 = st.columns(2)
with c1:
    st.button("🚩 Phishing", type="primary",
              on_click=answer, args=("phish",), disabled=st.session_state.answered)
with c2:
    st.button("✅ Safe", on_click=answer, args=("safe",), disabled=st.session_state.answered)

if st.session_state.feedback:
    st.info(st.session_state.feedback)

st.divider()
st.markdown("**Tips:**")
st.markdown(
"- Hover links before clicking; watch for mismatched domains.\n"
"- Check sender domain & display name spoofing.\n"
"- Look for urgency, threats, or password reset bait.\n"
"- Grammar/formatting oddities often signal phishing."
)

st.divider()
col1, col2 = st.columns([1,1])
with col1:
    st.button("🔄 Next Message", on_click=new_round, disabled=not st.session_state.answered)
with col2:
    if st.button("🗑️ Reset Score"):
        st.session_state.score = 0
        st.session_state.rounds = 0
        st.session_state.feedback = ""
        st.session_state.answered = False
        new_round()
