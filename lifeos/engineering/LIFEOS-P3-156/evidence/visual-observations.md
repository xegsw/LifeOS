# P3-156 合成 actual App 观察

2026-09-10，CUA只选择精确合成App路径；未列举/选择真实App。初始直接PID79815，通过proc_pidpath核对精确包内binary；窗口标题LifeOS P3-156 - Synthetic Conversation，AX standard window → scroll area → HTML content，URL tauri://localhost。

在该窗口输入“我明天先整理合成报告结论。”并Return，AX显示原始表达、本地记录“已记下”和Today单个“已说定的安排”。没有采纳/保存/完成必经按钮。

CUA getAXStateAndScreenshot显示正常宽窗；通过该窗口右下角拖动收窄后，getScreenshot显示对话文字、输入框和发送按钮仍可见，无横向截断。对话侧栏覆盖部分Today是继承的浮层行为；不把浮层打开时的背景遮挡当作正文不可达。没有声称测量了精确逻辑像素或全视口覆盖。

随后输入“报告结论做完了。”，AX显示“本地记录：已完成”，Today不再显示该Focus。Cmd-Q正常退出79815，再从同一已核对binary直接启动PID79905；点击与LifeOS聊聊，AX同时显示先前原文与完成反馈，Today仍无已完成Focus。再次Cmd-Q正常退出，保留合成数据库。

两次输入中的CUA setValue返回元素过期，但随后新AX确认文字已写入，独立Return才提交；未重复输入或重复创建，属于重新渲染后的定位更新。没有候选失败或边界接触。

截图为本任务CUA工具原生内联图像，可在当前任务01a07f0e-dbbd-7d23-9e6d-68f2152f9484查看；未伪造本地PNG路径或声称存在截图hash。此L2包保存观察、进程/启动/重启收据，不把会话内图片冒充独立可下载证据。最终包随后只新增旧建议status提交复核，UI/Domain展示代码未改变，本观察按影响面复用；最终包另核启动身份与只读恢复。不是独立评审或真实用户验收。
