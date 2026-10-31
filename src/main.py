"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

Run from the project root with: python -m src.main
"""

from src.recommender import load_songs, recommend_songs


# Taste profiles: target values for the features used in scoring.
# "energy" is a 0.0-1.0 target (closer songs score higher), not a minimum.
PROFILES = {
    "pop_happy": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
    "chill_lofi": {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
    "intense_rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
    "sad_acoustic": {"genre": "folk", "mood": "melancholy", "energy": 0.30, "likes_acoustic": True},
}
DEFAULT_PROFILE = "pop_happy"


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = PROFILES[DEFAULT_PROFILE]
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\nProfile: {DEFAULT_PROFILE} {user_prefs}")
    print("Top recommendations:\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / 5.00")
        for reason in explanation.split(", "):
            print(f"   - {reason}")
        print()


if __name__ == "__main__":
    main()
