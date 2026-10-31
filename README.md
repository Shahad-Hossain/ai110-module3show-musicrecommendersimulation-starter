# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

**VibeMatch 1.0** is a small command-line recommender. It loads 20 made-up songs from `data/songs.csv`, compares each song to a user's taste profile (favorite genre, favorite mood, target energy, and whether they like acoustic music), and gives every song a score out of 5. It then ranks the songs and prints the top 5, with a reason for every point awarded. I tested it on six profiles, ran two experiments that change the weights, and wrote down where it works and where it fails in the [Model Card](model_card.md).

---

## How The System Works

### How real-world recommenders work

Every recommender has three parts, and it helps to keep them separate:

1. **Input data.** What the system knows. For songs, that is features like genre, mood, tempo, energy and acousticness. For users, it is their history: plays, skips, saves, likes and playlist adds, plus context like time of day.
2. **User preferences.** What the system believes this person wants. Real platforms learn it from history (for example, "this user skips slow songs and replays upbeat pop"). In my version, I write it down by hand as a taste profile.
3. **Ranking and selection.** The system scores every candidate song against the preferences, sorts by score, and shows only the top few. Platforms like Spotify and YouTube do this in two steps: first they narrow millions of items to a few hundred candidates, then a heavier model ranks those.

Platforms blend two main ideas. **Collaborative filtering** uses other users' behavior and recommends what similar listeners enjoyed, so it needs no knowledge of the song itself. **Content-based filtering** uses song attributes and recommends songs that resemble what you already like. Collaborative filtering finds surprising picks but struggles with brand-new songs (the "cold start" problem); content-based handles new songs well but can trap you in a bubble of near-duplicates. Modern systems also learn from implicit feedback (a skip in the first 30 seconds is a strong "no") and try to optimize for satisfaction, such as watch time, instead of just clicks.

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

### Why these songs were recommended

Each explanation below comes straight from the score breakdown above.

- **Sunrise City (4.87 / 5), Happy Pop:** it is a pop song (+1.0 genre), its mood is happy (+1.5 mood), its energy of 0.82 is almost exactly the 0.80 target (+1.96 energy), and it is not very acoustic (+0.41). It matches on everything, so it wins.
- **Rooftop Lights (3.75 / 5), Happy Pop:** it is happy (+1.5) and has energy 0.76, close to the target (+1.92). It gets no genre points because it is "indie pop", not "pop". That one missing point is why it is second.
- **Gym Hero (3.22 / 5), Happy Pop:** it is a pop song (+1.0) with energy 0.93 (+1.74), but its mood is "intense", not "happy", so it earns no mood points. It ranks third only because there are few better options.
- **Storm Runner (4.93 / 5), Deep Intense Rock:** rock genre (+1.0), intense mood (+1.5), energy 0.91 against a 0.92 target (+1.98), and low acousticness (+0.45). It is a near-perfect match.
- **Library Rain (4.87 / 5), Chill Lofi:** lofi genre (+1.0), chill mood (+1.5), energy 0.35 against 0.38 (+1.94), and it is very acoustic, which this user likes (+0.43).

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Stress Test: Diverse Profiles

Output of `python -m src.main` (all six profiles; run one with `--profile NAME`). The first three are everyday users, the last three are adversarial profiles designed to trick the scoring.

### Happy Pop (normal)

```
Profile: pop_happy {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'likes_acoustic': False}
Top recommendations:

1. Sunrise City by Neon Echo [pop/happy]
   Score: 4.87 / 5.00
   - genre match (+1.0)
   - mood match (+1.5)
   - energy 0.82 vs target 0.80 (+1.96)
   - acoustic fit (+0.41)

2. Rooftop Lights by Indigo Parade [indie pop/happy]
   Score: 3.75 / 5.00
   - mood match (+1.5)
   - energy 0.76 vs target 0.80 (+1.92)
   - acoustic fit (+0.33)

3. Gym Hero by Max Pulse [pop/intense]
   Score: 3.22 / 5.00
   - genre match (+1.0)
   - energy 0.93 vs target 0.80 (+1.74)
   - acoustic fit (+0.47)

4. Heartbeat Replay by Neon Echo [pop/romantic]
   Score: 3.05 / 5.00
   - genre match (+1.0)
   - energy 0.65 vs target 0.80 (+1.70)
   - acoustic fit (+0.35)

5. Dandelion Fields by Paper Lanterns [folk/happy]
   Score: 3.02 / 5.00
   - mood match (+1.5)
   - energy 0.52 vs target 0.80 (+1.44)
   - acoustic fit (+0.08)
```

