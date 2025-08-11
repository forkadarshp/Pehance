import React, { useState, useRef, useEffect } from 'react';

const EnhancedOutputDisplay = ({ 
  content, 
  format = "auto_detect", 
  metadata = {}, 
  codeBlocks = [],
  isLoading = false,
  onFormatChange = null 
}) => {
  const [selectedFormat, setSelectedFormat] = useState(format);
  const [copySuccess, setCopySuccess] = useState(false);
  const [copyingCodeId, setCopyingCodeId] = useState(null);
  const contentRef = useRef(null);

  const [showCodeBlocks, setShowCodeBlocks] = useState(false);

  const buildMarkdown = () => {
    try {
      let plainText = content;
      if (selectedFormat === 'rich_text') {
        const tmp = document.createElement('div');
        tmp.innerHTML = content || '';
        plainText = tmp.textContent || tmp.innerText || '';
      }
      let md = plainText || '';
      if (Array.isArray(codeBlocks) && codeBlocks.length > 0) {
        const codeMd = codeBlocks
          .filter(b => !b.inline)
          .map(b => {
            const lang = (b.language || '').toLowerCase();
            const code = (b.content || b.code || '').trim();
            return `\n\n\
\`\`\`${lang}\n${code}\n\`\`\``;
          })
          .join('');
        md += codeMd;
      }
      return md.trim();
    } catch (e) {
      return content || '';
    }
  };

  const formatOptions = [
    { value: 'auto_detect', label: 'Auto Detect', icon: '🎯' },
    { value: 'rich_text', label: 'Rich Text', icon: '📝' },
    { value: 'code_blocks', label: 'Code Blocks', icon: '💻' },
    { value: 'markdown', label: 'Markdown', icon: '📄' },
    { value: 'plain_text', label: 'Plain Text', icon: '📋' }
  ];

  const handleFormatChange = (newFormat) => {
    setSelectedFormat(newFormat);
    if (onFormatChange) {
      onFormatChange(newFormat);
    }
  };

  const handleCopyAll = async () => {
    try {
      // For rich text, copy the plain text version
      const textToCopy = contentRef.current?.textContent || content;
      await navigator.clipboard.writeText(textToCopy);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 3000);
    } catch (err) {
      console.error('Copy failed:', err);
      // Fallback method
      const textArea = document.createElement('textarea');
      textArea.value = contentRef.current?.textContent || content;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 3000);
    }
  };

  const handleCopyCodeBlock = async (codeId, code) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopyingCodeId(codeId);
      setTimeout(() => setCopyingCodeId(null), 2000);
    } catch (err) {
      console.error('Code copy failed:', err);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Formatting content...</p>
        </div>
      );
    }

    if (format === 'rich_text' || format === 'markdown') {
      // Render HTML content with enhanced styling
      return (
        <div 
          ref={contentRef}
          className="rich-content"
          dangerouslySetInnerHTML={{ __html: content }}
        />
      );
    } else if (format === 'code_blocks' && codeBlocks.length > 0) {
      // Render with enhanced code blocks
      return (
        <div ref={contentRef} className="code-enhanced-content">
          {renderCodeEnhancedContent()}
        </div>
      );
    } else {
      // Plain text with basic formatting
      return (
        <div ref={contentRef} className="plain-content">
          <pre className="formatted-text">{content}</pre>
        </div>
      );
    }
  };

  const renderCodeEnhancedContent = () => {
    // Split content by code blocks and render with copy buttons
    let contentParts = [content];
    let blockIndex = 0;

    codeBlocks.forEach(block => {
      if (!block.inline) {
        const codeBlockPattern = new RegExp(`\`\`\`${block.language}\\n?([\\s\\S]*?)\`\`\``, 'g');
        contentParts = contentParts.flatMap(part => {
          if (typeof part === 'string') {
            return part.split(codeBlockPattern).map((segment, index) => {
              if (index % 2 === 1) {
                // This is code content
                return (
                  <div key={`code-${blockIndex++}`} className="code-block-container">
                    <div className="code-block-header">
                      <span className="language-label">{block.language.toUpperCase()}</span>
                      <button
                        className={`copy-code-btn ${copyingCodeId === block.id ? 'copied' : ''}`}
                        onClick={() => handleCopyCodeBlock(block.id, segment)}
                      >
                        <span className="copy-icon">
                          {copyingCodeId === block.id ? '✅' : '📋'}
                        </span>
                        <span className="copy-text">
                          {copyingCodeId === block.id ? 'Copied!' : 'Copy'}
                        </span>
                      </button>
                    </div>
                    <pre className="code-block">
                      <code className={`language-${block.language}`}>{segment}</code>
                    </pre>
                  </div>
                );
              }
              return segment;
            });
          }
          return part;
        });
      }
    });

    return contentParts.map((part, index) => 
      typeof part === 'string' ? <span key={index}>{part}</span> : part
    );
  };

  const getFormatDisplayName = () => {
    const option = formatOptions.find(opt => opt.value === selectedFormat);
    return option ? `${option.icon} ${option.label}` : 'Auto Detect';
  };

  return (
    <div className="enhanced-output-display">
      {/* Format Control Header */}
      <div className="output-control-header" role="region" aria-live="polite">
        <div className="format-info">
          <h3 className="output-title">Enhanced Output</h3>
          <div className="format-badge">
            <span className="format-indicator">{getFormatDisplayName()}</span>
            {metadata.enhanced && (
              <span className="enhancement-badge">AI Enhanced</span>
            )}
          </div>
        </div>

        <div className="output-actions">
          {/* Quick Actions */}
          <div className="quick-actions">
            <button
              onClick={handleCopyAll}
              className={`copy-all-btn ${copySuccess ? 'copied' : ''}`}
              disabled={isLoading}
              title="Copy all content"
            >
              <span className="copy-icon">
                {copySuccess ? '✅' : '📋'}
              </span>
              <span className="copy-text">
                {copySuccess ? 'Copied!' : 'Copy All'}
              </span>
            </button>

            <button
              onClick={() => {
                const md = buildMarkdown();
                navigator.clipboard.writeText(md);
              }}
              className="copy-md-btn"
              disabled={isLoading}
              title="Copy as Markdown"
            >
              <span className="copy-icon">📝</span>
              <span className="copy-text">Copy as MD</span>
            </button>

            {codeBlocks && codeBlocks.length > 0 && (
              <button
                onClick={() => setShowCodeBlocks(v => !v)}
                className={`toggle-code-btn ${showCodeBlocks ? 'active' : ''}`}
                disabled={isLoading}
                title={showCodeBlocks ? 'Hide code blocks' : 'Expand code blocks'}
              >
                <span className="copy-icon">💻</span>
                <span className="copy-text">{showCodeBlocks ? 'Hide Code' : 'Show Code'}</span>
              </button>
            )}
          </div>

          {/* Format Selector */}
          <div className="format-selector">
            <select
              value={selectedFormat}
              onChange={(e) => handleFormatChange(e.target.value)}
              className="format-select"
              disabled={isLoading}
            >
              {formatOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.icon} {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopyAll}
            className={`copy-all-btn ${copySuccess ? 'copied' : ''}`}
            disabled={isLoading}
          >
            <span className="copy-icon">
              {copySuccess ? '✅' : '📋'}
            </span>
            <span className="copy-text">
              {copySuccess ? 'Copied!' : 'Copy All'}
            </span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="output-content-area">
        {renderContent()}
      </div>

      {/* Metadata Footer */}
      {metadata && Object.keys(metadata).length > 0 && (
        <div className="output-metadata">
          <div className="metadata-stats">
            {metadata.original_length && (
              <div className="stat-item">
                <span className="stat-label">Original:</span>
                <span className="stat-value">{metadata.original_length} chars</span>
              </div>
            )}
            {metadata.formatted_length && (
              <div className="stat-item">
                <span className="stat-label">Formatted:</span>
                <span className="stat-value">{metadata.formatted_length} chars</span>
              </div>
            )}
            {codeBlocks.length > 0 && (
              <div className="stat-item">
                <span className="stat-label">Code Blocks:</span>
                <span className="stat-value">{codeBlocks.length}</span>
              </div>
            )}
            {metadata.languages_detected && metadata.languages_detected.length > 0 && (
              <div className="stat-item">
                <span className="stat-label">Languages:</span>
                <span className="stat-value">
                  {metadata.languages_detected.join(', ')}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedOutputDisplay;