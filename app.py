import streamlit as st
import re

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


# =========================================================
# CONFIG
# =========================================================

PROJECT_ENDPOINT = (
    "https://eduvision-ai-resource.services.ai.azure.com/"
    "api/projects/eduvision-ai"
)

AGENT_NAME = "StudyMentor"
AGENT_VERSION = "2"


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="StudyMentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# GLOBAL STYLE  (refined, education-themed — visuals only)
# =========================================================

st.markdown("""
<style>

    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

    :root{
        --sm-bg:#0B0E1A;
        --sm-bg-soft:#0F1424;
        --sm-card:#141A2E;
        --sm-card-alt:#1A2138;
        --sm-border:rgba(255,255,255,0.09);
        --sm-gold:#E3A21A;
        --sm-gold-dark:#B97F0E;
        --sm-gold-soft:#F5D68C;
        --sm-teal:#1FC9B4;
        --sm-text:#EDEFF8;
        --sm-text-muted:#9BA3C2;
    }

    html, body, [class*="css"]{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp{
        background:
            radial-gradient(circle at 10% 0%, rgba(227,162,26,0.09) 0%, transparent 40%),
            radial-gradient(circle at 92% 12%, rgba(31,201,180,0.08) 0%, transparent 45%),
            var(--sm-bg);
    }

    /* clear Streamlit's fixed top toolbar so headings never get clipped */
    header[data-testid="stHeader"]{
        background: rgba(11,14,26,0.85) !important;
        backdrop-filter: blur(6px);
    }
    .block-container{
        padding-top: 4rem;
        padding-bottom: 6rem;
        max-width: 1100px;
    }

    /* base text color across the app */
    .stApp, .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown strong,
    h1, h2, h3, h4, h5, h6,
    div[data-testid="stWidgetLabel"] label, div[data-testid="stWidgetLabel"] p,
    .stRadio label, .stRadio div[role="radiogroup"] label p,
    div[data-testid="stCaptionContainer"]{
        color: var(--sm-text);
    }
    div[data-testid="stCaptionContainer"]{
        color: var(--sm-text-muted) !important;
    }

    /* ---------------- HERO ---------------- */
    .sm-hero{
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, var(--sm-card-alt) 0%, var(--sm-bg-soft) 100%);
        padding: 2.1rem 2.3rem;
        border-radius: 20px;
        color: var(--sm-text);
        margin-bottom: 1.7rem;
        border: 1px solid var(--sm-border);
        box-shadow: 0 14px 30px rgba(0,0,0,0.35);
    }
    .sm-hero::after{
        content: "";
        position: absolute;
        right: -60px;
        top: -60px;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(227,162,26,0.30) 0%, transparent 70%);
    }
    .sm-hero::before{
        content: "";
        position: absolute;
        left: 30%;
        bottom: -90px;
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(31,201,180,0.24) 0%, transparent 70%);
    }
    .sm-hero h1{
        margin: 0 0 0.35rem 0;
        font-family: 'Fraunces', serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: #FFFFFF;
        position: relative;
        z-index: 1;
    }
    .sm-hero p{
        margin: 0;
        color: var(--sm-text-muted);
        font-size: 1.02rem;
        max-width: 560px;
        position: relative;
        z-index: 1;
    }
    .sm-hero-badge{
        display:inline-block;
        background: rgba(227,162,26,0.15);
        border: 1px solid rgba(227,162,26,0.45);
        color: var(--sm-gold-soft);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 0.7rem;
        position: relative;
        z-index: 1;
    }

    /* ---------------- PAGE TITLES ---------------- */
    .sm-page-title{
        font-family: 'Fraunces', serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.15rem;
    }
    .sm-page-sub{
        color: var(--sm-text-muted);
        margin-bottom: 1.3rem;
        font-size: 0.98rem;
    }

    .sm-chip{
        display:inline-block;
        background: rgba(227,162,26,0.10);
        color: var(--sm-gold-soft);
        font-weight: 700;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 5px 13px;
        border-radius: 999px;
        margin-bottom: 0.6rem;
        border: 1px solid rgba(227,162,26,0.25);
    }

    /* ---------------- BUTTONS ---------------- */
    .stButton>button{
        background: linear-gradient(90deg, #2A3462, #1B2142);
        color: var(--sm-text);
        border: 1px solid var(--sm-border);
        border-radius: 10px;
        padding: 0.55rem 1.3rem;
        font-weight: 600;
        transition: transform 0.06s ease-in-out, box-shadow 0.15s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .stButton>button:hover{
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        color: white;
        border-color: rgba(227,162,26,0.4);
    }
    .stButton>button:disabled{
        background: #1A1E2E;
        color: #565C77;
        box-shadow: none;
        border-color: var(--sm-border);
    }

    /* primary CTA-style buttons (Generate / Submit / Create) get a gold accent */
    button[kind="primary"]{
        background: linear-gradient(90deg, var(--sm-gold), var(--sm-gold-dark)) !important;
        color: #1E1B10 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(227,162,26,0.25) !important;
    }
    button[kind="primary"]:hover{
        box-shadow: 0 6px 18px rgba(227,162,26,0.4) !important;
        color: #1E1B10 !important;
    }

    /* secondary (inactive nav) buttons */
    button[kind="secondary"]{
        background: rgba(255,255,255,0.04) !important;
        color: var(--sm-text) !important;
        box-shadow: none !important;
        border: 1px solid var(--sm-border) !important;
    }
    button[kind="secondary"]:hover{
        background: rgba(255,255,255,0.09) !important;
        color: #FFFFFF !important;
    }

    /* ---------------- CONTAINERS / CARDS ---------------- */
    div[data-testid="stVerticalBlockBorderWrapper"]{
        background: var(--sm-card);
        border-radius: 14px;
        border: 1px solid var(--sm-border) !important;
        box-shadow: 0 3px 14px rgba(0,0,0,0.25);
    }

    /* ---------------- PILLS (weak topics) ---------------- */
    .sm-pill{
        display:inline-block;
        background: rgba(227,162,26,0.14);
        color: var(--sm-gold-soft);
        border: 1px solid rgba(227,162,26,0.35);
        padding: 5px 13px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 3px 6px 3px 0;
    }

    .sm-lock-caption{
        color: var(--sm-text-muted);
        font-size: 0.78rem;
        margin: -0.4rem 0 0.6rem 0.2rem;
    }

    /* ---------------- SIDEBAR ---------------- */
    section[data-testid="stSidebar"]{
        background: var(--sm-bg-soft);
        border-right: 1px solid var(--sm-border);
    }
    section[data-testid="stSidebar"] *{
        color: var(--sm-text);
    }
    section[data-testid="stSidebar"] hr{
        border-color: var(--sm-border);
    }
    section[data-testid="stSidebar"] .sm-lock-caption{
        color: var(--sm-text-muted);
    }

    /* ---------------- METRIC ---------------- */
    div[data-testid="stMetric"]{
        background: rgba(31,201,180,0.08);
        border: 1px solid rgba(31,201,180,0.25);
        border-radius: 12px;
        padding: 0.6rem 0.9rem;
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div{
        color: var(--sm-text) !important;
    }

    /* ---------------- CHAT MESSAGES ---------------- */
    div[data-testid="stChatMessage"]{
        background: var(--sm-card) !important;
        border: 1px solid var(--sm-border);
        border-radius: 12px;
    }

    hr{ margin: 1.4rem 0; border-color: var(--sm-border); }

</style>
""", unsafe_allow_html=True)


