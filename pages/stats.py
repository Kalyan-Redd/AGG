"""Stats page: results, guesses per game and guess quality."""
from statistics import mean

import plotly.graph_objects as go
import streamlit as st

GREEN, RED = "#2F6F4F", "#B5483A"
SCALE = ["#B5483A", "#D98A3D", "#E3C14B", "#8DB255", "#2F6F4F"]   # rating 1 (bad) to 5 (good)

games = st.session_state.finished_games
st.title("Stats")

if not games:
    st.info("No finished games yet. Play a round first!")
    st.stop()

# Numbers behind the charts
numbers = [str(i) for i in range(1, len(games) + 1)]
guesses = [len(g["log"]) for g in games]
quality = [mean(t["quality"] for t in g["log"]) if g["log"] else None for g in games]
ratings = [t["quality"] for g in games for t in g["log"]]


def average(selected):
    """Average rating of the given games as text."""
    values = [t["quality"] for g in selected for t in g["log"]]
    return f"{mean(values):.1f}" if values else "-"


def show(fig, x_title, y_title):
    """Apply one clean style to every chart and draw it."""
    fig.update_layout(xaxis_title=x_title, yaxis_title=y_title, showlegend=False,
                      margin=dict(t=10, b=10), font=dict(family="serif", size=14),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(type="category")
    st.plotly_chart(fig)


col1, col2, col3, col4 = st.columns(4)
col1.metric("Games played", len(games))
col2.metric("Games won", sum(g["won"] for g in games))
col3.metric("Average guesses per game", f"{mean(guesses):.1f}")
col4.metric("Average guess quality", f"{mean(ratings):.1f} / 5" if ratings else "-")

st.subheader("Guesses per game")
st.caption("Green: animal found. Red: lost or gave up. Hover a bar to see the animal.")
show(go.Figure(go.Bar(x=numbers, y=guesses, text=guesses, textposition="outside",
                      marker_color=[GREEN if g["won"] else RED for g in games],
                      hovertext=[g["animal"] for g in games],
                      hovertemplate="Game %{x}: %{y} guesses<br>%{hovertext}<extra></extra>")),
     "Game", "Guesses")

st.subheader("Guess quality")
st.write("Every question or guess is rated from 1 to 5 by the LLM, depending on how much it "
         "helps to find the animal (1 = nonsense or repeated, 3 = decent, 5 = excellent). "
         "Every single rating is listed below with its reason, so you can check it yourself.")
st.caption(f"Average quality in won games: {average(g for g in games if g['won'])}  |  "
           f"in lost games: {average(g for g in games if not g['won'])}")

if ratings:
    left, right = st.columns(2)
    with left:
        st.markdown("**Average quality per game**")
        fig = go.Figure(go.Scatter(x=numbers, y=quality, mode="lines+markers",
                                   line_color=GREEN, marker_size=10))
        fig.update_yaxes(range=[0.5, 5.5])
        show(fig, "Game", "Average rating")
    with right:
        st.markdown("**How often each rating was given**")
        show(go.Figure(go.Bar(x=["1", "2", "3", "4", "5"], y=[ratings.count(r) for r in range(1, 6)],
                              marker_color=SCALE)), "Rating", "Messages")

    # Plain markdown table (no dataframe widget needed); "|" and line breaks would break it
    def clean(text):
        return str(text).replace("|", "/").replace("\n", " ")

    rows = [f"| {i} | {t['turn']} | {clean(t['message'])} | {t['quality']} | {clean(t['reason'])} |"
            for i, g in enumerate(games, start=1) for t in g["log"]]
    with st.expander("Every rating with its reason", expanded=True):
        st.markdown("\n".join(["| Game | Turn | Your message | Quality | Why |",
                               "|---|---|---|---|---|", *rows]))
