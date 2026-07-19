"""MCQ Practice App — Streamlit UI for CSV-based quiz practice."""

from __future__ import annotations

import html
import re
from pathlib import Path

import pandas as pd
import streamlit as st

CSV_PATH = Path(__file__).parent / "questions.csv"
OPTION_COLS = {
    "A": "Option A",
    "B": "Option B",
    "C": "Option C",
    "D": "Option D",
}

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root {
  --ink: #1a2b3c;
  --muted: #5a6d7e;
  --paper: #f3f7f9;
  --card: #ffffff;
  --accent: #0d7377;
  --accent-soft: #e6f4f4;
  --accent-deep: #095456;
  --correct: #1b7a4e;
  --correct-bg: #e8f6ee;
  --wrong: #b42318;
  --wrong-bg: #fef3f2;
  --border: #d5e0e6;
  --shadow: 0 8px 28px rgba(26, 43, 60, 0.08);
}

html, body, [class*="css"] {
  font-family: "DM Sans", sans-serif;
  color: var(--ink);
}

.stApp {
  background:
    radial-gradient(ellipse 80% 50% at 10% -10%, #d4ecec 0%, transparent 55%),
    radial-gradient(ellipse 60% 40% at 100% 0%, #e8eef3 0%, transparent 50%),
    linear-gradient(180deg, #eef4f6 0%, var(--paper) 40%, #e8f0f2 100%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }

.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 760px !important;
}

/* —— Brand / headers —— */
.app-brand {
  font-family: "Fraunces", Georgia, serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.02em;
  margin: 0 0 0.25rem 0;
  line-height: 1.2;
}
.app-sub {
  color: var(--muted);
  font-size: 0.98rem;
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
}

.hero-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2rem 1.75rem;
  box-shadow: var(--shadow);
  margin-bottom: 1rem;
}
.hero-card h2 {
  font-family: "Fraunces", Georgia, serif;
  font-size: 1.55rem;
  margin: 0 0 0.75rem 0;
  color: var(--ink);
}
.hero-stats {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin: 1.25rem 0 1.5rem 0;
}
.stat-chip {
  background: var(--accent-soft);
  color: var(--accent-deep);
  border-radius: 12px;
  padding: 0.55rem 0.9rem;
  font-size: 0.88rem;
  font-weight: 600;
}

/* —— Progress —— */
.progress-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.35rem;
}
.progress-label {
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--ink);
}
.progress-count {
  font-size: 0.85rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

/* —— Question —— */
.q-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 1rem 0 0.85rem 0;
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 10px;
  padding: 0.35rem 0.7rem;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}
.badge-sno {
  background: #e8eef3;
  color: var(--muted);
}
.badge-single {
  background: var(--accent-soft);
  color: var(--accent-deep);
}
.badge-multi {
  background: #fff4e5;
  color: #9a5b00;
}

.question-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.35rem 1.4rem;
  box-shadow: var(--shadow);
  margin-bottom: 1.1rem;
}
.question-text {
  font-size: 1.08rem;
  font-weight: 500;
  line-height: 1.65;
  color: var(--ink);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.options-heading {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  margin: 0.25rem 0 0.65rem 0;
}

/* —— Radio / checkbox as option cards —— */
div[role="radiogroup"] > label,
div[data-testid="stCheckbox"] {
  background: var(--card) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 0.85rem 1rem !important;
  margin-bottom: 0.55rem !important;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 2px 8px rgba(26, 43, 60, 0.04);
}
div[role="radiogroup"] > label:hover,
div[data-testid="stCheckbox"]:hover {
  border-color: var(--accent) !important;
  background: var(--accent-soft) !important;
  box-shadow: 0 4px 14px rgba(13, 115, 119, 0.12);
}
div[role="radiogroup"] > label[data-checked="true"],
div[data-testid="stCheckbox"]:has(input:checked) {
  border-color: var(--accent) !important;
  background: var(--accent-soft) !important;
}
div[role="radiogroup"] label p,
div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] p {
  font-size: 0.98rem !important;
  line-height: 1.5 !important;
  color: var(--ink) !important;
  font-weight: 500 !important;
}
div[role="radiogroup"] {
  gap: 0 !important;
}

