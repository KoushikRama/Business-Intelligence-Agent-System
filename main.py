from graph.bi_graph import run_graph


def main():

    test_questions = [

    # 1. Direct
    "Hello, how are you today?",

    # 2. SQL Only
    "How many premium customers do we have?",

    # 3. RAG Only
    "What is the employee PTO policy?",

    # 4. SQL + RAG
    "How many payment failures occurred and what should customer support do according to the Payment Failure Handling SOP?"

    ]

    for i, question in enumerate(test_questions, start=1):

        print("\n" + "=" * 80)
        print(f"QUESTION {i}: {question}")
        print("-" * 80)

        response = run_graph(question)

        print("RESPONSE:", response)


if __name__ == "__main__":
    main()