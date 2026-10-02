"""Create sample_recital.xlsx from sample_recital.csv. Run from the project root."""
import csv
from pathlib import Path

from openpyxl import Workbook

folder = Path(__file__).parent
workbook = Workbook()
sheet = workbook.active

with open(folder / "sample_recital.csv", newline="", encoding="utf-8") as file:
    for row in csv.reader(file):
        sheet.append([cell if cell else None for cell in row])

workbook.save(folder / "sample_recital.xlsx")
print("Created sample_recital.xlsx")