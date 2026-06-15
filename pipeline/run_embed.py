from __future__ import annotations

import argparse

from .embed import embed_all
from .retrieve import retrieve

TEST_QUERIES = [
    "What do students say about Moshe Lach for Data Structures?",
    "What are the prerequisites for CISC 3130?",
    "What do students say about Gabriel Yarmish for CISC 1115?",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed chunks into ChromaDB and test retrieval.")
    parser.add_argument("--rebuild", action="store_true", help="Drop and re-embed the collection.")
    parser.add_argument("--test", action="store_true", help="Run 3 evaluation queries after embedding.")
    parser.add_argument("--k", type=int, default=5, help="Number of chunks to retrieve per query.")
    args = parser.parse_args()

    collection = embed_all(rebuild=args.rebuild)

    if args.test:
        run_test_queries(collection, k=args.k)


def run_test_queries(collection, k: int) -> None:
    for query in TEST_QUERIES:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)
        results = retrieve(query, k=k, collection=collection)
        for result in results:
            print("-" * 80)
            print(f"chunk_id : {result['chunk_id']}")
            print(f"source   : {result.get('source_type')} | {result.get('source_file')}")
            print(f"distance : {result['distance']:.3f}")
            if result.get("professor_name"):
                print(f"professor: {result['professor_name']}")
            if result.get("course_number"):
                print(f"course   : {result['course_number']}")
            print()
            print(result["text"][:400])
        print()


if __name__ == "__main__":
    main()
