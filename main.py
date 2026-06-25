from graph.bi_graph import run_graph
from memory.conversation_store import create_conversation

def main():

    test_questions = [
        # Simple workflow expected
        "How many customers do we have?",
        "What is the refund policy?",
        "How many completed orders are there?",
        "What is the IT security and password policy?",

        # SQL + RAG simple workflow expected
        "How many failed payments are there and what should support do according to the SOP?",

        # # ReAct expected
        # "That result does not look right, check again.",
        # "Why are those numbers inconsistent?",
        # "Can you verify that from the database?",

        # # Complex/ReAct expected
        # "Investigate why completed orders may be lower than expected.",
        # "Analyze payment failures and recommend actions."
    ]

    test_questions_set2 = [
        "What did we discuss about premium customers?",
        "What did you tell me about payment failures?",
        "Do you remember what we said about PTO?",
        "What about their orders?",
        "What does that policy say about approval?"
    ]

    test_questions_set3 = [
        "How many premium customers do we have?",
        "What is the PTO policy?",
        "How many payment failures occurred and what should support do?",
        "What about their orders?",
        # "Why did revenue drop this month?",
        # "That was wrong, try again."
    ]
    next_question = ["Just give me only the number of failed payment, no extra text"]
    # conversation_id = create_conversation()
    # print("conv_id:",conversation_id)
    conversation_id = "c0a95ccc-e09b-410c-aa89-3822de43eb7d"
    for i, question in enumerate(next_question, start=1):

        print("\n" + "=" * 80)
        print(f"QUESTION {i}: {question}")
        print("-" * 80)

        response = run_graph(question, conversation_id)

        print("RESPONSE:", response)


if __name__ == "__main__":
    main()