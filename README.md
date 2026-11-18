# Animal Guessing Game

A Streamlit app: the computer picks a secret animal and you find it by chatting.
Ask yes/no questions or guess at any time. An LLM answers in natural language and rates
how useful each of your questions was.

## Pages
- **Play** - chat game (`st.chat_input`, `st.chat_message`) with 20 turns, 3 hints and a
  win effects (balloons, sparkles, dancing paws, cheer) and lose effects (red light, low tone).
- **Stats** - games played and won, average guesses per game, Plotly bar chart of guesses per game
  (green = won, red = lost) and the guess-quality analysis: rating 1-5 with a reason for every message,
  quality per game, rating distribution and won-vs-lost comparison.

## How it works
- Python picks the animal and decides if a guess is correct (plurals and small typos are
  accepted). The LLM only answers and rates; its replies are checked so they never name the animal.
- Unusable LLM replies are retried once. Errors never crash the app.

## Files
`app.py` navigation, logo, background, music | `game.py` game logic and LLM calls | `effects.py` win/lose effects | `pages/play.py` | `pages/stats.py` | `assets/` logo, paw pattern, sounds

## Run locally
```
pip install -r requirements.txt
```
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, fill in the values,
then run `streamlit run app.py`.

## Deploy
Streamlit Community Cloud, main file `app.py`; paste the secrets under Settings > Secrets.

## Known limits
Stats are kept per browser session and reset on refresh.

## Who did what
(Max. 2 short sentences per contributor. Also state which tools, e.g. AI assistants,
you used, as your course requires.)
