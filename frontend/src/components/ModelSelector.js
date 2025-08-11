import React from "react";

const OPTIONS = [
  { key: "fast", label: "Ultra-Fast", icon: "⚡", desc: "Real-time, low-latency" },
  { key: "balanced", label: "Balanced", icon: "🎯", desc: "Speed + quality" },
  { key: "reasoning", label: "Reasoning", icon: "🧠", desc: "Complex analysis" },
  { key: "specialized", label: "Specialized", icon: "🔬", desc: "Advanced tasks" },
  { key: "safety", label: "Safety", icon: "🛡️", desc: "Content guardrails" }
];

export default function ModelSelector({ value, onChange, className = "" }) {
  return (
    <div className={`model-selector ${className}`}>
      <div className="selector-header">
        <h4 className="heading-sm">Model Preference</h4>
        <div className="selector-hint">Choose how the AI prioritizes performance</div>
      </div>
      <div className="selector-options">
        {OPTIONS.map((opt) => (
          <button
            key={opt.key}
            className={`selector-option ${value === opt.key ? "active" : ""}`}
            onClick={() => onChange(opt.key)}
            title={`${opt.label} • ${opt.desc}`}
          >
            <span className="option-icon">{opt.icon}</span>
            <span className="option-text">
              <span className="option-label">{opt.label}</span>
              <span className="option-desc">{opt.desc}</span>
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}