### Chill Lofi (normal)

```
Profile: chill_lofi {'genre': 'lofi', 'mood': 'chill', 'energy': 0.38, 'likes_acoustic': True}
Top recommendations:

1. Library Rain by Paper Lanterns [lofi/chill]
   Score: 4.87 / 5.00
   - genre match (+1.0)
   - mood match (+1.5)
   - energy 0.35 vs target 0.38 (+1.94)
   - acoustic fit (+0.43)

2. Midnight Coding by LoRoom [lofi/chill]
   Score: 4.78 / 5.00
   - genre match (+1.0)
   - mood match (+1.5)
   - energy 0.42 vs target 0.38 (+1.92)
   - acoustic fit (+0.35)

3. Spacewalk Thoughts by Orbit Bloom [ambient/chill]
   Score: 3.76 / 5.00
   - mood match (+1.5)
   - energy 0.28 vs target 0.38 (+1.80)
   - acoustic fit (+0.46)

4. Drift Cloud by Orbit Bloom [ambient/chill]
   Score: 3.65 / 5.00
   - mood match (+1.5)
   - energy 0.22 vs target 0.38 (+1.68)
   - acoustic fit (+0.47)

5. Focus Flow by LoRoom [lofi/focused]
   Score: 3.35 / 5.00
   - genre match (+1.0)
   - energy 0.40 vs target 0.38 (+1.96)
   - acoustic fit (+0.39)
```

### Deep Intense Rock (normal)

```
Profile: intense_rock {'genre': 'rock', 'mood': 'intense', 'energy': 0.92, 'likes_acoustic': False}
Top recommendations:

1. Storm Runner by Voltline [rock/intense]
   Score: 4.93 / 5.00
   - genre match (+1.0)
   - mood match (+1.5)
   - energy 0.91 vs target 0.92 (+1.98)
   - acoustic fit (+0.45)

2. Gym Hero by Max Pulse [pop/intense]
   Score: 3.96 / 5.00
   - mood match (+1.5)
   - energy 0.93 vs target 0.92 (+1.98)
   - acoustic fit (+0.47)

3. Crimson Highway by Iron Meadow [rock/angry]
   Score: 3.38 / 5.00
   - genre match (+1.0)
   - energy 0.88 vs target 0.92 (+1.92)
   - acoustic fit (+0.46)

4. Pulse Machine by Max Pulse [edm/energetic]
   Score: 2.41 / 5.00
   - energy 0.96 vs target 0.92 (+1.92)
   - acoustic fit (+0.48)

5. Sunrise City by Neon Echo [pop/happy]
   Score: 2.21 / 5.00
   - energy 0.82 vs target 0.92 (+1.80)
   - acoustic fit (+0.41)
```

### Conflicted: sad mood but very high energy (adversarial)

```
Profile: conflicted_sad_but_loud {'genre': 'folk', 'mood': 'melancholy', 'energy': 0.9, 'likes_acoustic': True}
Top recommendations:

1. Empty Porch Light by Hollow Pines [folk/melancholy]
   Score: 3.75 / 5.00
   - genre match (+1.0)
   - mood match (+1.5)
   - energy 0.30 vs target 0.90 (+0.80)
   - acoustic fit (+0.45)

2. Broken Signal by Static Lilies [indie pop/melancholy]
   Score: 3.00 / 5.00
   - mood match (+1.5)
   - energy 0.55 vs target 0.90 (+1.30)
   - acoustic fit (+0.20)

3. Dandelion Fields by Paper Lanterns [folk/happy]
   Score: 2.67 / 5.00
   - genre match (+1.0)
   - energy 0.52 vs target 0.90 (+1.24)
   - acoustic fit (+0.42)

4. Storm Runner by Voltline [rock/intense]
   Score: 2.03 / 5.00
   - energy 0.91 vs target 0.90 (+1.98)
   - acoustic fit (+0.05)

5. Crimson Highway by Iron Meadow [rock/angry]
   Score: 2.00 / 5.00
   - energy 0.88 vs target 0.90 (+1.96)
   - acoustic fit (+0.04)
```

