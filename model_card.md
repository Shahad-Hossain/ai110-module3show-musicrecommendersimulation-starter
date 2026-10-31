# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Goal / Task

VibeMatch suggests songs from a small catalog that fit one user's taste.

It tries to predict which songs a user would like best. It compares each song to the user's favorite genre, favorite mood, target energy, and whether they like acoustic music. Then it shows the top 5 songs with reasons.

---

## 3. Data Used

- The catalog is `data/songs.csv`. It has **20 songs**.
- Each song has 10 columns: id, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.
- There are **10 genres** (pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, edm, hip hop) and **12 moods**.
- I started with 10 songs and added 10 more. I added them to fill gaps: no sad songs, no mid-energy songs, and no songs that were both acoustic and upbeat.
- The songs and artists are **made up**. They are not real data.
- Limits: the catalog is tiny. `chill` shows up 4 times, but most moods show up once. There are no lyrics, no language, and no song popularity.

---

## 4. Algorithm Summary

Each song gets points out of 5. The song with the most points wins.

- **Energy (up to 2.0 points):** the closer the song's energy is to the user's target, the more points. A song that is too loud or too quiet both lose points.
- **Mood (1.5 points):** the song gets the points if its mood matches the user's favorite mood. Otherwise, zero.
- **Genre (1.0 point):** the song gets the point if its genre matches. Otherwise, zero.
- **Acoustic fit (up to 0.5 points):** if the user likes acoustic songs, more acoustic songs get more points. If not, less acoustic songs get more points.

After every song has a score, the system sorts them from highest to lowest and returns the top 5. It also lists the reasons, like "mood match (+1.5)".

Tempo, danceability, and valence are in the data, but I do not score them. They mostly repeat what energy already says.

---

## 5. Observed Behavior / Biases

**Main problem: matching labels can beat what the user actually wants.**

One test user wanted sad music at very high energy (0.9). The system gave a quiet folk song (energy 0.30) as the top pick. That song matched the genre and mood labels, so it got 2.5 points. Being far from the energy target only cost it 1.2 points. The loud songs that matched the energy were pushed down to 4th and 5th.

Other things I found:

- **Gym Hero shows up a lot.** It is an intense pop workout song. It lands in the top 5 for happy-pop fans and for rock fans. It is close to many people's numbers, even when the mood is wrong.
- **Wrong words fail silently.** A user who asked for mood "sad" matched nothing, because the catalog says "melancholy". The system did not warn them.
- **No partial credit.** "Angry" rock gets nothing for an "intense rock" fan. "Indie pop" gets nothing for a pop fan.
- **Chill is a bubble.** A rock fan who wanted quiet, chill songs got zero rock songs.
- **Small catalog.** The same few songs show up for many users. Pop is only 15% of the songs, so this is not a pop bias. It is a small-catalog and label-matching problem.

---

## 6. Evaluation Process

I tested six user profiles. The full outputs are in the README.

| Profile | Type |
|---|---|
| Happy Pop (pop, happy, energy 0.8) | normal |
| Chill Lofi (lofi, chill, energy 0.38, likes acoustic) | normal |
| Deep Intense Rock (rock, intense, energy 0.92) | normal |
| Conflicted (folk, melancholy, energy 0.9) | tricky |
| Mellow Rock (rock fan who wants chill, energy 0.4) | tricky |
| Unknown tastes (genre "classical", mood "sad") | tricky |

**What I checked:** Did the top song feel right? Did different users get different lists? Did the reasons explain the order?

**What matched my intuition:** the three normal users each got the song I would have picked first: Sunrise City, Library Rain, and Storm Runner.

**What surprised me:** the tricky users. The "sad but loud" user got a quiet song first. The "unknown tastes" user still got confident-looking results, even though two of their four preferences matched nothing.

**Why Gym Hero keeps showing up for people who just want happy pop:** the system adds up points. Gym Hero is a pop song (+1.0), and its energy is close to what a pop fan wants (about +1.7). That is nearly 3 points before mood is even checked. It is an "intense" song, not a "happy" one, so it misses the 1.5 mood points. But the catalog only has three pop songs, so there are not many better options, and it lands 3rd.

**Why Sunrise City wins for Happy Pop:** it matches the genre (+1.0) and the mood (+1.5). Its energy is very close (+1.96). Its acoustic fit adds +0.41. That is 4.87 out of 5.

