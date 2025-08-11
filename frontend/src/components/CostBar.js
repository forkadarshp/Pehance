import React, { useMemo } from "react";

function estimateTokens(chars) {
  if (!chars || chars <= 0) return 0;
  return Math.ceil(chars / 4); // rough heuristic
}

function formatNumber(n) {
  if (n === 0) return "0";
  if (!n) return "-";
  return n.toLocaleString();
}

function getTierForModel(modelStatus, modelName) {
  if (!modelStatus || !modelName || !modelStatus[modelName]) return "-";
  return modelStatus[modelName].tier || "-";
}

function findRecommendedModel(preference, modelStatus, modelSummary) {
  if (!modelStatus) return null;
  // Try summary when available
  if (modelSummary) {
    if (preference === "fast" && modelSummary.recommended_fast) return modelSummary.recommended_fast;
    if (preference === "reasoning" && modelSummary.recommended_reasoning) return modelSummary.recommended_reasoning;
    if (preference === "specialized" && modelSummary.recommended_creative) return modelSummary.recommended_creative;
    if (preference === "safety" && modelSummary.safety_model) return modelSummary.safety_model;
  }
  // Otherwise scan by tier
  const entries = Object.entries(modelStatus);
  const byTier = (tier) => entries
    .filter(([, v]) => (v.tier === tier) && v.available)
    .sort((a, b) => (b[1].performance_tokens_sec || 0) - (a[1].performance_tokens_sec || 0));

  if (preference === "fast") {
    const best = byTier("Tier 1: Ultra-Fast");
    return best[0]?.[0] || null;
  }
  if (preference === "balanced") {
    const best = byTier("Tier 2: Balanced");
    return best[0]?.[0] || null;
  }
  if (preference === "reasoning") {
    const best = byTier("Tier 3: High-Reasoning");
    return best[0]?.[0] || null;
  }
  if (preference === "specialized") {
    const best = byTier("Tier 4: Specialized");
    return best[0]?.[0] || null;
  }
  if (preference === "safety") {
    const best = entries.find(([, v]) => v.tier === "Safety Models" && v.available);
    return best?.[0] || null;
  }
  return null;
}

export default function CostBar({
  prompt = "",
  enhanced = "",
  processingTime = 0,
  modelsUsed = null,
  preference = "balanced",
  modelStatus = null,
  modelSummary = null,
}) {
  const inputChars = prompt?.length || 0;
  const outputChars = enhanced?.length || 0;

  const inputTokens = useMemo(() => estimateTokens(inputChars), [inputChars]);
  const outputTokens = useMemo(() => estimateTokens(outputChars), [outputChars]);
  const totalTokens = inputTokens + outputTokens;

  const preferredModel = useMemo(
    () => findRecommendedModel(preference, modelStatus, modelSummary),
    [preference, modelStatus, modelSummary]
  );

  const preferredPerf = preferredModel && modelStatus && modelStatus[preferredModel]
    ? modelStatus[preferredModel].performance_tokens_sec
    : null;

  const chips = [];
  if (modelsUsed && typeof modelsUsed === "object") {
    Object.entries(modelsUsed).forEach(([stage, model]) => {
      if (model) chips.push({ stage, model });
    });
  } else if (typeof modelsUsed === "string") {
    chips.push({ stage: "enhancement", model: modelsUsed });
  }

  return (
    <div className="costbar card animate-fade-in-up">
      <div className="costbar-grid">
        <div className="cost-item">
          <div className="cost-label">Est. Tokens</div>
          <div className="cost-values">
            <span className="token-in">In: {formatNumber(inputTokens)}</span>
            <span className="token-out">Out: {formatNumber(outputTokens)}</span>
            <span className="token-total">Total: {formatNumber(totalTokens)}</span>
          </div>
        </div>

        <div className="cost-item">
          <div className="cost-label">Processing Time</div>
          <div className="cost-value">{processingTime ? `${processingTime}s` : "-"}</div>
        </div>

        <div className="cost-item">
          <div className="cost-label">Preference</div>
          <div className="cost-value pref">
            {preference === "fast" && "⚡ Ultra-Fast"}
            {preference === "balanced" && "🎯 Balanced"}
            {preference === "reasoning" && "🧠 Reasoning"}
            {preference === "specialized" && "🔬 Specialized"}
            {preference === "safety" && "🛡️ Safety"}
          </div>
          {preferredModel && (
            <div className="model-meta">
              <span className="model-name">{preferredModel}</span>
              <span className="model-tier">{getTierForModel(modelStatus, preferredModel)}</span>
              {preferredPerf && (
                <span className="model-perf">{preferredPerf} tok/s</span>
              )}
            </div>
          )}
        </div>

        {chips.length &gt; 0 &amp;&amp; (
          <div className="cost-item span-2">
            <div className="cost-label">Models Used</div>
            <div className="chips">
              {chips.map((c, idx) =&gt; (
                <div key={`${c.stage}-${idx}`} className="chip">
                  <span className="chip-stage">{c.stage}</span>
                  <span className="chip-model">{c.model}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}