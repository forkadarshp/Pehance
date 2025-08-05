import React from 'react';

const ModelStatusBoard = ({ modelStatus, className = '' }) => {
  if (!modelStatus) return null;

  const totalModels = Object.keys(modelStatus).length;
  const availableModels = Object.values(modelStatus).filter(m => m.available).length;
  const healthPercentage = Math.round((availableModels / totalModels) * 100);

  const getStatusColor = (available) => {
    return available ? 'var(--color-brand-success)' : 'var(--color-brand-error)';
  };

  const getTierBadgeColor = (tier) => {
    const colors = {
      1: 'var(--color-brand-success)',
      2: 'var(--color-brand-primary)', 
      3: 'var(--color-brand-accent)',
      4: 'var(--color-brand-warning)'
    };
    return colors[tier] || 'var(--color-text-tertiary)';
  };

  return (
    <div className={`model-status-board ${className}`}>
      <div className="status-header">
        <div className="status-title">
          <h3>AI Model Status</h3>
          <div className="status-summary">
            <span className="available-count">{availableModels}/{totalModels}</span>
            <span className="health-indicator">
              <div 
                className="health-bar" 
                style={{ width: `${healthPercentage}%` }}
              ></div>
            </span>
            <span className="health-percentage">{healthPercentage}%</span>
          </div>
        </div>
      </div>

      <div className="models-grid">
        {Object.entries(modelStatus).map(([modelName, modelInfo]) => (
          <div 
            key={modelName}
            className={`model-card ${modelInfo.available ? 'available' : 'unavailable'}`}
          >
            <div className="model-header">
              <div className="model-name" title={modelName}>
                {modelName.replace(/^.*\//, '')}
              </div>
              <div 
                className="status-dot"
                style={{ backgroundColor: getStatusColor(modelInfo.available) }}
              ></div>
            </div>
            
            <div className="model-details">
              {modelInfo.tier && (
                <div 
                  className="tier-badge"
                  style={{ color: getTierBadgeColor(modelInfo.tier) }}
                >
                  Tier {modelInfo.tier}
                </div>
              )}
              
              <div className="model-specs">
                {modelInfo.features && (
                  <div className="features">
                    {modelInfo.features.slice(0, 2).map((feature, index) => (
                      <span key={index} className="feature-tag">
                        {feature}
                      </span>
                    ))}
                  </div>
                )}
                
                {modelInfo.performance && (
                  <div className="performance">
                    <div className="perf-label">Speed</div>
                    <div className="perf-bar">
                      <div 
                        className="perf-fill"
                        style={{ 
                          width: `${modelInfo.performance.speed * 20}%`,
                          backgroundColor: getTierBadgeColor(modelInfo.tier)
                        }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {!modelInfo.available && (
              <div className="unavailable-overlay">
                <span className="unavailable-text">Offline</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <style jsx>{`
        .model-status-board {
          background: var(--gradient-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-2xl);
          padding: var(--space-6);
          box-shadow: var(--shadow-lg);
        }

        .status-header {
          margin-bottom: var(--space-6);
        }

        .status-title {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: var(--space-4);
        }

        .status-title h3 {
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--color-text-primary);
          margin: 0;
        }

        .status-summary {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          font-size: 0.875rem;
        }

        .available-count {
          font-weight: 600;
          color: var(--color-brand-primary);
        }

        .health-indicator {
          width: 60px;
          height: 6px;
          background: var(--color-surface-hover);
          border-radius: var(--radius-full);
          overflow: hidden;
          position: relative;
        }

        .health-bar {
          height: 100%;
          background: linear-gradient(90deg, var(--color-brand-error), var(--color-brand-warning), var(--color-brand-success));
          border-radius: var(--radius-full);
          transition: var(--transition-all);
        }

        .health-percentage {
          font-weight: 600;
          color: var(--color-text-secondary);
        }

        .models-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: var(--space-4);
        }

        .model-card {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-xl);
          padding: var(--space-4);
          position: relative;
          transition: var(--transition-all);
        }

        .model-card:hover {
          transform: translateY(-1px);
          box-shadow: var(--shadow-lg);
          border-color: var(--color-brand-primary);
        }

        .model-card.unavailable {
          opacity: 0.6;
          background: var(--color-surface-hover);
        }

        .model-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: var(--space-3);
        }

        .model-name {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--color-text-primary);
          font-family: var(--font-mono);
          truncate: true;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .model-details {
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
        }

        .tier-badge {
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .model-specs {
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
        }

        .features {
          display: flex;
          gap: var(--space-1);
          flex-wrap: wrap;
        }

        .feature-tag {
          background: var(--color-surface-elevated);
          color: var(--color-text-tertiary);
          font-size: 0.75rem;
          padding: var(--space-1) var(--space-2);
          border-radius: var(--radius-md);
          border: 1px solid var(--color-border);
        }

        .performance {
          display: flex;
          align-items: center;
          gap: var(--space-2);
        }

        .perf-label {
          font-size: 0.75rem;
          color: var(--color-text-tertiary);
          min-width: 40px;
        }

        .perf-bar {
          flex: 1;
          height: 4px;
          background: var(--color-surface-hover);
          border-radius: var(--radius-full);
          overflow: hidden;
        }

        .perf-fill {
          height: 100%;
          border-radius: var(--radius-full);
          transition: var(--transition-all);
        }

        .unavailable-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(220, 38, 38, 0.1);
          backdrop-filter: blur(2px);
          border-radius: var(--radius-xl);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .unavailable-text {
          background: var(--color-brand-error);
          color: white;
          padding: var(--space-1) var(--space-3);
          border-radius: var(--radius-full);
          font-size: 0.75rem;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
};

export default ModelStatusBoard;