# =========================================================
# CONNECT TO MICROSOFT FOUNDRY
# =========================================================

credential = DefaultAzureCredential()

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential
)

openai = project.get_openai_client()


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    "vector_store_id": None,
    "file_id": None,
    "quiz_text": None,
    "quiz_generated": False,
    "quiz_questions": [],
    "quiz_submitted": False,
    "score": None,
    "weak_topics": [],

    # UI-only state
    "nav": "chat",
    "chat_messages": [],

}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# SCHEDULING STATE
# =========================================================

if "deadline" not in st.session_state:
    st.session_state.deadline = None

if "study_hours" not in st.session_state:
    st.session_state.study_hours = None


# =========================================================
# SIDEBAR — NAVIGATION
# =========================================================

with st.sidebar:

    st.markdown("### 🎓 StudyMentor")
    st.caption("Your AI-powered personalized study mentor")
    st.markdown("---")
    st.markdown("#### Navigate")

    # 1) Chat (always available — this is the landing page)
    if st.button(
        "💬 Chat",
        use_container_width=True,
        type="primary" if st.session_state.nav == "chat" else "secondary"
    ):
        st.session_state.nav = "chat"
        st.rerun()

    # 2) Knowledge Checker (locked until material is processed)
    quiz_locked = st.session_state.vector_store_id is None
    if st.button(
        "🧠 Knowledge Checker",
        use_container_width=True,
        disabled=quiz_locked,
        type="primary" if st.session_state.nav == "quiz" else "secondary"
    ):
        st.session_state.nav = "quiz"
        st.rerun()
    if quiz_locked:
        st.markdown(
            '<div class="sm-lock-caption">🔒 Upload your notes to unlock</div>',
            unsafe_allow_html=True
        )

    # 3) Study Schedule (locked until quiz is submitted)
    schedule_locked = not st.session_state.quiz_submitted
    if st.button(
        "📅 Study Schedule",
        use_container_width=True,
        disabled=schedule_locked,
        type="primary" if st.session_state.nav == "schedule" else "secondary"
    ):
        st.session_state.nav = "schedule"
        st.rerun()
    if schedule_locked:
        st.markdown(
            '<div class="sm-lock-caption">🔒 Finish the quiz to unlock</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption(
        "💡 Upload your notes, chat with StudyMentor, test yourself, "
        "then get a schedule built around your weak topics."
    )


