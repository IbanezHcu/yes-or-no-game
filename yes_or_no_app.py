import streamlit as st

# --- INITIAL SETUP ---
if 'phase' not in st.session_state:
    st.session_state.phase = 'setup'
    st.session_state.players = []
    st.session_state.scores = {}
    st.session_state.current_owner_idx = 0
    st.session_state.current_turn_idx = 0
    st.session_state.active_players = []
    st.session_state.eliminated = []
    st.session_state.total_rounds = 1
    st.session_state.rounds_left = 0
    st.session_state.answer = ""
    st.session_state.question_history = []
    st.session_state.total_questions = 0
    st.session_state.max_questions = 5
    st.session_state.asking_queue = []
    st.session_state.ask_count = {}
    st.session_state.last_question = None

st.title("🧠 เกม 'ใช่หรือไม่วะเนี่ย' ")

# --- SETUP PHASE ---
if st.session_state.phase == 'setup':
    st.header("🎮 ตั้งค่าผู้เล่นและจำนวนรอบ")
    num_players = st.slider("จำนวนผู้เล่น (2-10 คน)", 2, 10, 5)
    total_rounds = st.number_input("จำนวนรอบที่แต่ละคนจะได้ตั้งคำตอบ (1 รอบ = 1 คนตั้งคำตอบ)", min_value=1, value=1)

    names = []
    for i in range(num_players):
        name = st.text_input(f"ชื่อผู้เล่นคนที่ {i+1}", key=f"player_{i}")
        if name:
            names.append(name)

    if st.button("✅ เริ่มเกม") and len(names) == num_players:
        st.session_state.players = names
        st.session_state.active_players = names.copy()
        st.session_state.scores = {name: 0 for name in names}
        st.session_state.total_rounds = total_rounds
        st.session_state.rounds_left = total_rounds * len(names)
        st.session_state.phase = 'set_answer'
        st.rerun()

# --- SETTING SECRET ANSWER ---
elif st.session_state.phase == 'set_answer':
    owner = st.session_state.players[st.session_state.current_owner_idx]
    st.subheader(f"👑 {owner} ตั้งคำตอบ ลับ")
    st.session_state.answer = st.text_input("คำตอบลับของคุณ (จะถูกซ่อนไว้)", type="password")

    if st.button("🔒 ล็อคคำตอบและเริ่มรอบ") and st.session_state.answer:
        st.session_state.phase = 'playing'
        st.session_state.asking_queue = [i for i in range(len(st.session_state.players)) if i != st.session_state.current_owner_idx]
        st.session_state.current_turn_idx = st.session_state.asking_queue[0]
        st.session_state.eliminated = []
        st.session_state.question_history = []
        st.session_state.total_questions = 0
        st.session_state.ask_count = {name: 0 for name in st.session_state.players}
        st.session_state.last_question = None
        st.rerun()

# --- GAMEPLAY ---
elif st.session_state.phase == 'playing':
    st.subheader(f"🧩 ดูที่พวกมันถามดิ  ({st.session_state.total_questions}/{st.session_state.max_questions})")
    for q in st.session_state.question_history:
        with st.container():
            st.markdown(f"""<div style='background-color:#ffe8cc;padding:15px;border-radius:12px;font-size:18px'>
            <b>❓ {q}</b>
            </div>""", unsafe_allow_html=True)

    current_player = st.session_state.players[st.session_state.current_turn_idx]
    owner = st.session_state.players[st.session_state.current_owner_idx]

    if current_player in st.session_state.eliminated:
        next_idx = (st.session_state.asking_queue.index(st.session_state.current_turn_idx) + 1) % len(st.session_state.asking_queue)
        st.session_state.current_turn_idx = st.session_state.asking_queue[next_idx]
        st.rerun()

    st.markdown(f"### 🕹️ ตาไอ้ :  **{current_player}**  อ่ะ")
    action = st.radio("จะถามหรือจะตอบ เอาสักอย่าง :", ["ถาม", "ตอบ"], key=f"action_{st.session_state.current_turn_idx}")

    if action == "ถาม" and st.session_state.ask_count[current_player] < 5:
        with st.form(f"ask_form_{st.session_state.current_turn_idx}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                question = st.text_input("คำถามของคุณ:", key=f"question_input_{current_player}")
            with col2:
                st.markdown("<br><b>ใช่หรือไม่?</b>", unsafe_allow_html=True)
            submit_q = st.form_submit_button("ถาม")

        if submit_q and question.strip():
            st.session_state.last_question = question.strip()
            st.session_state.phase = 'owner_answer'
            st.rerun()

    elif action == "ตอบ":
        with st.form(f"answer_form_{st.session_state.current_turn_idx}"):
            guess = st.text_input("พิมพ์คำตอบของคุณ")
            submit_a = st.form_submit_button("ตอบ")

        if submit_a and guess.strip():
            if guess.strip().lower() == st.session_state.answer.strip().lower():
                st.success(f"🎉 {current_player} ตอบถูก! ได้ 1 คะแนน")
                st.session_state.scores[current_player] += 1
                st.session_state.phase = 'result'
            else:
                st.warning("❌ ผิด! คุณตกรอบนี้แล้ว")
                st.session_state.eliminated.append(current_player)
                idx = st.session_state.asking_queue.index(st.session_state.current_turn_idx)
                st.session_state.current_turn_idx = st.session_state.asking_queue[(idx + 1) % len(st.session_state.asking_queue)]
            st.rerun()

# --- OWNER ANSWERS THE QUESTION ---
elif st.session_state.phase == 'owner_answer':
    st.subheader("👑 เจ้าของคำตอบ กรุณาตอบคำถาม")
    question_display = st.session_state.last_question + " ใช่หรือไม่?"
    st.markdown(f"""<div style='background-color:#fff3cd;padding:20px;border-radius:12px;font-size:20px'>
    <b>❓ {question_display}</b>
    </div>""", unsafe_allow_html=True)

    choice = st.radio("เลือกคำตอบ:", ["ใช่", "ไม่ใช่"], key=f"owner_ans_{st.session_state.total_questions}")
    if st.button("✅ ยืนยันคำตอบ"):
        full_q = f"{question_display} → {choice}"
        st.session_state.question_history.append(full_q)
        current_player = st.session_state.players[st.session_state.current_turn_idx]
        st.session_state.total_questions += 1
        st.session_state.ask_count[current_player] += 1
        idx = st.session_state.asking_queue.index(st.session_state.current_turn_idx)
        st.session_state.current_turn_idx = st.session_state.asking_queue[(idx + 1) % len(st.session_state.asking_queue)]

        if all(count >= 5 for name, count in st.session_state.ask_count.items() if name != owner):
            st.session_state.phase = 'result'
        else:
            st.session_state.phase = 'playing'
        st.rerun()

# --- RESULT ---
elif st.session_state.phase == 'result':
    st.subheader("📊 คะแนนรวม:")
    for name, score in st.session_state.scores.items():
        st.markdown(f"- **{name}**: {score} คะแนน")

    if st.session_state.rounds_left > 1:
        st.session_state.rounds_left -= 1
        st.session_state.current_owner_idx = (st.session_state.current_owner_idx + 1) % len(st.session_state.players)
        if st.button("🔁 เริ่มรอบถัดไป"):
            st.session_state.phase = 'set_answer'
            st.rerun()
    else:
        st.success("🎉 เกมจบแล้ว!")
        if st.button("🔁 เริ่มใหม่ทั้งหมด"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