**More explanations of why songs were recommended** (taken from the score breakdowns in the README):

- **Rooftop Lights (3.75) for Happy Pop:** it is happy (+1.5) and its energy is close to the target (+1.92). It gets no genre points because it is "indie pop", not "pop".
- **Storm Runner (4.93) for Deep Intense Rock:** rock (+1.0), intense (+1.5), energy 0.91 against a 0.92 target (+1.98), and not acoustic (+0.45). It matches almost perfectly.
- **Library Rain (4.87) for Chill Lofi:** lofi (+1.0), chill (+1.5), energy 0.35 against 0.38 (+1.94), and very acoustic, which this user likes (+0.43).

**Comparing pairs of profiles:**

| Pair | What changed | Does it make sense? |
|---|---|---|
| Happy Pop vs Chill Lofi | Loud pop songs are replaced by quiet lofi and ambient songs. No songs in common. | Yes. Opposite mood and opposite energy. |
| Happy Pop vs Deep Intense Rock | Both want high energy, so Gym Hero shows up in both. The rest changes with genre and mood. | Yes. The overlap is the high-energy part. |
| Chill Lofi vs Deep Intense Rock | No songs in common. Quiet and acoustic versus loud and electric. | Yes. Every preference points the other way. |
| Deep Intense Rock vs Mellow Rock | Same genre, but the rock songs disappear when the user wants quiet, chill songs. | Partly. Energy and mood beat genre, but a rock fan getting zero rock is surprising. |
| Chill Lofi vs Mellow Rock | Almost the same list. | Yes, both want quiet, chill, acoustic songs. The "rock" label barely counted. |
| Deep Intense Rock vs Conflicted | Both want energy about 0.9, but Conflicted gets quiet folk first and loud rock only at 4th and 5th. | Not really. It shows labels beating energy. |
| Chill Lofi vs Unknown tastes | Chill Lofi gets strong matches. Unknown gets mid-energy songs with low scores (about 2 out of 5). | Yes. Low scores signal weak matches, but the user is never told their genre was not found. |

The other pairs follow the same pattern: the more preferences two users share, the more songs their lists share.

**Experiments:**

- **Double energy, halve genre:** normal users barely changed. Only the "sad but loud" user got a different top song. It was different, but not clearly better.
- **Remove the mood check:** happy-pop users got an angry rock song, and Gym Hero moved up. Mood matters, so I kept it.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**

- A classroom project to learn how recommenders turn data into a ranked list.
- Trying out scoring rules on a small catalog and seeing why a song ranks where it does.

**Not intended for:**

- A real music app or real users. The catalog is too small and made up.
- Judging anyone's taste. One genre, one mood, and one energy number cannot describe a person.
- Anything where a wrong answer matters. It has no fairness checks and cannot learn from feedback.

---

## 8. Ideas for Improvement

1. **Give partial credit.** Treat close moods and genres as partly matching, like "angry" and "intense", or "indie pop" and "pop". Warn the user when their genre or mood is not in the catalog.
2. **Let users pick more than one taste.** Allow a list of favorite genres and moods. Add valence so "sad" and "happy" can be told apart by number.
3. **Add variety and more songs.** Avoid a top 5 that all sound alike. Grow the catalog so one song like Gym Hero cannot show up everywhere.

---

## 9. Personal Reflection

**Biggest learning moment.** I thought the hard part would be the math. It was actually the weights. I tried the common starting point of giving genre 2.0 and mood 1.0. A rock fan who wanted chill songs got loud rock songs first. That showed me one number can quietly decide who gets what.

**How AI helped, and when I double-checked it.** AI was great for getting started fast. It helped me find gaps in my songs, draft the scoring rule, and write the code. But I did not just trust it. I ran the recommender on test profiles and read the results myself. I also found a bug where `python -m src.main` did not work because of an import. I would not have caught that without running it.

**What surprised me.** A few simple rules felt like a real recommendation. Seeing "mood match (+1.5)" next to a song made it feel smart, even though it is only adding points. It also showed me how a system can look confident when it is wrong, like when it gave results for a mood that was not in the catalog.

**What I would try next.** I would add partial credit for similar moods and genres, let users pick more than one favorite, and add many more songs. I would also try the "people like you" idea from apps like Spotify, so the system is not only comparing song labels.