# =========================================================
# PARSE QUIZ
# =========================================================

def parse_quiz(text):

    questions = []

    blocks = re.split(
        r"(?=Q\d+\.)",
        text
    )

    for block in blocks:

        block = block.strip()

        if not re.match(r"Q\d+\.", block):
            continue

        question_match = re.search(
            r"Q\d+\.\s*(.*?)(?=\nA\))",
            block,
            re.DOTALL
        )

        option_a = re.search(
            r"A\)\s*(.*?)(?=\nB\))",
            block,
            re.DOTALL
        )

        option_b = re.search(
            r"B\)\s*(.*?)(?=\nC\))",
            block,
            re.DOTALL
        )

        option_c = re.search(
            r"C\)\s*(.*?)(?=\nD\))",
            block,
            re.DOTALL
        )

        option_d = re.search(
            r"D\)\s*(.*?)(?=\nCorrect Answer:)",
            block,
            re.DOTALL
        )

        answer_match = re.search(
            r"Correct Answer:\s*([ABCD])",
            block
        )

        topic_match = re.search(
            r"Topic:\s*(.*)",
            block
        )

        if not all([
            question_match,
            option_a,
            option_b,
            option_c,
            option_d,
            answer_match
        ]):
            continue

        question = question_match.group(1).strip()

        options = [
            option_a.group(1).strip(),
            option_b.group(1).strip(),
            option_c.group(1).strip(),
            option_d.group(1).strip()
        ]

        correct_answer = answer_match.group(1).strip()

        topic = (
            topic_match.group(1).strip()
            if topic_match
            else "Unknown Topic"
        )

        questions.append({
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic": topic
        })

    return questions


# =========================================================
# PAGE: CHAT  (landing page — upload + chat only)
# =========================================================

