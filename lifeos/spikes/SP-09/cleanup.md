# SP-09 清理说明

`work/` 中全部数据库均由确定性合成脚本生成，可重建，不是用户资产。轻量证据和脚本应保留。

如 PM 完成抽样复核，可仅删除以下明确目录以回收约 2.9 GiB：

```bash
rm -rf /Users/xxe/Documents/No.2/lifeos/spikes/SP-09/work/u10000
rm -rf /Users/xxe/Documents/No.2/lifeos/spikes/SP-09/work/u100000
rm -rf /Users/xxe/Documents/No.2/lifeos/spikes/SP-09/work/u1000000
```

本专项会话未执行清理。不要删除 `lifeos/spikes/SP-09/` 整体，也不要把仓库根目录、用户目录或变量/glob 作为清理目标。

