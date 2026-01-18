import pandas as pd
from pathlib import Path


def test_mxik_lookup(sub_category_id):
    default_mxik = 12
    default_package = 12

    try:
        excel_path = Path("api/mxik-codes.xlsx")
        df = pd.read_excel(excel_path, header=None)
        match = df[df[0] == sub_category_id]
        if not match.empty:
            mxik = match.iloc[0, 3]
            package_code = match.iloc[0, 4]
            try:
                if pd.notna(mxik):
                    mxik = int(mxik)
                if pd.notna(package_code):
                    package_code = int(package_code)
            except:
                pass
            return mxik, package_code
        return default_mxik, default_package
    except Exception as e:
        return f"Error: {e}"


test_ids = [609, 606, 999]
for tid in test_ids:
    print(f"ID {tid} -> {test_mxik_lookup(tid)}")