if st.session_state.nav == "chat":

    st.markdown("""
    <div class="sm-hero">
        <div class="sm-hero-badge">Personalized Learning</div>
        <h1>🎓 StudyMentor</h1>
        <p>Upload your notes, then chat with StudyMentor about anything inside them — like having a tutor who has actually read your material.</p>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # FILE UPLOAD
    # -----------------------------------------------------

    st.markdown('<span class="sm-chip">📘 Study Material</span>', unsafe_allow_html=True)

    with st.container(border=True):

        uploaded_file = st.file_uploader(
            "Upload your study material",
            type=["pdf", "txt", "docx", "pptx"]
        )

        if uploaded_file:

            st.success(f"Selected: {uploaded_file.name}")

            if st.button("⚙️ Process My Notes", type="primary"):

                with st.spinner("Processing your study material..."):

                    try:

                        temp_file = uploaded_file.name

                        with open(temp_file, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Create vector store
                        vector_store = openai.vector_stores.create(
                            name="StudyMentor_User_Notes"
                        )

                        # Upload file
                        with open(temp_file, "rb") as f:

                            file = openai.vector_stores.files.upload_and_poll(
                                vector_store_id=vector_store.id,
                                file=f
                            )

                        # Save session information
                        st.session_state.vector_store_id = vector_store.id
                        st.session_state.file_id = file.id

                        # Reset quiz
                        st.session_state.quiz_text = None
                        st.session_state.quiz_generated = False
                        st.session_state.quiz_questions = []
                        st.session_state.quiz_submitted = False
                        st.session_state.score = None
                        st.session_state.weak_topics = []

                        # Reset chat for the new material
                        st.session_state.chat_messages = []

                        st.success(
                            "✅ Notes processed successfully!"
                        )

                        st.info(
                            "Your study material is ready."
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Error processing notes: {e}"
                        )

    st.divider()

    # -----------------------------------------------------
    # STUDY CHAT (chat-style, fixed input footer)
    # -----------------------------------------------------

    st.markdown('<span class="sm-chip">💬 Study Chat</span>', unsafe_allow_html=True)

    if st.session_state.vector_store_id:

        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        question = st.chat_input("Ask StudyMentor about your notes...")

        if question:

            st.session_state.chat_messages.append(
                {"role": "user", "content": question}
            )

            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):

                with st.spinner("🔎 Searching your study material..."):

                    try:

                        response = openai.responses.create(

                            input=question,

                            extra_body={
                                "agent_reference": {
                                    "name": AGENT_NAME,
                                    "version": AGENT_VERSION,
                                    "type": "agent_reference"
                                },

                                "structured_inputs": {
                                    "vector_store_id":
                                        st.session_state.vector_store_id
                                }
                            }
                        )

                        st.write(response.output_text)

                        st.session_state.chat_messages.append(
                            {"role": "assistant", "content": response.output_text}
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Chat error: {e}"
                        )

    else:

        st.info("📤 Upload and process your study material above to start chatting.")


# =========================================================
# PAGE: KNOWLEDGE CHECKER  (quiz + results)
# =========================================================

elif st.session_state.nav == "quiz":

    st.markdown('<div class="sm-page-title">🧠 Knowledge Checker</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sm-page-sub">Test yourself on your uploaded material and spot your weak topics.</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.vector_store_id:

        st.info("📤 Upload and process your study material from the Chat page first.")

    else:

        # ---------------------------------------------
        # QUIZ GENERATION
        # ---------------------------------------------

        st.markdown('<span class="sm-chip">✍️ Generate</span>', unsafe_allow_html=True)

        with st.container(border=True):

            col_a, col_b = st.columns([2, 1])

            with col_a:
                number_of_questions = st.selectbox(
                    "Number of questions",
                    [5, 10, 15, 20],
                    index=0
                )

            with col_b:
                st.write("")
                st.write("")
                generate_clicked = st.button("📝 Generate Quiz", use_container_width=True, type="primary")

            if generate_clicked:

                quiz_prompt = f"""
You are generating an exam quiz from the student's uploaded
study material.

IMPORTANT QUESTION COUNT:
The student selected EXACTLY {number_of_questions} questions.

You MUST generate EXACTLY {number_of_questions} questions.

If the selected number is:
- 5 → generate exactly 5 questions
- 10 → generate exactly 10 questions
- 15 → generate exactly 15 questions
- 20 → generate exactly 20 questions

NEVER generate only 5 questions when the requested number is
10, 15, or 20.

Use File Search to retrieve information from the student's
uploaded study material.

The questions must be based ONLY on the uploaded study material.

Use EXACTLY this format for every question:

Q1. Question text

A) Option A
B) Option B
C) Option C
D) Option D

Correct Answer: A
Topic: Topic name

Q2. Question text

A) Option A
B) Option B
C) Option C
D) Option D

Correct Answer: B
Topic: Topic name

Continue this exact format until you have generated
EXACTLY {number_of_questions} questions.

RULES:

1. Generate EXACTLY {number_of_questions} questions.
2. Exactly 4 options per question.
3. Only one option is correct.
4. Correct Answer must be A, B, C, or D.
5. Include the topic being tested.
6. Keep questions exam-oriented.
7. Use ONLY information from the uploaded study material.
8. Do not add explanations.
9. Do not use Markdown tables.
10. Do not stop after 5 questions.
11. Before finishing, count your questions.
12. If the count is less than {number_of_questions}, continue
    generating questions until the count reaches exactly
    {number_of_questions}.
