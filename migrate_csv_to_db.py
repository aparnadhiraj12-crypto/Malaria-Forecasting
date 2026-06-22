from pathlib import Path
import pandas as pd
from malaria_db import init_db, bulk_add_dataframe

DATA_DIR = Path(__file__).parent / "data"


def main():
    init_db()

    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return

    for csv_path in csv_files:
        state = csv_path.stem  # "assam.csv" -> "assam"
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()  # handles stray spaces like "LogCases "

        # basic sanity check on expected columns
        if not {"Month", "LogCases"}.issubset(df.columns):
            print(f"  Skipping {csv_path.name}: missing Month/LogCases columns")
            continue

        bulk_add_dataframe(state, df)
        print(f"  Loaded {len(df)} rows for state '{state}'")

    print("Migration complete.")


if __name__ == "__main__":
    main()
