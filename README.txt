# Naas

Nana as a Service is a language tutor that helps you practice the writing system of your target language. Nana gives you some words one at a time, then asks you to transliterate them. Then she'll check your work and give you some encouragement, including some phrases in your target language, but out of scope of your present studies.

---

## Project Structure

naas_root/
├─ naas/
│  ├─ __init__.py
│  ├─ api.py              # FastAPI app + routes
│  ├─ service.py          # Orchestrates DB + LLM
│  ├─ db_manager.py       # In-memory word database
│  ├─ llm_manager.py      # OpenAI client + prompt logic
│  ├─ word_entry.py       # WordEntry model
│  └─ check_response.py   # CheckResponse model
├─ schemes/
│  └─ armenian.py         # Example transliteration scheme
├─ prompts/
│  ├─ check_transliteration.yaml
│  ├─ word_batch.yaml
│  └─ nan_it_up.yaml
├─ requirements.txt
└─ README.md

---

## An Admission of Guilt

I got a little trigger happy with the copy and paste while producing, or should I say  midwifing this project. Part of my goal here was to experiment with using ChatGPT as a  coding assistant. The verdict: helpful but a little overbearing. Once I let it write one function, I had to let it rewrite all the functions that touched it, and the functions touching those, and the end result is a code base that I didn't exactly write, but I did  learn a lot from.

It's not how I usually do things, but it was an interesting experience.

One funny twist is that I somehow managed to delete the entire project (also not how I usually do things!), but then I just went back and asked ChatGPT to show me all the code it could remember. There were a few gaps but I was able to fill them in pretty easily. All in all, it's not as powerful as git, but I like the UI a lot more.

---

## Purpose

I had set up a chat in ChatGPT, which I was using to practice reading Armenian, and I wanted to see what it takes to replicate that functionality in a self-enclosed program.

So now we have NAAS--Nana As A Service. NAAS can be extended to work with different transliteration schemes, but I have stuck with Armenian for this toy project. I imagine that in its current state, it would work best with alphabetic systems, maybe abjads or syllabaries. An ideographic system would probably prohibitively expensive in terms of space, because I'm using an LLM for scoring and the prompt has to include the desired transliteration scheme.

---

## A Note on Using LLMs for Scoring

You shouldn't actually do it this way. I know because the LLM told me. Just kidding. I know because getting the LLMs to give consistent answers was much harder than simply hand rolling the transliteration logic and checking answers myself. So why do it this way? Well, the point was to learn.

---

## What I Learned

It helps to force the LLM to spell out its thought process, and to get it to do that, you have to physically provide the space for it to write out its thoughts! Otherwise it can and will hallucinate every aspect of the answer. It will tell you your answer was wrong, and the right answer was your answer! It will check the two answers, see that their identical, congratulate you for getting it right and then still mark it wrong. It will mark it right and then tell you to better. It's truly fascinating.

---
## Setup

1. Clone the repo

   git clone https://github.com/<your-username>/naas.git
   cd naas

2. Create a virtual environment

   python3 -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   # .venv\Scripts\activate    # Windows (PowerShell)

3. Install dependencies

   pip install --upgrade pip
   pip install -r requirements.txt

4. Set your OpenAI API key

   export OPENAI_API_KEY=sk-...   # macOS/Linux
   # setx OPENAI_API_KEY "sk-..." # Windows PowerShell

5. Run the server

   uvicorn naas.api:app --reload

   The app will be available at: http://127.0.0.1:8000

---

## Endpoints


### Healthcheck
GET /health
This just lets you know that Nana is listening.

### Word Management
GET /word/{language} 

Get a random active word of your language. If there are less than the required number of active words in memory, get a new batch from Nana. 

Active words are words that you have not yet transcribed correctly three times in a row.

Note that the only language currently supported is Armenian.

GET /dump/{language}

Show all the words in memory for the language, including whether the words are active and the number of correct tries. Note that correct tries is reset to 0 whenever you get it wrong.

### Transliteration Check
GET /check/{language}/{original}/{transliteration}

Checks whether your transliteration matches the original word in the language. Depending on whether your transliteration is right or wrong, Nana will either say something encouraging or offer a gentle correction. Either way, she will include a phrase in the language which is generally speaking not in your word list; she'll also give you a transliteration and gloss of this word, so that you get a little more exposure to your target language.

---

## Schemes

Currently, only Armenian is supported.

---

## Extensions

Jeez, where do I start?

# UI

Currently all interaction takes place through the URL bar. This is not how you do anything in real life. But if I wanted to build a webpage, I'd have to rely on ChatGPT way more than I really want to.

# Persistence

This is easy enough to do in principle, but if I wanted to support persistence, it would open up all sorts of questions about users and permissions that I frankly don't want to deal with.

# Support for Other Languages

On the one hand, we could just add more transliteration schemes. But what I think would be really fun is writing a prompt to ask Nana to provide a transliteration scheme in the correct format, then call the prompt and install the result. Validating the scheme opens up a whole can of worms, however.


# Fix Word Pool Size

Currently when the (active) word pool dips below a certain size, we ask Nana for a whole new batch of words, meaning that the size of the word pool varies between N and 2N-1. This doesn't please me. The solution is to add batches of new words to a buffer, then draw from the buffer whenever the word pool gets too small. Easy enough, but frankly I have other things to do.

---
