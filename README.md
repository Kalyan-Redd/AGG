# Animal Guessing Game

A Streamlit app: the computer picks a secret animal and you find it by chatting.
Ask yes/no questions or guess at any time. An LLM (via the Groq API) answers in natural
language and rates how useful each of your questions was.

## Live App: https://animalgame.streamlit.app/

## Pages
- **Play** - chat game (`st.chat_input`, `st.chat_message`) with 20 turns, 3 hints and
  win effects (balloons, sparkles, dancing paws, cheer) and lose effects (red light, low tone).
- **Stats** - games played and won, average guesses per game, Plotly bar chart of guesses per
  game (green = won, red = lost) and the guess-quality analysis: rating 1-5 with a reason for
  every message, quality per game, rating distribution and won-vs-lost comparison.

## How it works
- Python picks the animal and decides if a guess is correct (plurals and small typos are
  accepted). The LLM (served by Groq) only answers and rates; its replies are checked so they
  never name the animal.
- Unusable LLM replies are retried once. Errors never crash the app.

## Files
`app.py` navigation, logo, background, music | `game.py` game logic and Groq LLM calls |
`effects.py` win/lose effects | `pages/play.py` Play page | `pages/stats.py` Stats page |
`assets/` logo, paw pattern, sounds | `requirements.txt` dependencies

## Run locally
```
pip install -r requirements.txt
```
Create a free API key at console.groq.com. Copy `.streamlit/secrets.toml.example` to
`.streamlit/secrets.toml`, fill in the values (including your Groq API key), then run
`streamlit run app.py`.

## Deploy
Streamlit Community Cloud, main file `app.py`; paste the secrets under Settings > Secrets.

## Known limits
Stats are kept per browser session and reset on refresh.

## Who did what
Developed by Kalyan Reddy Gaddam
