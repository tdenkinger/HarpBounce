import streamlit as st
import time
import re

st.set_page_config(page_title="Harmonica Note Visualizer", layout="wide")

for key, val in [("playing", False), ("note_index", 0), ("notes", []), ("bpm", 120)]:
    if key not in st.session_state:
        st.session_state[key] = val

st.title("Harmonica Note Visualizer")

notes_input = st.text_area(
    "Enter notes (BPM=XX on its own line, then hole numbers: plain = blow, minus prefix = draw):",
    value="BPM=120\n4 -4 5 -5 6 -6 -7 6",
    height=120,
    disabled=st.session_state.playing,
)


def parse_input(text):
    notes = []
    bpm = 120
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        bpm_match = re.match(r"^\s*BPM\s*=\s*(\d+)\s*$", line, re.IGNORECASE)
        if bpm_match:
            bpm = int(bpm_match.group(1))
            continue
        for token in line.split():
            m = re.match(r"^(-?)(\d+)$", token)
            if m:
                is_draw = m.group(1) == "-"
                hole = int(m.group(2))
                if 1 <= hole <= 10:
                    notes.append({"hole": hole, "draw": is_draw, "token": token})
    return notes, bpm


if not st.session_state.playing:
    parsed_notes, parsed_bpm = parse_input(notes_input)
    st.session_state.notes = parsed_notes
    st.session_state.bpm = parsed_bpm

notes = st.session_state.notes
bpm = st.session_state.bpm

col1, col2, col3 = st.columns([1, 1, 5])
with col1:
    go_clicked = st.button(
        "GO",
        disabled=st.session_state.playing or len(notes) == 0,
        use_container_width=True,
    )
with col2:
    stop_clicked = st.button(
        "STOP",
        disabled=not st.session_state.playing,
        use_container_width=True,
    )

if go_clicked:
    st.session_state.playing = True
    st.session_state.note_index = 0
    st.rerun()

if stop_clicked:
    st.session_state.playing = False
    st.rerun()

if notes:
    if st.session_state.playing:
        current = notes[st.session_state.note_index]
        direction = "Draw" if current["draw"] else "Blow"
        st.caption(
            f"BPM: {bpm}  |  Note {st.session_state.note_index + 1}/{len(notes)}"
            f"  |  Hole {current['hole']} - {direction}"
        )
    else:
        st.caption(f"BPM: {bpm}  |  {len(notes)} notes ready")
else:
    st.caption("No valid notes found — use hole numbers 1-10, prefix with - for draw notes")


def render_harmonica(active_hole=None, is_draw=None):
    holes_html = ""
    for hole in range(1, 11):
        is_active = active_hole == hole

        dot_html = (
            '<div style="width:18px;height:18px;background:#e00;border-radius:50%;margin:0 auto 6px;"></div>'
            if is_active
            else '<div style="width:18px;height:18px;margin:0 auto 6px;"></div>'
        )

        if is_active and not is_draw:
            hole_bg, hole_border, text_color = "#4477ee", "#2255bb", "white"
        elif is_active and is_draw:
            hole_bg, hole_border, text_color = "#ee5544", "#bb2211", "white"
        else:
            hole_bg, hole_border, text_color = "#d8d8d8", "#999", "#222"

        holes_html += f"""
        <div style="text-align:center;flex:1;min-width:44px;max-width:64px;">
            {dot_html}
            <div style="
                background:{hole_bg};
                border:3px solid {hole_border};
                border-radius:8px;
                padding:12px 4px;
                font-size:20px;
                font-weight:bold;
                color:{text_color};
                box-shadow:0 2px 5px rgba(0,0,0,0.25);
            ">{hole}</div>
        </div>"""

    note_label = ""
    if active_hole:
        direction = "DRAW" if is_draw else "BLOW"
        color = "#ee5544" if is_draw else "#4477ee"
        note_label = (
            f'<div style="color:{color};font-size:16px;font-weight:bold;'
            f'text-align:center;margin-top:14px;">'
            f"{direction} &mdash; Hole {active_hole}</div>"
        )

    return f"""
    <div style="
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        padding:24px 20px;
        border-radius:16px;
        margin:16px 0;
        box-shadow:0 4px 14px rgba(0,0,0,0.35);
    ">
        <div style="display:flex;gap:6px;justify-content:center;align-items:flex-end;">
            {holes_html}
        </div>
        {note_label}
    </div>"""


def render_sequence(notes, current_index):
    if not notes:
        return ""
    tokens_html = ""
    for i, note in enumerate(notes):
        if i == current_index:
            bg, color, weight = "#dd0000", "white", "bold"
        elif i < current_index:
            bg, color, weight = "#555", "#bbb", "normal"
        else:
            bg, color, weight = "#333", "#ddd", "normal"

        tokens_html += (
            f'<span style="display:inline-block;background:{bg};color:{color};'
            f"font-weight:{weight};padding:4px 9px;border-radius:4px;margin:3px;"
            f'font-family:monospace;font-size:15px;">{note["token"]}</span>'
        )

    return (
        '<div style="background:#1e1e1e;padding:12px 16px;border-radius:8px;'
        f'line-height:2.2;word-wrap:break-word;">{tokens_html}</div>'
    )


harmonica_slot = st.empty()

if st.session_state.playing and notes:
    current_note = notes[st.session_state.note_index]
    harmonica_slot.markdown(
        render_harmonica(current_note["hole"], current_note["draw"]),
        unsafe_allow_html=True,
    )
else:
    harmonica_slot.markdown(render_harmonica(), unsafe_allow_html=True)

if notes:
    st.markdown("**Note sequence:**")
    seq_slot = st.empty()
    active_idx = st.session_state.note_index if st.session_state.playing else -1
    seq_slot.markdown(render_sequence(notes, active_idx), unsafe_allow_html=True)

# Animation tick — sleep then advance and rerun
if st.session_state.playing and notes:
    time.sleep(60.0 / bpm)
    st.session_state.note_index = (st.session_state.note_index + 1) % len(notes)
    st.rerun()
