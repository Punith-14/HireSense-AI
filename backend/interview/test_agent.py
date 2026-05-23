if __name__ == "__main__":
    from agents.technical_agent import generate_technical_question

    question = generate_technical_question(
        role="Java Developer",
        difficulty="medium"
    )

    print(question)
