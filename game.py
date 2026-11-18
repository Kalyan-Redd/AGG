"""Game logic: state, LLM calls and answer checking."""
import json
import random
import re
from difflib import SequenceMatcher

import streamlit as st
from openai import OpenAI

MAX_TURNS = 20        # a game is lost after this many questions/guesses
MAX_HINTS = 3         # hints per game
MAX_INPUT_CHARS = 300
CALL_LIMIT = 300      # LLM calls per visitor session, protects the shared API key

ANIMALS = [
    "dog", "cat", "elephant", "giraffe", "dolphin", "penguin", "kangaroo", "owl",
    "shark", "frog", "snake", "horse", "bee", "octopus", "bat", "crocodile",
    "rabbit", "eagle", "whale", "turtle", "lion", "panda", "camel", "butterfly",
    "spider", "squirrel", "flamingo", "hedgehog",
]

# The LLM only talks to the player and describes the message. Python decides who wins.
SYSTEM_PROMPT = """You are the host of an animal guessing game. The secret animal is: {animal}.
The player tries to find it with questions or guesses. Answer every message, whatever it is about.

How to write the "answer" (max 2 sentences, friendly):
- Questions about the animal (habitat, size, diet, colour, sounds, legs, comparisons with
  other animals ...): answer truthfully for a typical adult of the species. Start with
  Yes / No / Sometimes / Not really (or a short fact), plus at most one tiny remark.
- Wrong guess: say it is not that animal and add a vague hint.
- Off-topic, nonsense or not a question: answer politely and invite a yes/no question.
- NEVER write the secret animal's name or its plural unless the player just guessed it
  correctly. Say "it" or "this animal" instead.
- Reply in the language the player writes in.

Reply ONLY with a JSON object with these keys:
- "answer": the reply described above.
- "guessed_animal": the animal the player names as their final answer (singular, lowercase,
  translated to English), or null. Questions ("Is it bigger than a dog?"), comparisons and
  groups ("a mammal") are NOT guesses.
- "quality": integer 1-5, how useful the message was for narrowing down the animal.
  1 = nonsense, off-topic or repeated; 2 = very vague; 3 = decent; 4 = good, splits the
  possibilities well; 5 = excellent (or a correct guess).
- "reason": one short sentence in English explaining the quality rating."""


# ---------- state ----------

def new_game():
    """Start a round with a random secret animal (chosen by Python, not the LLM)."""
    st.session_state.game = {
        "animal": random.choice(ANIMALS),
        "messages": [],   # chat history: {"role", "content"}
        "log": [],        # one rated entry per turn, used on the Stats page
        "hints": 0,
        "over": False,
        "won": False,
        "celebrated": False,
    }


def init_state():
    """Create session state on the first run."""
    st.session_state.setdefault("finished_games", [])
    if "game" not in st.session_state:
        new_game()


def finish_game(won):
    """End the game and store it for the Stats page (only once)."""
    game = st.session_state.game
    if not game["over"]:
        game["over"], game["won"] = True, won
        st.session_state.finished_games.append(game)


# ---------- answer checking ----------

def forms(animal):
    """The animal's name plus simple plural forms."""
    plural = animal[:-1] + "ies" if animal.endswith("y") else animal + "s"
    return {animal, plural, animal + "es"}


def mentions(text, animal):
    """True if the text contains the animal's name or a plural as a whole word."""
    return re.search(r"\b(" + "|".join(forms(animal)) + r")\b", text.lower()) is not None


def matches(guess, animal):
    """Forgiving comparison: ignores case, articles, plurals and small typos."""
    words = guess.lower().strip(" .!?").split()
    if words and words[0] in ("a", "an", "the"):
        words = words[1:]
    guess = " ".join(words)
    if not guess or guess[0] != animal[0]:
        return False
    return guess in forms(animal) or SequenceMatcher(None, guess, animal).ratio() >= 0.75


# ---------- LLM ----------