### Mellow Rock: rock fan who wants quiet, chill songs (adversarial)

```
Profile: mellow_rock {'genre': 'rock', 'mood': 'chill', 'energy': 0.4, 'likes_acoustic': True}
Top recommendations:

1. Library Rain by Paper Lanterns [lofi/chill]
   Score: 3.83 / 5.00
   - mood match (+1.5)
   - energy 0.35 vs target 0.40 (+1.90)
   - acoustic fit (+0.43)

2. Midnight Coding by LoRoom [lofi/chill]
   Score: 3.81 / 5.00
   - mood match (+1.5)
   - energy 0.42 vs target 0.40 (+1.96)
   - acoustic fit (+0.35)

3. Spacewalk Thoughts by Orbit Bloom [ambient/chill]
   Score: 3.72 / 5.00
   - mood match (+1.5)
   - energy 0.28 vs target 0.40 (+1.76)
   - acoustic fit (+0.46)

4. Drift Cloud by Orbit Bloom [ambient/chill]
   Score: 3.61 / 5.00
   - mood match (+1.5)
   - energy 0.22 vs target 0.40 (+1.64)
   - acoustic fit (+0.47)

5. Focus Flow by LoRoom [lofi/focused]
   Score: 2.39 / 5.00
   - energy 0.40 vs target 0.40 (+2.00)
   - acoustic fit (+0.39)
```

### Unknown tastes: genre and mood not in the catalog (adversarial)

```
Profile: unknown_tastes {'genre': 'classical', 'mood': 'sad', 'energy': 0.5, 'likes_acoustic': False}
Top recommendations:

1. Broken Signal by Static Lilies [indie pop/melancholy]
   Score: 2.20 / 5.00
   - energy 0.55 vs target 0.50 (+1.90)
   - acoustic fit (+0.30)

2. Velvet Evenings by Slow Stereo [jazz/romantic]
   Score: 2.05 / 5.00
   - energy 0.48 vs target 0.50 (+1.96)
   - acoustic fit (+0.09)

3. Heartbeat Replay by Neon Echo [pop/romantic]
   Score: 2.05 / 5.00
   - energy 0.65 vs target 0.50 (+1.70)
   - acoustic fit (+0.35)

4. Dandelion Fields by Paper Lanterns [folk/happy]
   Score: 2.04 / 5.00
   - energy 0.52 vs target 0.50 (+1.96)
   - acoustic fit (+0.08)

5. Golden Hour Drive by Neon Echo [synthwave/nostalgic]
   Score: 2.01 / 5.00
   - energy 0.68 vs target 0.50 (+1.64)
   - acoustic fit (+0.38)
```

### What the outputs show

- **Happy Pop vs Chill Lofi:** the pop profile gets loud, upbeat songs (energy around 0.8), and the lofi profile shifts to quiet, acoustic ones (energy around 0.35). The two lists share no songs, which is what opposite tastes should produce.
- **Happy Pop vs Deep Intense Rock:** both want high energy, so Gym Hero appears in both lists. Genre and mood then pull the lists apart: Sunrise City for pop, Storm Runner and Crimson Highway for rock.
- **Chill Lofi vs Deep Intense Rock:** no songs in common. Every preference points the other way: quiet vs loud, acoustic vs electric.
- **Deep Intense Rock vs Mellow Rock:** same favorite genre, but the mellow rock fan gets no rock songs at all. Energy, mood and acoustic fit together outweigh the single genre point.
- **Conflicted (sad but loud):** the quiet folk song wins because it matches the labels, and the loud songs that fit the energy request only show up at 4th and 5th.
- **Unknown tastes:** none of the genre or mood labels match anything, so the system falls back on energy and acousticness. The scores are low (about 2 out of 5), which correctly signals a weak match, but the system never tells the user.

---

## Experiments You Tried

