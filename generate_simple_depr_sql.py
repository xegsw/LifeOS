import csv
from pathlib import Path

source = Path("/Users/xxe/Documents/codex_fixed_assets_20260630.csv")
output = Path("/Users/xxe/Documents/No.2/update_IDecDeprMonths_simple.sql")

with source.open("r", encoding="utf-8-sig", newline="") as f:
    source_rows = csv.DictReader(f)
    rows = []
    for row in source_rows:
        card_no = (row.get("卡片编号") or "").strip()
        months = (row.get("已计提月份") or "").strip()
        if card_no.startswith("合计:"):
            continue
        if not card_no or not months:
            raise ValueError("卡片编号或已计提月份为空")
        card_sql = card_no.replace("'", "''")
        rows.append(f"        (N'{card_sql}', {int(months)})")

sql = """UPDATE C
SET C.IDecDeprMonths = V.IDecDeprMonths
FROM dbo.fa_cards AS C
INNER JOIN
(
    VALUES
""" + ",\n".join(rows) + """
) AS V (sCardNum, IDecDeprMonths)
    ON CONVERT(nvarchar(100), C.sCardNum) = V.sCardNum;
"""

output.write_text(sql, encoding="utf-8-sig")
print(f"generated {output} with {len(rows)} values")
