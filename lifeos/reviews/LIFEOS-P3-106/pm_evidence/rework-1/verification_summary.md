# LIFEOS-P3-106 PM Evidence｜rework-1

- Frozen ABF：`ABF-P3-106-v1`，SHA-256 `1aa076a289173eb0dbd4e17ccfd3a1af89cbd9f815ad656d31d9318a5172a5c4`，本轮未修改。
- Engineering Manifest：325 项；提交 verifier 与 PM 独立 `shasum -a 256 -c` 两种复算均为 325/325，零 missing、零 extra、无 self-reference。
- 源码闭环：旧禁止路径只在 `legacy_metadata.py` 以 `os.lstat` 获取存在性、类型、size、mtime_ns、ctime_ns；PM 定向追踪全部引用，未发现 open/read/hash/copy/write/delete 内容路径。cleanup 和 finalizer 均在动作／结论前拒绝禁止表达式。
- 结果闭环：M001–M018 均由条件规则生成，18/18 PASS；不再无条件写入 M016–M018。静态 40/40、runtime 7/7、动态 38/38，离线 locked test/build/bundle 退出码均为 0。
- 历史保全：PM 独立复算 protected snapshot 144/144 hash 未变；旧禁止文件只做 lstat，metadata 与工程 before/after 完全相等；允许夹具残留为 0。
- 显示恢复：目视原始截图为第 4 档默认、临时截图为第 5 档更多空间、恢复截图回到第 4 档默认。三张基准图均为 1280×1024；恢复后的三态工作区图均为 1160×768，窄窗口为 700×760，未见关键操作裁切或不可达。
- PM 未执行提交的会改动 app／显示环境的全量 runner，也未创建 PM 测试夹具；本轮通过只读独立复算关闭两个既有 finding，PM 临时残留为 0。
- Local Precheck 跳过：本轮属于授权、显示恢复和本地文件禁止读取的高风险最终判断，本地模型不得代判。
- 最终：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0；PM Pass，等待用户采纳；Not Frozen。
