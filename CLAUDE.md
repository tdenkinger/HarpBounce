# HarpBounce

A Streamlit app that visualizes harmonica tab notation in real time, advancing a red dot over each note at a specified BPM.

## Running the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Note input format

Enter notes in the text area using this format:

```
BPM=120
4 -4 5 -5 6 -6 -7 6
```

- `BPM=<number>` — sets the tempo (default 120); must be on its own line
- Plain number (`4`) — blow note on that hole
- Minus-prefixed number (`-4`) — draw note on that hole
- Valid hole numbers: 1–10
- Multiple lines of notes are supported; blank lines are ignored
- Tokens that don't match the pattern are silently skipped

## Architecture

The entire app lives in `app.py` as a single-file Streamlit script. There are no external dependencies beyond Streamlit itself.

**Session state keys:**

| Key | Type | Purpose |
|-----|------|---------|
| `playing` | bool | Whether the animation loop is running |
| `note_index` | int | Index into the current note list |
| `notes` | list[dict] | Parsed notes: `{hole, draw, token}` |
| `bpm` | int | Tempo parsed from input |

**Animation loop:** Streamlit has no native animation primitive. Playback is implemented by sleeping for `60/bpm` seconds at the end of each script run and then calling `st.rerun()`, which advances `note_index` by one. The loop wraps around when it reaches the end of the sequence.

**Rendering:** The harmonica graphic and note-sequence strip are rendered as raw HTML via `st.markdown(..., unsafe_allow_html=True)` using inline styles. No external CSS or JS is loaded.

- `render_harmonica(active_hole, is_draw)` — returns the full harmonica HTML; hole turns blue for blow, red for draw; red dot appears above the active hole
- `render_sequence(notes, current_index)` — returns the token strip; current token is red, past tokens are dimmed

## Known limitations

- The STOP button takes effect on the next rerun, so there is up to one beat of latency after clicking it.
- The text area is disabled while playing to prevent the parsed note list from being replaced mid-playback.
- Half-step bends and overbends are not represented in the notation.
