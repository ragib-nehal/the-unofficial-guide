"""
Retrieval evaluation against three questions from planning.md.
Run from the project root:  python eval_retrieval.py
"""
from pipeline.retrieve import retrieve

QUERIES = [
    {
        "question": "What do students say about Moshe Lach for Data Structures?",
        "expected": "Strong positive reviews — good at explaining, engaging",
        "sources": "RMP source 1",
    },
    {
        "question": "What courses are required for the CS major that involve hardware or systems?",
        "expected": "CISC 3305 or 3310 (Architecture), CISC 3320 (Operating Systems)",
        "sources": "BC CS major requirements (source 20)",
    },
    {
        "question": "What is the recommended 4-year course schedule for a CS major?",
        "expected": (
            "Sem 1: CISC 1115 + MATH; Sem 2: CISC 2210, 3115 + MATH; "
            "Sem 3: CISC 2820W, 3130; Sem 4: CISC 3305/3310 + MATH; ..."
        ),
        "sources": "BC advising PDF (source 22)",
    },
]


def main() -> None:
    for entry in QUERIES:
        print("\n" + "=" * 80)
        print(f"QUESTION : {entry['question']}")
        print(f"EXPECTED : {entry['expected']}")
        print(f"SOURCES  : {entry['sources']}")
        print("=" * 80)

        results = retrieve(entry["question"], k=5)

        for result in results:
            print("-" * 80)
            print(f"chunk_id : {result['chunk_id']}")
            print(f"source   : {result.get('source_type')} | {result.get('source_file')}")
            dist = result["distance"]
            print(f"distance : {dist:.3f}" if dist is not None else "distance : —")
            print(f"match    : {result.get('match_type', 'semantic')}")
            if result.get("professor_name"):
                print(f"professor: {result['professor_name']}")
            if result.get("course_number"):
                print(f"course   : {result['course_number']}")
            print()
            print(result["text"][:500])

        print()


if __name__ == "__main__":
    main()
