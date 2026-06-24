from graph.bi_graph import run_graph
from memory.conversation_store import create_conversation

def main():

    test_questions = [
        # #1. Direct greeting
        # "Hello, how are you today?",

        # # 2. SQL only
        # "How many premium customers do we have?",

        # # 3. RAG only
        # "What is the employee PTO policy?",

        # 4. SQL + RAG
        "How many payment failures occurred and what should customer support do according to the Payment Failure Handling SOP?",

        # 5. Recent memory - previous question
        "What was my previous question?",

        # 6. Recent memory - summarize recent chat
        "Summarize what we just discussed.",

        # 7. Recent memory + SQL follow-up
        "What about their orders?",

        # 8. Recent memory + RAG follow-up
        "What does that policy say about approval?"
    ]

    test_questions_set2 = [
        "What did we discuss about premium customers?",
        "What did you tell me about payment failures?",
        "Do you remember what we said about PTO?",
        "What about their orders?",
        "What does that policy say about approval?"
    ]

    test_questions_set3 = [
        "When i asked about orders, it was about the premium customers"
    ]

    # conversation_id = create_conversation()
    conversation_id = "cf034eb2-bca9-4058-bdf8-7bebb6d3a5ec"
    for i, question in enumerate(test_questions_set3, start=1):

        print("\n" + "=" * 80)
        print(f"QUESTION {i}: {question}")
        print("-" * 80)

        response = run_graph(question, conversation_id)

        print("RESPONSE:", response)


if __name__ == "__main__":
    main()