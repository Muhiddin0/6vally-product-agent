import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from services.product_service import ProductService


def test():
    service = ProductService()

    # Test IDs
    # 609: Header-like row in Excel
    # 606: Valid numeric row
    # 999: Unknown ID
    test_ids = [606, 602, 600, 596, 593, 584, 574, 568, 561]

    print("Testing _get_mxik_codes implementation:")
    print("-" * 40)
    for tid in test_ids:
        mxik, package = service._get_mxik_codes(tid)
        print(f"Sub-category ID: {tid}")
        print(f"  MXIK:    {mxik} (type: {type(mxik).__name__})")
        print(f"  Package: {package} (type: {type(package).__name__})")
        print("-" * 40)


if __name__ == "__main__":
    test()
