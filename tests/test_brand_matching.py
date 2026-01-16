import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.category_brand.agent import _match_brand


def test_brand_matching():
    brands = [
        {"id": 1, "name": "Samsung"},
        {"id": 2, "name": "Apple"},
        {"id": 3, "name": "Nike"},
        {"id": 4, "name": "Adidas"},
        {"id": 5, "name": "Unknown"},
    ]

    test_cases = [
        ("Samsung", 1),  # Exact match
        ("samsung", 1),  # Case-insensitive
        ("Apple ", 2),  # Whitespace
        ("Nik", 3),  # Fuzzy match
        ("Adiddas", 4),  # Typo
        ("Somewhere", 1),  # Fallback to first brand (current logic)
    ]

    print("Testing brand matching...")
    all_passed = True
    for input_name, expected_id in test_cases:
        actual_id = _match_brand(input_name, brands)
        if actual_id == expected_id:
            print(f"✅ Input: '{input_name}' -> Matched ID: {actual_id}")
        else:
            print(
                f"❌ Input: '{input_name}' -> Expected ID: {expected_id}, Got: {actual_id}"
            )
            all_passed = False

    if all_passed:
        print("\nAll brand matching tests passed!")
    else:
        print("\nSome brand matching tests failed.")


if __name__ == "__main__":
    test_brand_matching()