/* —— Feedback —— */
.feedback {
  border-radius: 14px;
  padding: 1rem 1.15rem;
  margin: 0.85rem 0 1rem 0;
  border: 1.5px solid transparent;
}
.feedback-ok {
  background: var(--correct-bg);
  border-color: #a6e0bf;
  color: var(--correct);
}
.feedback-bad {
  background: var(--wrong-bg);
  border-color: #f5c2c0;
  color: var(--wrong);
}
.feedback-title {
  font-weight: 700;
  font-size: 1.05rem;
  margin: 0 0 0.35rem 0;
}
.feedback-body {
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
  color: var(--ink);
}
.correct-list {
  margin: 0.55rem 0 0 0;
  padding: 0;
  list-style: none;
}
.correct-list li {
  background: #fff;
  border-radius: 10px;
  padding: 0.55rem 0.75rem;
  margin-top: 0.4rem;
  border: 1px solid #c8e6d4;
  font-size: 0.92rem;
  color: var(--ink);
}
.letter-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.55rem;
  height: 1.55rem;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  font-size: 0.8rem;
  margin-right: 0.55rem;
  flex-shrink: 0;
  vertical-align: middle;
}

/* —— Results (hardcoded colors: Streamlit theme was washing out text) —— */
.score-card {
  background: #ffffff;
  border: 1px solid #d5e0e6;
  border-radius: 20px;
  padding: 1.75rem;
  text-align: center;
  box-shadow: var(--shadow);
  margin-bottom: 1.25rem;
  color: #1a2b3c !important;
}
.score-card h2 {
  font-family: "Fraunces", Georgia, serif;
  margin: 0 0 0.5rem 0;
  color: #1a2b3c !important;
  font-size: 1.45rem !important;
  font-weight: 700 !important;
}
.score-big {
  font-family: "Fraunces", Georgia, serif;
  font-size: 2.6rem;
  font-weight: 700;
  color: #095456 !important;
  margin: 0.35rem 0;
  line-height: 1;
}
.score-pct {
  color: #3d5163 !important;
  font-size: 1rem;
  margin-bottom: 0.75rem;
}

