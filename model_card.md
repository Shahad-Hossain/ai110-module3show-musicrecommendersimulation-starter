# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

**Main weakness: matching labels can outvote what the listener actually asked to hear.** A user who wants sad music but very high energy (energy 0.9) was handed "Empty Porch Light", a quiet folk song with energy 0.30, as the number one pick. It collects 2.5 points just for matching the genre and mood labels, while being 0.6 away from the energy target only costs it 1.2 of its 2.0 energy points, so the labels win. The loud songs that really matched the energy request (Storm Runner, Crimson Highway) were pushed to 4th and 5th place. The system treats genre and mood as all-or-nothing stickers, so one sticker match can hide a large mismatch in how the song actually sounds.

Other weaknesses I found:

- **Vocabulary mismatches fail silently.** A profile asking for mood "sad" matched nothing, because the catalog calls that mood "melancholy". The profile was then ranked on energy and acousticness alone, with no warning to the user.
- **No partial credit for close moods or genres.** `angry` rock earns nothing for an "intense rock" fan, `indie pop` earns nothing for a pop fan, and `pop/intense` Gym Hero still gets recommended to happy-pop fans.
- **Chill is a bubble.** Four of the 20 songs are "chill" (lofi and ambient). Chill-lofi users get all-chill top 4 lists, and a rock fan who wanted quiet songs (mellow rock) got no rock song at all, because energy and acousticness outweigh the one genre point.
- **Mood vocabulary is lopsided.** `chill` appears 4 times and `happy` 3 times, while most of the other 12 moods appear once, so people with rarer tastes get fewer good candidates.
- **The catalog is tiny and invented.** 20 songs means the same few songs (Gym Hero, Sunrise City) turn up for many different profiles. Pop is only 3 of the 20 songs (15%), so this is not mainly a pop bias; it is a small-catalog and label-matching problem.

---

## 7. Evaluation  

**Profiles tested** (all outputs are pasted in the README under "Stress Test: Diverse Profiles"):

| Profile | Type | What it asks for |
|---|---|---|
| Happy Pop | normal | pop, happy, energy 0.8 |
| Chill Lofi | normal | lofi, chill, energy 0.38, likes acoustic |
| Deep Intense Rock | normal | rock, intense, energy 0.92 |
| Conflicted | adversarial | folk, melancholy, energy **0.9**, likes acoustic (sad but loud) |
| Mellow Rock | adversarial | rock fan who wants chill songs at energy 0.40 |
| Unknown tastes | adversarial | genre "classical", mood "sad" (neither is in the catalog) |

**What I looked for:** whether the top song felt right, whether different profiles got different lists, and whether the "because" reasons explained the order.

**What matched intuition:** the three normal profiles each put the song I would pick on top (Sunrise City, Library Rain, Storm Runner), and their lists do not overlap much.

**What surprised me:**
- **Why does Gym Hero keep showing up for people who just want happy pop?** In plain terms: the system adds up points. Gym Hero is a pop song (+1.0) and its energy (0.93) is close to what a pop fan wants (about +1.7), so it already has nearly 3 points before mood is even checked. It is an "intense" workout song, not a "happy" one, so it misses the 1.5 mood points. But the catalog only has three pop songs, so the system runs out of better candidates quickly and Gym Hero slides into 3rd place. It also shows up second for the rock fan, because it matches "intense" and has almost the same energy as the rock song. It is simply a song that is close to a lot of people's numbers, even though it does not fit their mood.
- **The conflicted user got a quiet song first** (see Limitations).
- **The "unknown tastes" profile still got confident-looking results**, even though two of its four preferences matched nothing.

**Why Sunrise City ranks first for Happy Pop:** genre match +1.0, mood match +1.5, energy 0.82 vs 0.80 gives +1.96, and acoustic fit +0.41, for 4.87 out of 5. The runner-up, Rooftop Lights, loses the 1.0 genre point (it is "indie pop") and ends with 3.75.

**Comparing pairs of profiles** (why the lists differ, and whether that makes sense):

| Pair | What changed | Does it make sense? |
|---|---|---|
| Happy Pop vs Chill Lofi | Pop/happy songs near energy 0.8 (Sunrise City) are replaced by lofi and ambient songs near energy 0.35 (Library Rain). | Yes. These are opposite moods and opposite energy levels, and the lists share no songs. |
| Happy Pop vs Deep Intense Rock | Both want high energy, so Gym Hero appears in both. Pop songs are replaced by Storm Runner and Crimson Highway. | Yes. The overlap is the high-energy part; the genre and mood decide the rest. |
| Chill Lofi vs Deep Intense Rock | No song in common. Quiet, acoustic songs versus loud, non-acoustic ones. | Yes. This is the clearest test of the profile: every preference points the opposite way. |
| Deep Intense Rock vs Mellow Rock | Same genre, but the rock songs disappear entirely when the user wants energy 0.40 and chill. | Partly. It shows energy and mood matter more than genre, which is defensible, but a rock fan getting zero rock is surprising. |
| Chill Lofi vs Mellow Rock | Nearly identical lists. | Expected, since both want low-energy, chill, acoustic songs. It shows the "rock" label barely counted. |
| Deep Intense Rock vs Conflicted | Both want energy about 0.9, but Conflicted starts with quiet folk and only reaches the loud rock songs at 4th and 5th. | Not fully. It shows the label-over-energy problem. |
| Chill Lofi vs Unknown tastes | Chill Lofi gets confident matches; Unknown gets mid-energy songs across five genres with low scores (about 2.0 of 5). | Yes. The low scores correctly signal weak matches, but nothing tells the user that their genre was not found. |

The remaining pairs follow the same pattern: the more preferences two profiles share, the more songs their lists share.

**Experiments** (details in the README):
- **Weight shift (energy x2, genre x0.5):** rankings barely moved for normal users and changed mainly for the conflicted user. Different, not clearly more accurate.
- **Mood check removed:** happy-pop users got an angry rock song and the intense-pop Gym Hero moved up. Mood clearly matters, so I kept it.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
