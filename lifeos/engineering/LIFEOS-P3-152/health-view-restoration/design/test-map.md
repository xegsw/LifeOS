# 健康辅助查看影响面

1. 纯请求解析：重复键/未知字段/版本/operation/JSON替代Raw/超4096bytes，以及metric、days、endDay、source-offset对、source字节、offset、groupPage边界；先验证再开库。
2. 沿150 R1 Reader原15项小夹具正负测试；large_fixture改为本增量自有夹具，禁止读150临时目录。新增get_today授权否决、只读返回不改Store revision/业务记录/健康库字节、初始化日期与来源分页兼容。
3. 前端原9项Controller/内容测试复用；新增按需实例不预读、退出阻断后续串行请求和迟到更新、重新进入新实例、详情/趋势/过滤不影响对话草稿。
4. 原44项Host和10项TS→Host是共享主入口/Store依赖受影响回归，复跑一次。若新增逻辑失败，先修其影响，不整轮历史重跑。
5. 构建两种模式；真实仅构建不启动、不读窗口。少量合成视觉仅检查辅助区和原壳组合，不重新拍设置全部状态。
