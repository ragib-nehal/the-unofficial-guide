from __future__ import annotations

from rag.query import ask

TEST_QUERIES = [
    {
        "question": "What do students say about Moshe Lach for Data Structures?",
        "pass_criteria": "Answer is traceable to Moshe Lach RMP review chunks and sources include an RMP file.",
    },
    {
        "question": "What are the prerequisites for CISC 3130?",
        "pass_criteria": "Answer cites the CISC 3115 prerequisite and sources include BC CIS courses.",
    },
    {
        "question": "What is the recommended 4-year course schedule for a CS major?",
        "pass_criteria": "Answer references the semester sequence from the advising guide or CS major requirements.",
    },
    {
        "question": "What dining halls are best at Brooklyn College?",
        "pass_criteria": "Answer is exactly: I don't have enough information on that.",
    },
]


def main() -> None:
    for index, entry in enumerate(TEST_QUERIES, start=1):
        question = entry["question"]
        print("\n" + "=" * 80)
        print(f"QUESTION {index}: {question}")
        print(f"PASS CRITERIA: {entry['pass_criteria']}")
        print("=" * 80)

        result = ask(question)

        print("ANSWER:")
        print(result["answer"])
        print("\nSOURCES:")
        if result["sources"]:
            for source in result["sources"]:
                print(f"- {source}")
        else:
            print("- No sources returned")
        print("\nGROUNDING CHECK:")
        print("Could this answer have come from anywhere other than the retrieved chunks? If yes, tighten grounding.")


if __name__ == "__main__":
    main()
