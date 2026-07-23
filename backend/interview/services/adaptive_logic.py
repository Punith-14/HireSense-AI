def get_next_difficulty(score):

    if score >= 80:
        return "hard"

    elif score >= 50:
        return "medium"

    else:
        return "easy"