"""

                with st.spinner(
                    f"🧠 Generating {number_of_questions} questions..."
                ):

                    try:

                        response = openai.responses.create(

                            input=quiz_prompt,

                            extra_body={
                                "agent_reference": {
                                    "name": AGENT_NAME,
                                    "version": AGENT_VERSION,
                                    "type": "agent_reference"
                                },

                                "structured_inputs": {
                                    "vector_store_id":
                                        st.session_state.vector_store_id
                                }
                            }
                        )

                        quiz_text = response.output_text.strip()

                        if not quiz_text:

                            st.error(
                                "❌ No quiz was returned."
                            )

                        else:

                            # Parse the generated questions
                            questions = parse_quiz(quiz_text)

                            # Verify requested question count
                            if len(questions) != number_of_questions:

                                st.error(
                                    f"❌ StudyMentor generated "
                                    f"{len(questions)} questions instead of "
                                    f"{number_of_questions}."
                                )

                                st.info(
                                    "Please click Generate Quiz again."
                                )

                                st.session_state.quiz_text = quiz_text

                                st.code(quiz_text)

                            else:

                                st.session_state.quiz_text = quiz_text
                                st.session_state.quiz_questions = questions
                                st.session_state.quiz_generated = True
                                st.session_state.quiz_submitted = False
                                st.session_state.score = None
                                st.session_state.weak_topics = []

                                st.success(
                                    f"✅ {number_of_questions} questions generated!"
                                )

                                st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Quiz generation error: {e}"
                        )

        # ---------------------------------------------
        # DISPLAY CLICKABLE QUIZ
        # ---------------------------------------------

        if st.session_state.quiz_questions:

            st.divider()
            st.markdown('<span class="sm-chip">🎯 Answer</span>', unsafe_allow_html=True)
            st.subheader("🎯 Answer the Quiz")

            total_questions = len(st.session_state.quiz_questions)

            for i, q in enumerate(
                st.session_state.quiz_questions
            ):

                with st.container(border=True):

                    st.caption(f"Question {i + 1} of {total_questions} · Topic: {q['topic']}")

                    st.markdown(
                        f"**Q{i + 1}. {q['question']}**"
                    )

                    st.radio(
                        "Choose your answer:",
                        ["A", "B", "C", "D"],

                        format_func=lambda x, q=q:
                            f"{x}) {q['options'][ord(x) - ord('A')]}",

                        key=f"quiz_answer_{i}"
                    )

            # -------------------------------------------
            # SUBMIT QUIZ
            # -------------------------------------------

            if not st.session_state.quiz_submitted:

                if st.button("✅ Submit Quiz", type="primary"):

                    score = 0
                    weak_topics = []

                    for i, q in enumerate(
                        st.session_state.quiz_questions
                    ):

                        selected = st.session_state[
                            f"quiz_answer_{i}"
                        ]

                        correct = q["correct_answer"]

                        if selected == correct:

                            score += 1

                        else:

                            weak_topics.append(
                                q["topic"]
                            )

                    st.session_state.score = score

                    st.session_state.weak_topics = list(
                        dict.fromkeys(weak_topics)
                    )

                    st.session_state.quiz_submitted = True

                    st.rerun()

        # ---------------------------------------------
        # QUIZ RESULT
        # ---------------------------------------------

        if st.session_state.quiz_submitted:

            st.divider()
            st.markdown('<span class="sm-chip">📊 Results</span>', unsafe_allow_html=True)
            st.subheader("📊 Quiz Result")

            total = len(
                st.session_state.quiz_questions
            )

            score = st.session_state.score

            percentage = (
                score / total
            ) * 100

            with st.container(border=True):

                col1, col2 = st.columns([1, 2])

                with col1:
                    st.metric("Score", f"{score}/{total}", f"{percentage:.1f}%")

                with col2:
                    st.progress(int(percentage))
                    st.success(
                        f"Score: {score}/{total} "
                        f"({percentage:.1f}%)"
                    )

                # -----------------------------------
                # WEAK TOPICS
                # -----------------------------------

                if st.session_state.weak_topics:

                    st.warning(
                        "📌 Topics to revise:"
                    )

                    pills_html = "".join(
                        f'<span class="sm-pill">{topic}</span>'
                        for topic in st.session_state.weak_topics
                    )
                    st.markdown(pills_html, unsafe_allow_html=True)

                else:

                    st.success(
                        "🎉 Excellent! No weak topics detected."
                    )

                st.write("")

                if st.button("📅 Build my study schedule", use_container_width=True, type="primary"):
                    st.session_state.nav = "schedule"
                    st.rerun()


# =========================================================
# PAGE: STUDY SCHEDULE
# =========================================================

elif st.session_state.nav == "schedule":

    st.markdown('<div class="sm-page-title">📅 Personalized Study Schedule</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sm-page-sub">A day-by-day plan built around your quiz results.</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.quiz_submitted:

        st.info("🧠 Finish the Knowledge Checker quiz first to unlock your schedule.")

    else:

        with st.container(border=True):

            col_d, col_h = st.columns(2)

            with col_d:
                deadline = st.date_input(
                    "📅 Select your deadline",
                    key="deadline_input"
                )

            with col_h:
                study_hours = st.number_input(
                    "⏱️ Available study hours per day",
                    min_value=1,
                    max_value=12,
                    value=3,
                    step=1,
                    key="study_hours_input"
                )

            if st.button("📚 Create Study Schedule", type="primary"):

                # -------------------------------------------------
                # CALCULATE AVAILABLE DAYS
                # -------------------------------------------------

                from datetime import date

                today = date.today()

                days_available = (
                    deadline - today
                ).days + 1

                # Prevent invalid deadline
                if days_available <= 0:

                    st.error(
                        "❌ Please select a future deadline."
                    )

                else:

                    weak_topics = st.session_state.weak_topics

                    if weak_topics:

                        weak_topic_text = ", ".join(
                            weak_topics
                        )

                    else:

                        weak_topic_text = "No weak topics detected"


                    # -------------------------------------------------
                    # STUDY SCHEDULE PROMPT
                    # -------------------------------------------------

                    schedule_prompt = f"""
