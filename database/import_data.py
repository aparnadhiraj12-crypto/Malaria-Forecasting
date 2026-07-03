import sqlite3
import pandas as pd

# =====================================================
# CONNECT DATABASE
# =====================================================

conn = sqlite3.connect(
    r"C:\Users\M. Srinivasa Rao\Shraddha Code\Forecasting\database\malaria.db"
)

cursor = conn.cursor()

# =====================================================
# CSV FILES
# =====================================================

STATE_FILES = {
    "Assam": r"C:\Users\M. Srinivasa Rao\Shraddha Code\Forecasting\data\assam.csv",
    "Tripura": r"C:\Users\M. Srinivasa Rao\Shraddha Code\Forecasting\data\tripura.csv",
    "Meghalaya": r"C:\Users\M. Srinivasa Rao\Shraddha Code\Forecasting\data\meghalaya.csv",
    "Arunachal Pradesh": r"C:\Users\M. Srinivasa Rao\Shraddha Code\Forecasting\data\arunachalpradesh.csv"
}

# =====================================================
# IMPORT DATA
# =====================================================

for state_name, file_path in STATE_FILES.items():

    print(f"Importing {state_name}...")

    df = pd.read_csv(file_path)

    # Convert Month to datetime
    df["Month"] = pd.to_datetime(
        df["Month"],
        format="%d-%m-%Y"
    )

    # Insert records
    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT OR IGNORE INTO malaria_cases
            (state, month, cases, log_cases)

            VALUES (?, ?, ?, ?)
            """,
            (
                state_name,
                row["Month"].strftime("%Y-%m-%d"),
                int(row["Cases"]),
                float(row["LogCases"])
            )
        )

conn.commit()
conn.close()

print("\n====================================")
print("All data imported successfully!")
print("====================================")