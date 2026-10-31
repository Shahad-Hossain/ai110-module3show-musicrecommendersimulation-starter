"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

Run from the project root with: python -m src.main
Options:
  --profile NAME      run a single profile instead of all of them
  --experiment NAME   weight_shift (energy x2, genre x0.5) or no_mood (mood check off)
"""

import argparse

from src.recommender import DEFAULT_WEIGHTS, load_songs, recommend_songs


# Taste profiles: target values for the features used in scoring.
# "energy" is a 0.0-1.0 target (closer songs score higher), not a minimum.
PROFILES = {
    # Normal, well-behaved users
    "pop_happy": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
    "chill_lofi": {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
    "intense_rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
    # Adversarial / edge-case users
    "conflicted_sad_but_loud": {"genre": "folk", "mood": "melancholy", "energy": 0.9, "likes_acoustic": True},
    "mellow_rock": {"genre": "rock", "mood": "chill", "energy": 0.40, "likes_acoustic": True},
    "unknown_tastes": {"genre": "classical", "mood": "sad", "energy": 0.5, "likes_acoustic": False},
}
DEFAULT_PROFILE = "pop_happy"

# Experimental weight sets (default recipe totals 5.0 points)
EXPERIMENTS = {
    "weight_shift": {**DEFAULT_WEIGHTS, "energy": DEFAULT_WEIGHTS["energy"] * 2, "genre": DEFAULT_WEIGHTS["genre"] / 2},
    "no_mood": {**DEFAULT_WEIGHTS, "mood": 0.0},
}


def show(name: str, user_prefs: dict, songs: list, weights: dict | None = None) -> None:
    """Prints the top 5 recommendations and reasons for one profile."""
    max_score = sum((weights or DEFAULT_WEIGHTS).values())
    print(f"\nProfile: {name} {user_prefs}")
    print("Top recommendations:\n")
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=5, weights=weights), start=1):
        print(f"{rank}. {song['title']} by {song['artist']} [{song['genre']}/{song['mood']}]")
        print(f"   Score: {score:.2f} / {max_score:.2f}")
        for reason in explanation.split(", "):
            print(f"   - {reason}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--experiment", choices=EXPERIMENTS)
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    weights = EXPERIMENTS[args.experiment] if args.experiment else None
    if weights:
        print(f"Experiment: {args.experiment} weights = {weights}")

    names = [args.profile] if args.profile else list(PROFILES)
    for name in names:
        show(name, PROFILES[name], songs, weights)


if __name__ == "__main__":
    main()