Create a concise and well-organized study schedule.

TODAY'S DATE:
{today}

DEADLINE:
{deadline}

EXACT NUMBER OF AVAILABLE STUDY DAYS:
{days_available}

AVAILABLE STUDY HOURS PER DAY:
{study_hours}

WEAK TOPICS FROM QUIZ:
{weak_topic_text}

IMPORTANT:
The schedule MUST contain exactly {days_available} days.

Do NOT create more than {days_available} days.
Do NOT create fewer than {days_available} days.

For example:
If there are 2 available days, create exactly Day 1 and Day 2.
If there are 3 available days, create exactly Day 1, Day 2 and Day 3.

Use the student's uploaded study material when
referring to study topics.

FORMAT:

📅 Study Schedule

Day 1
• Topic:
• Study time:
• Task:
• Practice:

Day 2
• Topic:
• Study time:
• Task:
• Practice:

Continue until exactly Day {days_available}.

RULES:
- Exactly {days_available} days.
- Maximum {study_hours} study hours per day.
- Prioritize weak topics.
- Include revision and practice.
- Keep it concise.
- Use short bullet points.
- Do not write long explanations.
- Do not add an introduction.
- Do not add a conclusion.
- Do not add motivational paragraphs.
"""


                    # -------------------------------------------------
                    # GENERATE SCHEDULE
                    # -------------------------------------------------

                    with st.spinner(
                        "🧠 Creating your personalized study schedule..."
                    ):

                        try:

                            response = openai.responses.create(

                                input=schedule_prompt,

                                extra_body={
                                    "agent_reference": {
                                        "name": AGENT_NAME,
                                        "version": AGENT_VERSION,
                                        "type": "agent_reference"
                                    },

                                    "structured_inputs": {
                                        "vector_store_id":
                                            st.session_state.vector_store_id
                                    }
                                }
                            )

                            schedule = response.output_text.strip()

                            if schedule:

                                st.success(
                                    f"✅ {days_available}-day study schedule created!"
                                )

                                st.markdown(schedule)

                            else:

                                st.error(
                                    "❌ No study schedule was generated."
                                )

                        except Exception as e:

                            st.error(
                                f"❌ Schedule generation error: {e}"
                            )