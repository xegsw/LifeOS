import csv
from pathlib import Path

SOURCE = Path("/Users/xxe/Documents/codex_fixed_assets_20260630.csv")
OUTPUT = Path("/Users/xxe/Documents/No.2/update_IDecDeprMonths_from_excel.sql")


def sql_nvarchar(value: str) -> str:
    return "N'" + value.replace("'", "''") + "'"


with SOURCE.open("r", encoding="utf-8-sig", newline="") as source_file:
    rows = list(csv.DictReader(source_file))

values = []
for row_number, row in enumerate(rows, start=2):
    card_no = (row.get("卡片编号") or "").strip()
    months_text = (row.get("已计提月份") or "").strip()
    if card_no.startswith("合计:"):
        continue
    if not card_no:
        raise ValueError(f"第 {row_number} 行缺少卡片编号")
    try:
        months = int(months_text)
    except ValueError as exc:
        raise ValueError(f"第 {row_number} 行已计提月份不是整数: {months_text!r}") from exc
    values.append(f"    ({sql_nvarchar(card_no)}, {months})")

sql = f"""-- 数据来源：2026年固定资产卡片清单--截止2026.06.30.xls
-- 共 {len(values)} 条。默认仅预演并回滚；核对结果后把 @PreviewOnly 改为 0。
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @SchemaName  sysname = N'dbo';
DECLARE @TableName   sysname = N'fa_cards';
DECLARE @MatchColumn sysname = N'sCardNum';       -- 对应 Excel 的“卡片编号”
DECLARE @TargetColumn sysname = N'IDecDeprMonths';
DECLARE @PreviewOnly bit = 1;                     -- 1=回滚预演，0=正式提交

CREATE TABLE #ExcelDeprMonths
(
    CardNo         nvarchar(100) NOT NULL,
    IDecDeprMonths int NOT NULL
);

INSERT INTO #ExcelDeprMonths (CardNo, IDecDeprMonths)
VALUES
{',\n'.join(values)};

-- Excel 数据自身校验：卡片编号不可重复。
IF EXISTS
(
    SELECT 1
    FROM #ExcelDeprMonths
    GROUP BY CardNo
    HAVING COUNT(*) > 1
)
BEGIN
    SELECT CardNo, COUNT(*) AS DuplicateCount
    FROM #ExcelDeprMonths
    GROUP BY CardNo
    HAVING COUNT(*) > 1;
    RAISERROR(N'Excel 数据中存在重复卡片编号，已停止更新。', 16, 1);
    RETURN;
END;

DECLARE @QualifiedTable nvarchar(517) = QUOTENAME(@SchemaName) + N'.' + QUOTENAME(@TableName);

IF OBJECT_ID(@QualifiedTable, N'U') IS NULL
BEGIN
    RAISERROR(N'目标表不存在，请检查 @SchemaName 和 @TableName。', 16, 1);
    RETURN;
END;

IF COL_LENGTH(@SchemaName + N'.' + @TableName, @MatchColumn) IS NULL
BEGIN
    RAISERROR(N'匹配字段不存在，请检查 @MatchColumn。', 16, 1);
    RETURN;
END;

IF COL_LENGTH(@SchemaName + N'.' + @TableName, @TargetColumn) IS NULL
BEGIN
    RAISERROR(N'目标字段不存在，请检查 @TargetColumn。', 16, 1);
    RETURN;
END;

CREATE TABLE #Changes
(
    CardNo   nvarchar(100),
    OldMonths int NULL,
    NewMonths int NULL
);

BEGIN TRANSACTION;

DECLARE @Sql nvarchar(max) = N'
-- 未匹配到数据库记录的 Excel 卡片：
SELECT E.CardNo, E.IDecDeprMonths
FROM #ExcelDeprMonths AS E
WHERE NOT EXISTS
(
    SELECT 1
    FROM ' + @QualifiedTable + N' AS T
    WHERE CONVERT(nvarchar(100), T.' + QUOTENAME(@MatchColumn) + N') = E.CardNo
);

-- 若数据库中一个卡片编号对应多行，停止执行，避免误更新：
IF EXISTS
(
    SELECT 1
    FROM ' + @QualifiedTable + N' AS T
    INNER JOIN #ExcelDeprMonths AS E
        ON CONVERT(nvarchar(100), T.' + QUOTENAME(@MatchColumn) + N') = E.CardNo
    GROUP BY E.CardNo
    HAVING COUNT(*) > 1
)
BEGIN
    SELECT E.CardNo, COUNT(*) AS DatabaseMatchCount
    FROM ' + @QualifiedTable + N' AS T
    INNER JOIN #ExcelDeprMonths AS E
        ON CONVERT(nvarchar(100), T.' + QUOTENAME(@MatchColumn) + N') = E.CardNo
    GROUP BY E.CardNo
    HAVING COUNT(*) > 1;
    RAISERROR(N''数据库中存在一个卡片编号对应多行的情况，已停止更新。'', 16, 1);
    RETURN;
END;

UPDATE T
SET T.' + QUOTENAME(@TargetColumn) + N' = E.IDecDeprMonths
OUTPUT
    E.CardNo,
    CONVERT(int, deleted.' + QUOTENAME(@TargetColumn) + N'),
    CONVERT(int, inserted.' + QUOTENAME(@TargetColumn) + N')
INTO #Changes (CardNo, OldMonths, NewMonths)
FROM ' + @QualifiedTable + N' AS T
INNER JOIN #ExcelDeprMonths AS E
    ON CONVERT(nvarchar(100), T.' + QUOTENAME(@MatchColumn) + N') = E.CardNo
WHERE ISNULL(CONVERT(int, T.' + QUOTENAME(@TargetColumn) + N'), -2147483648)
      <> E.IDecDeprMonths;';

EXEC sys.sp_executesql @Sql;

SELECT
    (SELECT COUNT(*) FROM #ExcelDeprMonths) AS ExcelRowCount,
    (SELECT COUNT(*) FROM #Changes) AS ChangedRowCount;

SELECT CardNo, OldMonths, NewMonths
FROM #Changes
ORDER BY CardNo;

IF @PreviewOnly = 1
BEGIN
    ROLLBACK TRANSACTION;
    PRINT N'预演完成：事务已回滚，数据库未发生永久修改。';
END
ELSE
BEGIN
    COMMIT TRANSACTION;
    PRINT N'更新完成：事务已提交。';
END;
"""

OUTPUT.write_text(sql, encoding="utf-8-sig")
print(f"generated {OUTPUT} with {len(values)} rows")
