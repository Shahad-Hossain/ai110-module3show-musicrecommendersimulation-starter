import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# Algorithm Recipe (max 5.0 points); see "How The System Works" in README.md
ENERGY_POINTS = 2.0
MOOD_POINTS = 1.5
GENRE_POINTS = 1.0
ACOUSTIC_POINTS = 0.5

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for this user, best match first."""
        ranked = sorted(self.songs, key=lambda s: score_song(_to_prefs(user), asdict(s))[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a comma-separated list of the reasons this song scored as it did."""
        _, reasons = score_song(_to_prefs(user), asdict(song))
        return ", ".join(reasons)

def _to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the prefs dict that score_song expects."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file as dicts, converting numeric columns to int/float."""
    int_fields = ("id",)
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against user prefs; returns (score out of 5.0, list of reasons)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_POINTS
        reasons.append(f"genre match (+{GENRE_POINTS:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_POINTS
        reasons.append(f"mood match (+{MOOD_POINTS:.1f})")

    if "energy" in user_prefs:
        points = ENERGY_POINTS * (1 - abs(song["energy"] - user_prefs["energy"]))
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{points:.2f})"
        )

    if "likes_acoustic" in user_prefs:
        fit = song["acousticness"] if user_prefs["likes_acoustic"] else 1 - song["acousticness"]
        points = ACOUSTIC_POINTS * fit
        score += points
        reasons.append(f"acoustic fit (+{points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song and returns the top k as (song, score, explanation), best first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
