# 清理 marker 换行拒绝

首次创建 marker 使用了带尾随换行的 `printf`。清理脚本的初始字节严格比较在删除前返回 `required marker mismatched`（exit 66）；没有删除动作。脚本随后改为只规范化 marker 的终止换行，仍要求相同的唯一 marker 内容和精确临时根。
