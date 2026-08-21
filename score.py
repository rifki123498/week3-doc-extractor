import json
from pathlib import Path

from extractor import extract


GOLDEN_DIR = Path("golden")


def score_document(doc_path: Path, expected_path: Path) -> tuple[int, int]:
    document = doc_path.read_text(encoding="utf-8")

    expected = json.loads(
        expected_path.read_text(encoding="utf-8")
    )

    result = extract(document)
    actual = result.model_dump()

    correct_fields = 0

    for field, expected_value in expected.items():
        actual_value = actual.get(field)

        if actual_value == expected_value:
            correct_fields += 1
        else:
            print(f"\n  MISMATCH: {field}")
            print(f"  Expected: {expected_value}")
            print(f"  Actual:   {actual_value}")

    total_fields = len(expected)

    return correct_fields, total_fields


def main() -> None:
    total_correct = 0
    total_fields = 0
    passed_documents = 0

    print("Golden Set Evaluation — Prompt V1")
    print("---------------------------------\n")

    for number in range(1, 10):
        doc_path = GOLDEN_DIR / f"doc_{number:02}.txt"
        expected_path = GOLDEN_DIR / f"expected_{number:02}.json"

        try:
            correct, total = score_document(
                doc_path,
                expected_path,
            )

            total_correct += correct
            total_fields += total

            if correct == total:
                passed_documents += 1
                status = "PASS"
            else:
                status = "FAIL"

            print(
                f"doc_{number:02}: "
                f"{correct}/{total} fields — {status}"
            )

        except Exception as error:
            print(
                f"doc_{number:02}: ERROR — "
                f"{type(error).__name__}: {error}"
            )

    print("\nOverall Results")
    print("---------------")

    if total_fields > 0:
        accuracy = total_correct / total_fields
        print(
            f"Field accuracy: "
            f"{total_correct}/{total_fields} "
            f"({accuracy:.1%})"
        )

    print(f"Documents passing: {passed_documents}/9")


if __name__ == "__main__":
    main()