.review-card {
  background: #ffffff !important;
  border: 1px solid #d5e0e6;
  border-radius: 16px;
  padding: 1.15rem 1.25rem;
  margin-bottom: 0.85rem;
  box-shadow: 0 2px 10px rgba(26, 43, 60, 0.05);
  color: #1a2b3c !important;
}
.review-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.65rem;
  color: #1a2b3c !important;
}
.review-head strong {
  color: #1a2b3c !important;
  font-size: 1rem !important;
}
.review-q {
  font-size: 0.98rem !important;
  line-height: 1.55 !important;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0 0 0.75rem 0;
  font-weight: 500 !important;
  color: #1a2b3c !important;
}
.opt-row {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  padding: 0.55rem 0.7rem;
  border-radius: 10px;
  margin-bottom: 0.4rem;
  font-size: 0.92rem !important;
  line-height: 1.45 !important;
  border: 1px solid transparent;
  color: #1a2b3c !important;
}
.opt-row span {
  color: #1a2b3c !important;
}
.opt-neutral { background: #f0f4f6; border-color: #d5e0e6; }
.opt-right { background: #e8f6ee; border-color: #a6e0bf; }
.opt-wrong-pick { background: #fef3f2; border-color: #f5c2c0; }
.review-meta {
  margin: 0.7rem 0 0 0 !important;
  font-size: 0.88rem !important;
  color: #3d5163 !important;
  line-height: 1.45 !important;
}
.review-meta strong {
  color: #1a2b3c !important;
}
.tag {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-radius: 8px;
  padding: 0.3rem 0.55rem;
}
.tag-ok { background: #e8f6ee; color: #1b7a4e !important; }
.tag-bad { background: #fef3f2; color: #b42318 !important; }
.tag-skip { background: #e8eef3; color: #3d5163 !important; }

/* Streamlit markdown headings / captions on results */
h1, h2, h3, h4, [data-testid="stMarkdownContainer"] h3 {
  color: #1a2b3c !important;
}
[data-testid="stCaption"] p,
.stCaption, small {
  color: #3d5163 !important;
}
.letter-pill {
  color: #ffffff !important;
  background: #0d7377 !important;
}
.question-text,
.question-card,
.hero-card,
.hero-card h2,
.hero-card p,
.app-brand {
  color: #1a2b3c !important;
}
.app-sub,
.score-pct,
.options-heading {
  color: #3d5163 !important;
}

/* Buttons */
.stButton > button {
  border-radius: 12px !important;
  font-weight: 600 !important;
  padding: 0.65rem 1.1rem !important;
  color: #1a2b3c !important;
  background: #ffffff !important;
  border: 1.5px solid #d5e0e6 !important;
}
.stButton > button p,
.stButton > button span,
.stButton > button div {
  color: inherit !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: #0d7377 !important;
  border-color: #0d7377 !important;
  color: #ffffff !important;
}
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"] {
  background: #ffffff !important;
  border-color: #d5e0e6 !important;
  color: #1a2b3c !important;
}
.stButton > button:hover,
.stButton > button:focus,
.stButton > button:active,
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover,
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
  transform: none !important;
  box-shadow: none !important;
  opacity: 1 !important;
  background: inherit !important;
  border-color: inherit !important;
  color: inherit !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover,
.stButton > button[kind="primary"]:focus,
.stButton > button[data-testid="baseButton-primary"]:focus,
.stButton > button[kind="primary"]:active,
.stButton > button[data-testid="baseButton-primary"]:active {
  background: #0d7377 !important;
  border-color: #0d7377 !important;
  color: #ffffff !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover,
.stButton > button:not([kind="primary"]):hover,
.stButton > button[kind="secondary"]:focus,
.stButton > button[data-testid="baseButton-secondary"]:focus,
.stButton > button:not([kind="primary"]):focus,
.stButton > button[kind="secondary"]:active,
.stButton > button[data-testid="baseButton-secondary"]:active,
.stButton > button:not([kind="primary"]):active {
  background: #ffffff !important;
  border-color: #d5e0e6 !important;
  color: #1a2b3c !important;
}

section[data-testid="stSidebar"] .stButton > button {
  font-size: 0.82rem !important;
  padding: 0.45rem 0.25rem !important;
  min-height: 2.4rem !important;
}

section[data-testid="stSidebar"] {
  background: #f7fbfb;
}
</style>
"""


def parse_correct_answers(raw: object) -> set[str]:
    """Parse values like 'B', 'A, D', or '"A, B"' into a set of option letters."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return set()
    text = str(raw).strip().strip('"').strip("'")
    letters = re.findall(r"[A-Da-d]", text)
    return {letter.upper() for letter in letters}


def soft_format_question(text: str) -> str:
    """Light cleanup so dense exam text is easier to scan."""
    text = text.strip()
    # Space after common statement numbers like "01:" when jammed into prose
    text = re.sub(r"(?<!\n)(\d{2}:)", r"\n\1", text)
    # Break before System.debug / common Apex cues when glued together
    text = re.sub(r"(?<=[)}\]])(?=System\.)", "\n", text)
    text = re.sub(r"(?<=\))(?=while\s*\()", "\n", text, flags=re.IGNORECASE)
    return text.strip()


@st.cache_data
def load_questions(path: str) -> list[dict]:
    df = pd.read_csv(path)
    questions: list[dict] = []

    for idx, row in df.iterrows():
        options: dict[str, str] = {}
        for key, col in OPTION_COLS.items():
            value = row.get(col)
            if value is None or (isinstance(value, float) and pd.isna(value)):
                continue
            text = str(value).strip()
            if text:
                options[key] = text

        correct = parse_correct_answers(row.get("Correct Answers"))
        correct = {c for c in correct if c in options}

        num_correct = row.get("Number of correct answer")
        try:
            expected_count = int(num_correct) if not pd.isna(num_correct) else len(correct)
        except (TypeError, ValueError):
            expected_count = len(correct)

        questions.append(
            {
                "index": int(idx),
                "sno": row.get("SNO", idx + 1),
                "content": soft_format_question(str(row.get("Question Content", ""))),
                "options": options,
                "correct": correct,
                "num_correct": expected_count if expected_count > 0 else len(correct),
            }
        )

    return questions


def init_state(total: int) -> None:
    defaults = {
        "q_index": 0,
        "answers": {},
        "checked": {},
        "started": False,
        "finished": False,
        "ended_early": False,
        "total": total,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_quiz() -> None:
    st.session_state.q_index = 0
    st.session_state.answers = {}
    st.session_state.checked = {}
    st.session_state.started = False
    st.session_state.finished = False
    st.session_state.ended_early = False


def is_correct(selected: set[str], correct: set[str]) -> bool:
    return selected == correct


def format_letters(letters: set[str] | list[str]) -> str:
    return ", ".join(sorted(letters)) if letters else "—"


def option_label(key: str, text: str) -> str:
    return f"{key}  ·  {text}"


def render_start(total: int) -> None:
    st.markdown('<p class="app-brand">MCQ Practice</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="app-sub">Practice at your pace. Check each answer as you go, '
        "then review everything at the end.</p>",
        unsafe_allow_html=True,
    )

    single_hint = "One answer → tap a single option"
    multi_hint = "Multiple answers → tick every correct option"

    st.markdown(
        f"""
        <div class="hero-card">
          <h2>Ready when you are</h2>
          <p style="color:var(--muted);margin:0;line-height:1.55;">
            Read the question, pick your answer(s), then press
            <strong>Check Answer</strong>. You’ll see if you’re right before moving on.
          </p>
          <div class="hero-stats">
            <span class="stat-chip">{total} questions</span>
            <span class="stat-chip">{single_hint}</span>
            <span class="stat-chip">{multi_hint}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Start Practice →", type="primary", use_container_width=True):
        st.session_state.started = True
        st.rerun()


def end_practice_early() -> None:
    st.session_state.finished = True
    st.session_state.ended_early = True
    st.rerun()


def render_question_navigation(questions: list[dict]) -> None:
    """Show a clickable question grid and preserve the current practice state."""
    st.sidebar.divider()
    st.sidebar.markdown("### Questions")

    answered = len(st.session_state.checked)
    st.sidebar.caption(
        f"{answered} answered · {len(questions) - answered} remaining"
    )
    st.sidebar.caption("✓ Correct  ·  ✕ Wrong  ·  Number = unanswered")

    columns = st.sidebar.columns(4)
    current = st.session_state.q_index

    for index, question in enumerate(questions):
        attempted = index in st.session_state.checked
        selected = st.session_state.answers.get(index, set())

        if attempted and is_correct(selected, question["correct"]):
            label = f"✓ {index + 1}"
            status = "Correct"
        elif attempted:
            label = f"✕ {index + 1}"
            status = "Wrong"
        else:
            label = str(index + 1)
            status = "Not answered"

        with columns[index % 4]:
            if st.button(
                label,
                key=f"nav_question_{index}",
                type="primary" if index == current else "secondary",
                use_container_width=True,
                help=f"Question {index + 1}: {status}",
            ):
                st.session_state.q_index = index
                st.session_state.started = True
                st.session_state.finished = False
                st.session_state.ended_early = False
                st.rerun()


def render_question(q: dict, q_index: int, total: int) -> None:
    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(
            f"""
            <div class="progress-row">
              <span class="progress-label">Question {q_index + 1}</span>
              <span class="progress-count">{q_index + 1} / {total}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_r:
        if st.button("Exit", use_container_width=True, key=f"exit_top_{q_index}", help="End practice and see review"):
            end_practice_early()

    progress = (q_index + 1) / total
    st.progress(progress)

    multi = q["num_correct"] > 1
    badge_class = "badge-multi" if multi else "badge-single"
    badge_text = (
        f"Select all {q['num_correct']} correct answers"
        if multi
        else "Select one correct answer"
    )

    safe_q = html.escape(q["content"])
    st.markdown(
        f"""
        <div class="q-meta">
          <span class="badge badge-sno">#{html.escape(str(q['sno']))}</span>
          <span class="badge {badge_class}">{badge_text}</span>
        </div>
        <div class="question-card">
          <p class="question-text">{safe_q}</p>
        </div>
        <p class="options-heading">Your options</p>
        """,
        unsafe_allow_html=True,
    )

    options = q["options"]
    keys = list(options.keys())
    already_checked = st.session_state.checked.get(q_index, False)
    previous = st.session_state.answers.get(q_index, set())
    selected: set[str] = set()

    if multi:
        for key in keys:
            checked = st.checkbox(
                option_label(key, options[key]),
                value=key in previous,
                key=f"cb_{q_index}_{key}",
                disabled=already_checked,
            )
            if checked:
                selected.add(key)
    else:
        default_index = None
        if previous:
            prev_letter = next(iter(previous))
            if prev_letter in keys:
                default_index = keys.index(prev_letter)
        choice = st.radio(
            "Your answer",
            options=keys,
            index=default_index,
            format_func=lambda k: option_label(k, options[k]),
            key=f"radio_{q_index}",
            disabled=already_checked,
            label_visibility="collapsed",
        )
        selected = {choice} if choice else set()

    st.write("")

    if not already_checked:
        check_col, exit_col = st.columns([3, 1])
        with check_col:
            if st.button(
                "Check Answer",
                type="primary",
                use_container_width=True,
                key=f"check_{q_index}",
            ):
                if len(selected) == 0:
                    st.warning("Please select an option before checking.")
                elif multi and len(selected) < q["num_correct"]:
                    st.warning(
                        f"This question needs {q['num_correct']} answers. "
                        "Select all that apply, then check again."
                    )
                else:
                    st.session_state.answers[q_index] = selected
                    st.session_state.checked[q_index] = True
                    st.rerun()
        with exit_col:
            if st.button("Exit", use_container_width=True, key=f"exit_mid_{q_index}"):
                end_practice_early()
        return

    stored = st.session_state.answers.get(q_index, set())
    ok = is_correct(stored, q["correct"])

    if ok:
        st.markdown(
            """
            <div class="feedback feedback-ok">
              <p class="feedback-title">Correct</p>
              <p class="feedback-body">Nice work — that matches the answer key.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        items = "".join(
            f'<li><span class="letter-pill">{html.escape(letter)}</span>'
            f"{html.escape(options[letter])}</li>"
            for letter in sorted(q["correct"])
            if letter in options
        )
        st.markdown(
            f"""
            <div class="feedback feedback-bad">
              <p class="feedback-title">Incorrect</p>
              <p class="feedback-body">
                Your pick: <strong>{html.escape(format_letters(stored))}</strong>
                &nbsp;·&nbsp; Correct: <strong>{html.escape(format_letters(q['correct']))}</strong>
              </p>
              <ul class="correct-list">{items}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    is_last = q_index >= total - 1
    label = "Finish & see review →" if is_last else "Next question →"
    next_col, exit_col = st.columns([3, 1])
    with next_col:
        if st.button(label, type="primary", use_container_width=True, key=f"next_{q_index}"):
            if is_last:
                st.session_state.finished = True
                st.session_state.ended_early = False
            else:
                st.session_state.q_index = q_index + 1
            st.rerun()
    with exit_col:
        if st.button("Exit", use_container_width=True, key=f"exit_after_{q_index}"):
            end_practice_early()


def render_results(questions: list[dict]) -> None:
    total = len(questions)
    score = 0
    attempted = 0
    results: list[dict] = []

    for i, q in enumerate(questions):
        attempted_q = i in st.session_state.checked
        selected = st.session_state.answers.get(i, set()) if attempted_q else set()
        ok = attempted_q and is_correct(selected, q["correct"])
        if attempted_q:
            attempted += 1
            if ok:
                score += 1
        results.append(
            {
                "q": q,
                "selected": selected,
                "ok": ok,
                "attempted": attempted_q,
                "index": i,
            }
        )

    denom = attempted if attempted else total
    pct = (score / denom * 100) if denom else 0
    ended_early = st.session_state.get("ended_early", False)
    title = "Practice ended early" if ended_early else "Practice complete"
    subtitle = (
        f"{score} correct of {attempted} attempted · {total - attempted} not answered"
        if ended_early or attempted < total
        else f"{pct:.0f}% correct"
    )

    st.markdown(
        f"""
        <div class="score-card" style="color:#1a2b3c;">
          <h2 style="color:#1a2b3c;margin:0 0 0.5rem 0;font-size:1.45rem;">{html.escape(title)}</h2>
          <div class="score-big" style="color:#095456;">{score} / {attempted if attempted else total}</div>
          <div class="score-pct" style="color:#3d5163;">{html.escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / denom if denom else 0)

    if st.button("Restart Practice", use_container_width=True):
        reset_quiz()
        st.rerun()

    st.markdown(
        """
        <h3 style="color:#1a2b3c;margin:1.25rem 0 0.35rem 0;">Full review</h3>
        <p style="color:#3d5163;font-size:0.9rem;margin:0 0 1rem 0;">
          Every question is listed with Correct, Wrong, or Not answered —
          wrong and skipped items show the correct answer.
        </p>
        """,
        unsafe_allow_html=True,
    )

    for item in results:
        q = item["q"]
        selected = item["selected"]
        ok = item["ok"]
        attempted_q = item["attempted"]
        n = item["index"] + 1

        if not attempted_q:
            tag = (
                '<span class="tag tag-skip" style="background:#e8eef3;color:#3d5163;">'
                "Not answered</span>"
            )
            your_ans = "—"
        elif ok:
            tag = (
                '<span class="tag tag-ok" style="background:#e8f6ee;color:#1b7a4e;">'
                "Correct</span>"
            )
            your_ans = format_letters(selected)
        else:
            tag = (
                '<span class="tag tag-bad" style="background:#fef3f2;color:#b42318;">'
                "Wrong</span>"
            )
            your_ans = format_letters(selected)

        safe_q = html.escape(q["content"])

        option_rows = []
        for key, text in q["options"].items():
            if key in q["correct"]:
                css = "opt-right"
                bg = "#e8f6ee"
                border = "#a6e0bf"
                note = " · correct answer"
            elif key in selected:
                css = "opt-wrong-pick"
                bg = "#fef3f2"
                border = "#f5c2c0"
                note = " · your pick"
            else:
                css = "opt-neutral"
                bg = "#f0f4f6"
                border = "#d5e0e6"
                note = ""
            option_rows.append(
                f'<div class="opt-row {css}" style="background:{bg};border:1px solid {border};'
                f'color:#1a2b3c;display:flex;gap:0.6rem;align-items:flex-start;'
                f'padding:0.55rem 0.7rem;border-radius:10px;margin-bottom:0.4rem;'
                f'font-size:0.92rem;line-height:1.45;">'
                f'<span class="letter-pill" style="background:#0d7377;color:#fff;'
                f'display:inline-flex;align-items:center;justify-content:center;'
                f'width:1.55rem;height:1.55rem;border-radius:8px;font-weight:700;'
                f'font-size:0.8rem;flex-shrink:0;">{html.escape(key)}</span>'
                f'<span style="color:#1a2b3c;">{html.escape(text)}{html.escape(note)}</span>'
                f"</div>"
            )

        st.markdown(
            f"""
            <div class="review-card" style="background:#fff;border:1px solid #d5e0e6;
                 border-radius:16px;padding:1.15rem 1.25rem;margin-bottom:0.85rem;color:#1a2b3c;">
              <div class="review-head" style="display:flex;justify-content:space-between;
                   align-items:center;gap:0.75rem;margin-bottom:0.65rem;">
                <strong style="color:#1a2b3c;font-size:1rem;">Question {n}</strong>
                {tag}
              </div>
              <p class="review-q" style="color:#1a2b3c;font-size:0.98rem;line-height:1.55;
                 white-space:pre-wrap;word-break:break-word;margin:0 0 0.75rem 0;font-weight:500;">
                {safe_q}
              </p>
              {"".join(option_rows)}
              <p class="review-meta" style="margin:0.7rem 0 0 0;font-size:0.88rem;color:#3d5163;">
                Your answer: <strong style="color:#1a2b3c;">{html.escape(your_ans)}</strong>
                &nbsp;·&nbsp;
                Correct: <strong style="color:#1a2b3c;">{html.escape(format_letters(q['correct']))}</strong>
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="MCQ Practice",
        page_icon="📝",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    uploaded = st.sidebar.file_uploader("Upload a different CSV (optional)", type=["csv"])
    if uploaded is not None:
        questions = load_questions(uploaded)
        st.sidebar.success(f"Loaded {len(questions)} questions from upload.")
    else:
        if not CSV_PATH.exists():
            st.error(f"CSV not found at `{CSV_PATH}`. Place `questions.csv` next to `app.py`.")
            st.stop()
        questions = load_questions(str(CSV_PATH))
        st.sidebar.caption(f"Using `{CSV_PATH.name}` ({len(questions)} questions)")

    if not questions:
        st.error("No questions found in the CSV.")
        st.stop()

    init_state(len(questions))

    if st.sidebar.button("Reset quiz"):
        reset_quiz()
        st.rerun()

    if st.session_state.started:
        render_question_navigation(questions)

    if not st.session_state.started:
        render_start(len(questions))
        return

    if st.session_state.finished:
        render_results(questions)
        return

    q_index = st.session_state.q_index
    if q_index < 0 or q_index >= len(questions):
        st.session_state.finished = True
        st.rerun()

    render_question(questions[q_index], q_index, len(questions))


if __name__ == "__main__":
    main()
