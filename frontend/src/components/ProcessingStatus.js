import React from 'react';

const ProcessingStatus = ({ 
  stage, 
  stageIndex, 
  stages, 
  isActive, 
  currentModel, 
  processingTime 
}) => {
  // Accessibility: live region updates and reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!isActive) return null;

  const progress = ((stageIndex + 1) / stages.length) * 100;
  const currentStage = stages[stageIndex] || {};

  return (
    <div className="processing-status animate-scale-in" role="status" aria-live="polite" aria-atomic="true">
      <div className="processing-header">
        <div className="processing-icon animate-glow">
          <div className="processing-spinner"></div>
        </div>
        <div className="processing-info">
          <h4 className="processing-title">{stage}</h4>
          <div className="processing-meta">
            <span className="processing-step">Step {stageIndex + 1} of {stages.length}</span>
            {processingTime && (
              <span className="processing-time">{processingTime}s</span>
            )}
          </div>
        </div>
      </div>

      <div className="processing-progress">
        <div className="progress">
          <div 
            className="progress-bar" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="progress-labels">
          <span className="progress-current">{Math.round(progress)}% Complete</span>
          <span className="progress-eta">~{Math.max(0, (stages.length - stageIndex - 1) * 2)}s remaining</span>
        </div>
      </div>

      <div className="processing-models">
        <div className="model-info">
          <div className="model-label">Current Agent</div>
          <div className="model-name">{currentStage.agent || 'Processing...'}</div>
        </div>
        {currentModel && (
          <div className="model-info">
            <div className="model-label">AI Model</div>
            <div className="model-name light-trail">{currentModel}</div>
          </div>
        )}
      </div>

      <div className="processing-stages">
        {stages.map((stageItem, index) => (
          <div 
            key={index}
            className={`stage-item ${index <= stageIndex ? 'completed' : ''} ${index === stageIndex ? 'active' : ''}`}
          >
            <div className="stage-icon">
              {index < stageIndex ? '✓' : index === stageIndex ? '○' : '○'}
            </div>
            <div className="stage-details">
              <div className="stage-name">{stageItem.name}</div>
              <div className="stage-agent">{stageItem.agent}</div>
            </div>
          </div>
        ))}
      </div>

      <style jsx>{`
        .processing-status {
          background: var(--gradient-glass);
          backdrop-filter: blur(20px);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-2xl);
          padding: var(--space-6);
          box-shadow: var(--shadow-xl);
          margin-top: var(--space-6);
        }

        .processing-header {
          display: flex;
          align-items: center;
          gap: var(--space-4);
          margin-bottom: var(--space-6);
        }

        .processing-icon {
          width: 40px;
          height: 40px;
          background: var(--gradient-brand);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }

        .processing-spinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        .processing-info {
          flex: 1;
        }

        .processing-title {
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--color-text-primary);
          margin-bottom: var(--space-1);
        }

        .processing-meta {
          display: flex;
          gap: var(--space-4);
          font-size: 0.875rem;
          color: var(--color-text-tertiary);
        }

        .processing-progress {
          margin-bottom: var(--space-6);
        }

        .progress {
          height: 8px;
          margin-bottom: var(--space-2);
        }

        .progress-labels {
          display: flex;
          justify-content: space-between;
          font-size: 0.75rem;
          color: var(--color-text-tertiary);
        }

        .processing-models {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--space-4);
          margin-bottom: var(--space-6);
          padding: var(--space-4);
          background: var(--color-surface);
          border-radius: var(--radius-xl);
        }

        .model-info {
          display: flex;
          flex-direction: column;
          gap: var(--space-1);
        }

        .model-label {
          font-size: 0.75rem;
          font-weight: 500;
          color: var(--color-text-tertiary);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .model-name {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--color-brand-primary);
          font-family: var(--font-mono);
        }

        .processing-stages {
          display: flex;
          flex-direction: column;
          gap: var(--space-3);
        }

        .stage-item {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          padding: var(--space-3);
          border-radius: var(--radius-lg);
          transition: var(--transition-all);
          opacity: 0.5;
        }

        .stage-item.completed {
          opacity: 1;
          background: rgba(5, 150, 105, 0.05);
        }

        .stage-item.active {
          opacity: 1;
          background: rgba(59, 130, 246, 0.05);
          border: 1px solid var(--color-brand-primary);
        }

        .stage-icon {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          font-weight: 600;
          background: var(--color-surface-hover);
          color: var(--color-text-tertiary);
        }

        .stage-item.completed .stage-icon {
          background: var(--color-brand-success);
          color: white;
        }

        .stage-item.active .stage-icon {
          background: var(--color-brand-primary);
          color: white;
          animation: ${typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'none' : 'pulse 2s infinite'};
        }

        .stage-details {
          flex: 1;
        }

        .stage-name {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text-primary);
          margin-bottom: var(--space-1);
        }

        .stage-agent {
          font-size: 0.75rem;
          color: var(--color-text-tertiary);
          font-family: var(--font-mono);
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ProcessingStatus;