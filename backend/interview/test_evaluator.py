if __name__ == "__main__":
    from services.evaluator import evaluate_answer

    question = "What is polymorphism in Java?"

    answer = """
    Polymorphism allows one object to take many forms.
    Method overriding is an example of runtime polymorphism.
    """

    result = evaluate_answer(question, answer)

    print(result)
