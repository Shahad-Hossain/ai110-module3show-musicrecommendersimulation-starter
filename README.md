# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

### How real-world recommenders work

Platforms like Spotify and YouTube blend two ideas. **Collaborative filtering** looks at behavior (plays, skips, saves, playlist adds) and recommends what similar listeners enjoyed, so it needs no knowledge of the song itself. **Content-based filtering** looks at song attributes (genre, mood, tempo, audio features) and recommends songs that resemble what you already like. Collaborative filtering finds surprising picks but struggles with brand-new songs; content-based handles new songs well but can trap you in a bubble of near-duplicates.

My version is purely **content-based**: with 10 songs and one user at a time there is no crowd to learn from. It prioritizes **how close a song's energy is to what the user wants**, then **mood**, then **genre**. Mood and energy capture how a song *feels*, while genre is a coarse label that, in this catalog, matches only one to three songs.

### Features

**`Song`** (from `data/songs.csv`): `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`. Only `genre`, `mood`, `energy` and `acousticness` are used in scoring. `tempo_bpm`, `danceability` and `valence` are loaded but left out, because they largely repeat what `energy` already says (high-energy songs here are also fast and danceable).

**`UserProfile`**: `favorite_genre`, `favorite_mood`, `target_energy` (0.0 to 1.0) and `likes_acoustic` (bool).

### Algorithm Recipe (the Scoring Rule)

Each song gets a score from 0 to 5.0 points, the sum of four parts:

| Part | Max points | How it is computed |
|---|---|---|
| Energy closeness | 2.0 | `2.0 * (1 - abs(song.energy - user.target_energy))` |
| Mood match | 1.5 | `+1.5` if `song.mood == favorite_mood`, else `0` |
| Genre match | 1.0 | `+1.0` if `song.genre == favorite_genre`, else `0` |
| Acoustic fit | 0.5 | `0.5 * song.acousticness` if `likes_acoustic`, else `0.5 * (1 - song.acousticness)` |

**Why not "+2.0 genre, +1.0 mood"?** I tried that common starting point against the 20-song catalog and it let genre override everything else. A chill, acoustic rock fan (energy 0.40) was recommended Crimson Highway and Storm Runner, both loud rock tracks, ahead of every quiet song. A happy-pop fan got Gym Hero (an intense workout track) above Rooftop Lights (a happy indie-pop song). With genre at 1.0 and energy and mood carrying more weight, the rankings follow how a song feels, and genre acts as a bonus.

**Why closeness, not "higher is better":** a user who wants `energy = 0.4` should not be pushed toward a 0.9 song just because 0.9 is bigger. Taking the absolute distance and subtracting it from 1 gives full credit for an exact match and less credit the further the song drifts in either direction.

**Why mood outweighs genre:** mood describes the listening experience across genres (a "chill" lofi and a "chill" ambient track fit the same moment), while genre is a coarse label. Even in the 20-song catalog most genres have only one to three songs, so an exact genre match is a rare yes/no switch and should not dominate.

### Ranking Rule

The scoring rule judges **one song at a time** and knows nothing about the others. The ranking rule works on the **whole list**: it scores every song, sorts by score from highest to lowest, and returns the top `k`. Both are needed because a score alone is just a number, and a sorted list alone has nothing to sort by. Keeping them separate also means I can change the weights without touching the sorting, or change how many results to return without touching the scoring.

### Dataset and example profiles

`data/songs.csv` has 20 songs across 10 genres and 12 moods, with energy from 0.22 to 0.96 and valence from 0.22 to 0.84. The songs were expanded to fill gaps in the original 10 (no mid-energy songs, no sad songs, no acoustic-and-upbeat songs). Profiles are dictionaries in `src/main.py`, for example:

```python
{"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True}   # chill lofi
{"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False} # intense rock
```

In a trial run of the recipe these two profiles shared no songs in their top 4, so the profile is specific enough to tell them apart.

### Expected biases and limitations

- **Energy can outvote genre.** Energy and acoustic fit together are worth up to 2.5 of 5.0 points, so a user who wants rock but at low energy may get no rock at all. In a trial, a "mellow rock" profile received only quiet lofi and ambient songs.
- **Genre can still pull in the wrong song.** A genre match is a flat +1.0 even when the song feels different, and mood matching is all-or-nothing. A pop fan can be shown Gym Hero (an intense pop track), while `angry` rock gets no mood credit for an `intense` rock fan.
- **Exact string matching treats near-genres as total misses.** `indie pop` earns nothing for a `pop` fan.
- **Mood vocabulary favors common moods.** `chill` appears 4 times and `happy` 3 times, while most moods appear once, so users who prefer rarer moods get fewer good candidates.
- **One favorite per category.** A profile holds one genre and one mood, so someone who likes both lofi and jazz can't be represented.
- **No diversity or discovery.** Songs are scored independently, so the top results may all sound alike, and there is no collaborative signal to surface surprising picks.
- **Tiny, hand-made catalog.** The songs are invented and the weights can only be judged by whether rankings look sensible, not validated statistically.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default `pop_happy` profile:

```
Loaded songs: 20

Profile: pop_happy {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'likes_acoustic': False}
Top recommendations:

1. Sunrise City by Neon Echo
   Score: 4.87 / 5.00
   - genre match (+1.0)
   - mood match (+1.5)
   - energy 0.82 vs target 0.80 (+1.96)
   - acoustic fit (+0.41)

2. Rooftop Lights by Indigo Parade
   Score: 3.75 / 5.00
   - mood match (+1.5)
   - energy 0.76 vs target 0.80 (+1.92)
   - acoustic fit (+0.33)

3. Gym Hero by Max Pulse
   Score: 3.22 / 5.00
   - genre match (+1.0)
   - energy 0.93 vs target 0.80 (+1.74)
   - acoustic fit (+0.47)

4. Heartbeat Replay by Neon Echo
   Score: 3.05 / 5.00
   - genre match (+1.0)
   - energy 0.65 vs target 0.80 (+1.70)
   - acoustic fit (+0.35)

5. Dandelion Fields by Paper Lanterns
   Score: 3.02 / 5.00
   - mood match (+1.5)
   - energy 0.52 vs target 0.80 (+1.44)
   - acoustic fit (+0.08)
```

Sunrise City wins because it matches on genre, mood and energy. Gym Hero (an intense workout song) still lands third on genre and energy alone, which is the genre-pull bias noted above.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



