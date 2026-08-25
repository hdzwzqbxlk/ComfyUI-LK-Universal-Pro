# ComfyUI-LK-Universal-Pro 项目记忆

## Git 推送与 PR 纪律（项目铁律）
- 本机 git 一律走 **系统 SSH**：`git@github.com:hdzwzqbxlk/ComfyUI-LK-Universal-Pro.git`，通过 **pwsh MCP**（你系统的 PowerShell）执行。
- **绝不走 WorkBuddy 沙箱 Bash 的 git**：沙箱屏蔽 `git push` 网络出口，会在 push 上卡死/假成功，但 fetch/ls-remote 走代理可用——极易误判。视觉验证用 `git ls-remote`（SSH 秒回）即可。
- **凭据零明文**：绝不 `git credential fill` 取 GCM 明文 token（8/24 已因打印明文出过安全事故，token 已被吊销）。建 PR 走 **`gh` CLI**，gh 用本机 `GITHUB_TOKEN` 自行认证并掩码（`gho_****`），零明文接触。
- **Push Gate**：分支 + PR、禁直推 main。特性分支基于 `origin/main` 拉取，PR base=main。
- **PR 创建通道**：优先 **`gh` CLI**（`gh auth status` 确认 active 账号 `hdzwzqbxlk`、GITHUB_TOKEN、scope 含 `repo`）。`gh pr create --base main --head <branch> --title ... --body-file <tmp> --web=false` 非交互建 PR，token 由 gh 掩码管理，零明文。备选：GitHub Web 一键 `https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro/pull/new/<branch>`。
- **PR 合并通道**：同样走 **`gh` CLI**（`gh pr merge <n> --merge`，与 PR #1 风格一致保留 merge commit）。⚠️ `github` MCP 在本仓库仅有**读权限**——`merge_pull_request` 报 `403 Resource not accessible by integration`，写操作（合并/标签/关闭）一律用 `gh` CLI，不要浪费一次调用在 MCP 合并上。

## 代码结构要点
- 通用 API 层：`utils/api_client.py`(UniversalAPIClient) + `utils/provider_registry.py`(14 厂商预设+全局缓存) + `nodes/universal_nodes.py`(11 节点：工具/Chat/图像/视频/视觉/高级)。已移除 Gemini 专属体系（`GeminiAPIClient` 与 7 个 gemini 节点文件）。
- 11 节点清单：APIConfig, ModelFetcher, HealthCheck, ModelCompare（工具）；Chat（含单轮+会话）；ImageGen, ImageEdit（图像）；VideoGen（含图生视频）；Vision（视觉）；Advanced（结构化输出/工具调用二合一）；BatchChat, TokenEstimate（高级）。
- 图像转换复用 `utils/image_utils`，不重复造轮子。
- 版本号语义：仅大改动升 MINOR/MAJOR；修复/小幅优化走 PATCH（用户要求版本号不要跑太快）。当前 2.5.0。

## 关键历史
- 2026-08-24：v2.3.0/2.3.1 通用 API 兼容层（4 节点）→ PR #1 已合并 main（781b889）。分支 `feat/universal-api-compat` 已于 8/25 本地+远程清理。
- 2026-08-24：v2.4.0 通用 API 节点铺满 6 大类（15 节点）→ 分支 `feat/universal-nodes-v2` 已 push，PR #2 经 **`gh` CLI `--merge` 合并 main（d8f194d，保留 merge commit，风格同 PR #1）**。github MCP 合并报 403（仅读），已改用 gh。分支 `feat/universal-nodes-v2` 已于 8/25 合并后清理（本地+远程）。
- 2026-08-25：v2.5.0 重构——移除全部 Gemini 专项体系（18 节点/7 文件 + `GeminiAPIClient`），通用节点 15→11（Chat 吸收单轮/会话、VideoGen 加图生视频、Structured+ToolUse 合并为 Advanced）。PR #3 经 **`gh` CLI `--merge` 合并 main（14ef447，保留 merge commit）**，本地 main 已 ff 对齐（`d8f194d..14ef447`）。分支 `feat/refactor-universal` 已于 8/25 合并后清理（本地 `git branch -D` + 远程 SSH 删除）。
- 2026-08-25：v2.5.1 能力集成（用户指出 v2.5.0 只删 Gemini 没移植优秀功能，且明确"不加节点，能集成则集成"）：ImageGen +aspect_ratio/seed；ImageEdit +reference_images 多参考图(≤4)/seed；VideoGen +resolution/last_frame 尾帧；Vision +task_preset（含反推提示词，覆盖 ImageToPrompt）；Chat +file_path 文本文件注入（覆盖 DocumentProcess 文本场景）。分支 `feat/gemini-capability-integration`（7828790）已 push，PR #4 已建待合并。本机无 torch，节点逻辑验证用 AST 静态检查替代运行时单测。