Both experiments are built into the CLI: `python -m src.main --experiment weight_shift` and `python -m src.main --experiment no_mood`. The maximum score changes with the weights (6.5 and 3.5 instead of 5.0), but every score still stays between 0 and that maximum, so the math remains valid.

### Experiment 1: weight shift (energy x2, genre x0.5)

Weights became energy 4.0, mood 1.5, genre 0.5, acoustic 0.5.

| Profile | Baseline top 5 | After weight shift |
|---|---|---|
| Happy Pop | Sunrise City, Rooftop Lights, Gym Hero, Heartbeat Replay, Dandelion Fields | Sunrise City, Rooftop Lights, Gym Hero, **Dandelion Fields, Heartbeat Replay** (4th and 5th swap) |
| Chill Lofi | Library Rain, Midnight Coding, Spacewalk Thoughts, Drift Cloud, Focus Flow | Same five, same order |
| Deep Intense Rock | Storm Runner, Gym Hero, Crimson Highway, Pulse Machine, Sunrise City | Same five, same order |
| Conflicted (sad but loud) | Empty Porch Light, Broken Signal, Dandelion Fields, Storm Runner, Crimson Highway | **Broken Signal** first, Empty Porch Light second, then Storm Runner, Crimson Highway, Gym Hero (loud rock songs pushed up) |
| Mellow Rock | Library Rain, Midnight Coding, ... | Midnight Coding and Library Rain swap; no rock song either way |

Result: **different, not clearly more accurate.** Rankings barely moved for users whose genre, mood and energy all agree. They changed mostly for the conflicted user, where the quiet folk song lost its first place because its energy (0.30) is far from 0.90. That feels slightly more faithful to the "loud" half of the request but gives up the "sad folk" half, so neither ordering is clearly right.

### Experiment 2: remove the mood check

Mood weight set to 0.

| Profile | What changed |
|---|---|
| Happy Pop | **Gym Hero jumps from 3rd to 2nd**; Rooftop Lights (indie pop, happy) falls out of the top 5 and Crimson Highway, an angry rock song, appears. |
| Chill Lofi | Ambient songs drop out; Focus Flow and Coffee Shop Stories (jazz, relaxed) move up. |
| Deep Intense Rock | Crimson Highway (angry rock) rises from 3rd to 2nd above Gym Hero, which is arguably better for a rock fan. |
| Conflicted | A happy folk song (Dandelion Fields) takes first place for a user who asked for sad. |

Result: mood is doing real work. Without it, the system keeps the genre and energy matches but loses the "feel" of the request, so a user who wanted happy music gets an angry rock song. Keep it. The one case where removing mood looked better (intense rock) points to a different problem: `angry` and `intense` should earn partial credit instead of being treated as total opposites.

---

## Limitations and Risks

- **Labels can beat what the user actually wants.** A user who wanted sad music at very high energy got a quiet folk song first, because matching genre and mood is worth 2.5 points and the energy gap only cost 1.2.
- **Tiny, made-up catalog.** With 20 songs, the same few (like Gym Hero) show up for many users.
- **No partial credit and silent failures.** "Angry" rock earns nothing for an "intense rock" fan, and a mood that is not in the catalog (like "sad") is ignored without a warning.
- **One favorite per category.** A user can have one genre and one mood, and the system cannot learn from behavior.
- **It does not understand lyrics, language, or popularity.**

More detail is in the [Model Card](model_card.md).

---

## Reflection

Full model card: [**Model Card**](model_card.md)

**What I learned about how recommenders turn data into predictions.** A recommender is just three steps: describe the songs with numbers and labels, describe the user the same way, and score how close the two are. My scoring rule is only a few additions, but seeing "mood match (+1.5)" next to a song made it feel like a real recommendation. The weights ended up mattering more than the math. When I tried the common "genre 2.0, mood 1.0" starting point, a rock fan who wanted quiet songs got loud rock first. Changing one number changed who got what.

**Where bias or unfairness could show up.** The system treats genre and mood as all-or-nothing labels, so it favors users whose tastes match the catalog's labels and quietly fails for everyone else. A user who asked for "sad" got results anyway, even though nothing in the catalog is called "sad". In a real app, the same problem could appear as popular songs getting more exposure because they have more data, or niche listeners getting worse suggestions because fewer songs fit them.



