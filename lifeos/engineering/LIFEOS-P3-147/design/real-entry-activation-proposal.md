# P3-147 用户操作入口与激活条件

当前仅完成可操作的连接说明与合成演练，真实接入未激活。基线为801e478a5bf0c62a87d740c68a765fc219e81406。本轮PM明确授权普通产品工程，不执行独立复评或改变被平台拦截的安全检查。

## 已实现

Settings → 数据与隐私 → 来源 → 查看连接说明，可展开/收起。只展示PM提供的两个路径字符串，不对路径执行任何文件操作。打开说明不发送IPC；“连接此目录（未激活）”为原生disabled按钮，无真实连接handler。下方“连接合成目录”继续使用原25IPC与两个固定合成profile。后端Rust、root_profiles、Schema、FD保护均逐字不变。

## 激活前必须明确的决定

1. 用户明确批准：只读接入唯一来源 /Users/xxe/IT-obstain，并在唯一新输出根 /Users/xxe/Documents/LifeOS-Source-Pilot-1 保存 capture.sqlite、artifacts原件缓存与.runtime解析临时产物。SQLite及原件不加密；0700目录/0600文件权限不是加密；配置受限且不进入普通上下文。不沿用145/144的真实库、不迁移、不自动删除。
2. PM批准固定profile/API映射方案。本轮只提出，未实施：增加单独编译期source-pilot-1 profile，固定唯一只读源与上述输出根；不接受运行时任意root或UI任意路径。保持25IPC名称及既有payload，仅真实profile的connect_source_directory映射至固定授权源。新profile的marker owner、仓储文件名capture.sqlite、权限和输出FD边界须与合成profile明确区分；build/runtime profile不匹配仍拒绝。
3. 在批准后的接线实现中，启动及查看说明不探测真实源、不建库；用户点击连接后才校验来源与新输出所有权。已存在非本任务资产时停止，不补造marker、不覆盖。真实模式禁止stdio内容调试、正文日志/AX/截图/Evidence导出；不启用网页/目录外文件授权、Provider或后台定时扫描。如何在不新增IPC的情况下惰性初始化仓储，需要在真实接线中落实，不能仅换root字符串。
4. 批准方案、完成相应普通合成验证并明确用户启动真实App的授权后，才发布可激活版本。用户在App执行实际连接；Agent不读取或转述真实内容。技术接线未完成之前，即使已有方向同意也不会解除当前按钮禁用。

## 评审状态及剩余风险

User-directed review waiver / No Independent Pass。用户经PM明确停止独立复评；未重新运行、改写或换会话绕过平台拦截。原IR-P0-147-001和Rework、801e478a工程修正及原未完成8行保留为历史。独立安全效果未确认，不能写L3完整Pass、风险关闭或正式真实能力验收。合成普通功能通过不能替代该缺失判断。

## 本轮可验证范围

6项普通检查：说明开关零IPC、真实按钮禁用、UI连接并自动处理6夹具、暂停跨进程重启/继续、检索、刷新、断开后重启（组合为6组）。不调用authorize_source_target，不执行安全反例runner。桌面/窄屏actual App核对入口、进度、暂停重启/恢复和检索，全部为既有合成内容。
