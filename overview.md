# 通用 API 节点「模型下拉框」根因修复（v2.4.1）

## 完成内容
针对最早的核心需求「节点上直接选模型」此前未实现的问题，做了根因级修复：

**根因**：`model` 下拉框此前只展示 14 家厂商预设模型的并集（gpt-4o / dall-e-3 / llava …），而非节点自身 `base_url` 的真实模型列表，导致中转/自定义端点（如 `token.s...`）选不到真实模型。

**修复方案（plan C：JS 自动拉取 + 执行时校验）**
1. **新增前端扩展 `web/lk_universal_models.js`**：节点创建 / `base_url` / `api_key` 变化时，自动 `POST /lk_universal/fetch_models` 拉取该端点的 `/models`，动态填充 `model` 下拉框（combo `options.values` 实时更新；当前选中值在列表内则保留）；失败静默回退。
2. **`__init__.py` 服务端代理路由 `POST /lk_universal/fetch_models`**：接收 `{base_url, api_key, filter_keyword?}`，调用 `UniversalAPIClient.list_models()`，返回 `{ok, models}`，并写入全局 `UNIVERSAL_MODEL_CACHE`。
3. **`__init__.py` 注册 `WEB_DIRECTORY = .../web`**，让 ComfyUI 自动加载前端扩展。
4. **`nodes/universal_nodes.py` 执行时硬校验**：新增 `_validate_model()`，在 9 个模型类节点（TextGen / Chat / ImageGen / ImageEdit / VideoGen / Vision / Structured / ToolUse / BatchChat）创建 client 后立即校验——空模型直接报错；若缓存非空且所选 model 不在已拉取列表中，抛出 `UniversalAPIError` 由现有 `except` 分支转换为明确报错，避免用错模型静默失败。
5. 版本 2.4.0 → 2.4.1（PATCH）；`CHANGELOG.md` 增加 `[2.4.1]` 条目。

## 验证
- `py_compile` 对 `__init__.py`、`nodes/universal_nodes.py` 等全部通过
- `node --check` 对前端扩展通过
- 9 个节点的校验调用已全部插入；修正了编辑过程中的 3 处打字错误（`role` / `if` / `system_instruction`）

## 用户需知
- 这是纯本地插件代码，**需重启 / 重载 ComfyUI** 才能生效（前端 JS 与后端路由均在加载时注册）。
- 节点 `model` 会在你填写端点后自动拉取真实模型；若曾手动填写下拉外的模型名且缓存非空，会被明确拦截提示先刷新。

## 后续
- 如需纳入版本控制，按 Push Gate 走「分支 + PR」（未直推，等你确认）。
