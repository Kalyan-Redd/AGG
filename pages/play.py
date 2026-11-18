"""Play page: the chat game."""
import streamlit as st

import effects
from game import MAX_HINTS, MAX_INPUT_CHARS, MAX_TURNS, finish_game, get_hint, new_game, take_turn

game = st.session_state.game
turns = len(game["log"])

st.title("Guess the Animal")
st.caption("I am thinking of an animal. Ask yes/no questions or guess it.")
st.progress(turns / MAX_TURNS, text=f"Turn {turns} of {MAX_TURNS}")

# Buttons
hint_col, give_up_col, new_col = st.columns(3)
hints_left = MAX_HINTS - game["hints"]
if hint_col.button(f"Hint ({hints_left} left)", disabled=game["over"] or hints_left == 0):
    with st.spinner("Thinking of a hint..."):
        hint = get_hint()
    if hint:
        game["hints"] += 1
        game["messages"].append({"role": "assistant", "content": f"Hint: {hint}"})
    else:
        st.toast("Could not get a hint, please try again.")
    st.rerun()
if give_up_col.button("Give up", disabled=game["over"]):
    finish_game(won=False)
    st.rerun()
if new_col.button("New game"):
    new_game()
    st.rerun()

# Chat history (the script reruns on every interaction, so it is redrawn each time)
for m in game["messages"]:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# End of game: reveal the animal and show the win or lose effects
if game["over"]:
    first_time = not game["celebrated"]
    game["celebrated"] = True
    if game["won"]:
        st.success(f"Correct! It was a {game['animal']}. You needed {turns} turns.")
        effects.win(first_time)
    else:
        st.error(f"Game over. The animal was a {game['animal']}.")
        effects.lose(first_time)

# Player input
if prompt := st.chat_input("Ask a question or guess the animal...", disabled=game["over"]):
    prompt = prompt.strip()[:MAX_INPUT_CHARS]
    if prompt:   # ignore empty input
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"), st.spinner("Thinking..."):
            take_turn(prompt)
        st.rerun()
