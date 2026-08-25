// LK Universal Models — ComfyUI 前端扩展
// 在节点创建 / base_url 变化时，自动从该端点 GET /models（经服务端代理）
// 拉取真实模型列表，动态填充节点的 model 下拉框。
//
// 触发条件：节点 category 包含 "通用 API" 且同时具备 base_url 与 model 两个 widget。
// 失败时静默回退：保留当前 options.values（不破坏既有下拉）。

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "LK.UniversalModels",
    async beforeRegisterNodeDef(nodeType, nodeData /*, appRef */) {
        const category = (nodeData && nodeData.category) || "";
        if (!category.includes("通用 API")) return;

        const origOnCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const ret = origOnCreated ? origOnCreated.apply(this, arguments) : undefined;

            const widgets = this.widgets || [];
            const modelWidget = widgets.find(w => w.name === "model");
            const baseWidget = widgets.find(w => w.name === "base_url");
            const keyWidget  = widgets.find(w => w.name === "api_key");
            if (!modelWidget || !baseWidget) return ret;

            // 强制把 model 字段标记为 combo（即便默认 options 为空也允许动态填充）
            if (!Array.isArray(modelWidget.options)) modelWidget.options = {};
            if (!Array.isArray(modelWidget.options.values)) modelWidget.options.values = [];

            let timer = null;
            const refresh = () => {
                const baseUrl = String(baseWidget.value || "").trim().replace(/\/+$/, "");
                if (!baseUrl) return;
                const apiKey = keyWidget ? String(keyWidget.value || "").trim() : "";
                fetch("/lk_universal/fetch_models", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ base_url: baseUrl, api_key: apiKey })
                })
                .then(r => r.json().then(d => ({ status: r.status, body: d })))
                .then(({ status, body }) => {
                    if (status === 200 && body && body.ok && Array.isArray(body.models) && body.models.length) {
                        const prev = modelWidget.value;
                        modelWidget.options.values = body.models;
                        if (!body.models.includes(prev)) {
                            modelWidget.value = body.models[0];
                        }
                        // 触发重绘
                        if (typeof this.setDirtyCanvas === "function") {
                            this.setDirtyCanvas(true, true);
                        }
                    }
                })
                .catch(() => { /* 静默：保留当前下拉 */ });
            };
            const debounced = () => {
                if (timer) clearTimeout(timer);
                timer = setTimeout(refresh, 400);
            };

            // 初次拉取（节点刚建立、默认值就位后）
            setTimeout(refresh, 600);

            // 监听 base_url / api_key 变化 → 防抖重拉
            const wrapCallback = (widget) => {
                if (!widget || typeof widget.callback !== "function") {
                    widget.callback = function (v) { debounced(); };
                    return;
                }
                const orig = widget.callback;
                widget.callback = function (v) {
                    const r = orig.apply(this, arguments);
                    debounced();
                    return r;
                };
            };
            wrapCallback(baseWidget);
            if (keyWidget) wrapCallback(keyWidget);

            return ret;
        };
    }
});