@st.cache_resource
def get_client():
    """One shared API client; credentials come from st.secrets."""
    return OpenAI(api_key=st.secrets["API_KEY"], base_url=st.secrets["BASE_URL"])


def _chat(system, user, temperature=0.3, history=()):
    """One LLM call, returns the reply text."""
    st.session_state.calls = st.session_state.get("calls", 0) + 1
    if st.session_state.calls > CALL_LIMIT:
        raise RuntimeError("call limit reached")
    response = get_client().chat.completions.create(
        model=st.secrets["MODEL"],
        messages=[{"role": "system", "content": system}, *history,
                  {"role": "user", "content": user}],
        temperature=temperature,
    )
    return response.choices[0].message.content


def _parse(text):
    """Extract and validate the JSON reply (tolerates extra text around it)."""
    data = json.loads(text[text.index("{"): text.rindex("}") + 1])
    guess = data.get("guessed_animal")
    result = {
        "answer": str(data.get("answer", "")).strip(),
        "guess": guess if isinstance(guess, str) else "",
        "quality": min(5, max(1, int(data.get("quality", 1)))),
        "reason": str(data.get("reason", "")),
    }
    if not result["answer"]:
        raise ValueError("empty answer")
    return result


def ask(system, message, history):
    """Ask the LLM and parse its reply. One retry if the reply is unusable."""
    for _ in range(2):
        try:
            return _parse(_chat(system, message, history=history))
        except (ValueError, TypeError, KeyError):   # bad JSON, missing fields ...
            continue
    raise ValueError("no usable reply from the LLM")


def evaluate(message):
    """Rate and answer the player's message. Never raises, never leaks the animal."""
    game = st.session_state.game
    animal = game["animal"]
    history = game["messages"][-8:]   # recent context for follow-up questions
    system = SYSTEM_PROMPT.format(animal=animal)
    try:
        result = ask(system, message, history)
        # Leak check: the name may only appear in a correct guess or if the player wrote it
        if not matches(result["guess"], animal) and mentions(result["answer"], animal) \
                and not mentions(message, animal):
            result = ask(system + "\nYour last answer revealed the animal's name. "
                         "Answer again without it.", message, history)
            if mentions(result["answer"], animal):
                result["answer"] = "I can't answer that without giving it away. Try another question!"
        result["won"] = matches(result["guess"], animal)
        result["ok"] = True
        return result
    except Exception as e:   # API down, quota, missing secrets ... -> friendly message, no crash
        details = f"\n\n(Details: {type(e).__name__}: {e})" if st.secrets.get("DEBUG") else ""
        return {"answer": "Sorry, I couldn't reach the host. Please try again." + details,
                "quality": 1, "reason": "", "won": False, "ok": False}


def take_turn(message):
    """Play one turn: evaluate, update chat and log, check for win or loss."""
    game = st.session_state.game
    result = evaluate(message)
    if result["ok"]:   # failed API calls are not counted as turns
        game["log"].append({"turn": len(game["log"]) + 1, "message": message,
                            "quality": result["quality"], "reason": result["reason"]})
    game["messages"] += [{"role": "user", "content": message},
                         {"role": "assistant", "content": result["answer"]}]
    if result["won"]:
        finish_game(True)
    elif len(game["log"]) >= MAX_TURNS:
        finish_game(False)


def get_hint():
    """One vague hint from the LLM, or None if it fails or names the animal."""
    game = st.session_state.game
    earlier = [m["content"] for m in game["messages"] if m["content"].startswith("Hint:")]
    prompt = (f"You host an animal guessing game. The secret animal is: {game['animal']}. "
              "Give ONE short, vague hint (max 15 words). Never say the animal's name. "
              f"Do not repeat these earlier hints: {earlier}")
    try:
        hint = _chat(prompt, "Give me a hint.", temperature=0.7).strip()
        return hint if hint and not mentions(hint, game["animal"]) else None
    except Exception:
        return None
