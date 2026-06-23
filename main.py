from graph.bi_graph import run_graph


def main():

    test_questions = [
        "Hello",
        "How many customers do we have?",
        "How many payment failures occurred?",
        "Show all failed payments",
        "Show all employee salaries",
        "Insert a new customer",
        "Who won the NBA championship?"
    ]

    for i, question in enumerate(test_questions, start=1):

        print("\n" + "=" * 80)
        print(f"QUESTION {i}: {question}")
        print("-" * 80)

        response = run_graph(question)

        print("RESPONSE:", response)


if __name__ == "__main__":
    main()