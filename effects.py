"""Win and lose effects: sparkles, dancing paws and a red alarm light (pure CSS)."""
import random

import streamlit as st

CSS = """<style>
@keyframes dance { 0%, 100% { transform: translateY(0) rotate(-12deg); }
                   50% { transform: translateY(-24px) rotate(12deg); } }
@keyframes twinkle { 0%, 100% { opacity: 0; transform: scale(.3); }
                     50% { opacity: 1; transform: scale(1); } }
@keyframes alarm { 0%, 100% { opacity: 0; } 50% { opacity: 1; } }
.fx { position: relative; padding: 18px 0 8px; }
.dance { display: flex; justify-content: center; gap: 16px; }
.dance span { display: inline-block; animation: dance .8s ease-in-out infinite; }
.stars span { position: absolute; width: 20px; animation: twinkle 1.6s ease-in-out infinite; }
.alarm { position: fixed; inset: 0; z-index: 9999; pointer-events: none; opacity: 0;
    box-shadow: inset 0 0 180px 70px rgba(220, 30, 30, .8); animation: alarm .9s ease-in-out 4; }
</style>"""

PAW = ("<svg viewBox='-26 -26 52 52' width='46' height='46'><g fill='#2F6F4F'>"
       "<ellipse cy='12' rx='15' ry='12'/>"
       "<ellipse cx='-18' cy='-6' rx='5.5' ry='7.5' transform='rotate(-20 -18 -6)'/>"
       "<ellipse cx='-6' cy='-17' rx='5.5' ry='8'/><ellipse cx='6' cy='-17' rx='5.5' ry='8'/>"
       "<ellipse cx='18' cy='-6' rx='5.5' ry='7.5' transform='rotate(20 18 -6)'/></g></svg>")
STAR = ("<svg viewBox='0 0 20 20'><path d='M10 0L12 8L20 10L12 12L10 20L8 12L0 10L8 8Z' "
        "fill='#E3B341'/></svg>")


def win(first_time):
    """Sparkles and dancing paws stay on screen; balloons and the cheer play once."""
    rnd = random.Random(5)   # fixed seed: the stars stay in place on every rerun
    stars = "".join(f"<span style='left:{rnd.randint(2, 94)}%;top:{rnd.randint(0, 85)}%;"
                    f"animation-delay:{rnd.random() * 1.6:.2f}s'>{STAR}</span>" for _ in range(18))
    paws = "".join(f"<span style='animation-delay:{i * 0.15:.2f}s'>{PAW}</span>" for i in range(5))
    st.markdown(f"{CSS}<div class='fx'><div class='stars'>{stars}</div>"
                f"<div class='dance'>{paws}</div></div>", unsafe_allow_html=True)
    if first_time:
        st.balloons()
        st.audio("assets/cheer.wav", autoplay=True)


def lose(first_time):
    """A red light flashes four times and a low tone plays (once)."""
    if first_time:
        st.markdown(f"{CSS}<div class='alarm'></div>", unsafe_allow_html=True)
        st.audio("assets/lose.wav", autoplay=True)
