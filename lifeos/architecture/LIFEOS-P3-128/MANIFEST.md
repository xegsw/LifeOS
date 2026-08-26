# LIFEOS-P3-128 Stable Artifact Manifest

任务：`LIFEOS-P3-128`  
生成规则：SHA-256，覆盖所有稳定的主交付物、结构化 Evidence 与 verifier；`MANIFEST.md` 本身不自指，`verification.json` 为 verifier 运行产物，故不列入本表。

| 路径（相对本目录） | SHA-256 | 角色 |
|---|---|---|
| `frozen_input_impact.json` | 50958c40c630aa762f04435af228db1510114bd667be50a98a9e60e33ac8f903 | AC-01 固定输入影响矩阵 |
| `object_mapping.json` | d495fa641f3479e746e3e36c0216a223d1a9f9f704bc5c96443632ca709dde49 | AC-02 映射矩阵 |
| `context_lifecycle.json` | 384e546ad1e1cc5e14442f62814147aa8094d1072f9588bde79a0bdb1d0901e1 | AC-03 状态机 |
| `memory_provenance.json` | 019c86f2578bb1658421d7a3fb9313530edb7d8e24b80540b12333d702a5a045 | AC-04 记忆追溯 |
| `context_resolver_contract.json` | 6949e21b6c167611d9faaf1796ac1a1fe8bdfd62b15274c600ea619cd8097837 | AC-05 Resolver 合同 |
| `application_port_contract.json` | eacdb329d84262bd46e1102b3d95cfad82abdfd927fee81bc410ecb19f7e5387 | AC-06 分层／Port 合同 |
| `p3_126_compatibility.json` | 4978d496f959040c511bda860fa7cc95fe10bd58a09e639c07135aa728018e2d | AC-07 Runtime 事实矩阵 |
| `fast_track_handoff.json` | 4e15c8006275b10058d6c307a35ac4e04ebcb63e59a249ed0eaf09962eefd3fd | AC-08 工程 handoff |
| `negative_cases.json` | 52eff7d5707e664604b757a7a1c2dcaf01d7df1583fba58b87e30cb571669229 | AC-09 反例矩阵 |
| `verify_contract.py` | cc8e064b25d2c76ebdd597415ee8ffb1308d905d6e437caf27f6792628d40eb3 | fail-closed verifier |
| `../../deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md` | c385beb8267724945c7665f7a419e1358b5f1571a389055d7642fb660fca1a6b | AC-10 主交付物 |

验证命令：`python3 -B lifeos/architecture/LIFEOS-P3-128/verify_contract.py`
