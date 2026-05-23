if __name__ == "__main__":
    from agents.technical_agent import generate_technical_question
    from services.interview_flow import evaluate_interview_round

    # Step 1 - Generate Question
    question = generate_technical_question(
        role="Java Developer",
        difficulty="medium"
    )

    print("\nQUESTION:")
    print(question)

    # Step 2 - Candidate Answer
    answer = """
    Volatile is useful when multiple threads share a variable.
    It ensures visibility of latest updates between threads.
    Without volatile, threads may use cached values.
    """

    # Step 3 - Evaluate Interview Round
    result = evaluate_interview_round(
        question,
        answer
    )

    print("\nRESULT:")
    print(result)
