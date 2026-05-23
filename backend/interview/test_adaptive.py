if __name__ == "__main__":
    from services.adaptive_logic import get_next_difficulty

    print(get_next_difficulty(90))
    print(get_next_difficulty(65))
    print(get_next_difficulty(30))
