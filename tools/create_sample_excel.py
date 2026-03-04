"""Create a sample Excel workbook for manual testing of app.py."""

from pathlib import Path

import pandas as pd


OUTPUT_PATH = Path("sample_data.xlsx")


def main() -> None:
    sales = pd.DataFrame(
        {
            "Order Date": pd.date_range("2024-01-01", periods=12, freq="MS"),
            "Region": ["North", "South", "East", "West"] * 3,
            "Revenue": [1200, 980, 1430, 1110, 1600, 1025, 1510, 1320, 1495, 1700, 1630, 1580],
            "Units": [12, 9, 14, 11, 16, 10, 15, 13, 15, 17, 16, 15],
            "Active": ["Yes", "No", "Yes", "Yes"] * 3,
        }
    )

    support = pd.DataFrame(
        {
            "Ticket ID": [f"T-{i:04d}" for i in range(1, 21)],
            "Created": pd.date_range("2024-02-01", periods=20, freq="D"),
            "Priority": ["Low", "Medium", "High", "Critical", "Medium"] * 4,
            "Resolution Hours": [2.5, 5.0, 12.0, 24.0, 8.0] * 4,
            "Resolved": ["true", "true", "false", "true", "false"] * 4,
        }
    )

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        sales.to_excel(writer, sheet_name="Sales", index=False)
        support.to_excel(writer, sheet_name="Support", index=False)

    print(f"Created sample workbook at: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
