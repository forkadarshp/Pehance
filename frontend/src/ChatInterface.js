import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useTheme } from "./contexts/ThemeContext";
import ThemeToggle from "./components/ThemeToggle";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatInterface = ({ onBack }) => {
  const { theme } = useTheme();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [modelStatus, setModelStatus] = useState(null);
  const [currentModel, setCurrentModel] = useState("");
  const [processingAgent, setProcessingAgent] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check model status
  useEffect(() => {
    const checkModelStatus = async () => {
      try {
        const response = await axios.get(`${API}/test-models`);
        setModelStatus(response.data.models);
      } catch (err) {
        console.warn("Model status check failed:", err);
      }
    };
    
    checkModelStatus();
    const interval = setInterval(checkModelStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Initialize chat with welcome message
  useEffect(() => {
    setMessages([
      {
        id: 1,
        type: 'assistant',
        content: `Welcome to Pehance's Interactive Enhancement Mode! 🎯

I'm your AI prompt engineering assistant, powered by our advanced multi-agent system. Here's how I can help:

**🔍 Intelligent Analysis**
• Analyze your prompts for intent and complexity
• Identify areas for improvement and optimization
• Provide detailed feedback and suggestions

**💬 Interactive Refinement**
• Ask clarifying questions when needed
• Guide you through step-by-step improvements
• Offer multiple enhancement variations

**🤖 Multi-Agent Processing**
• Classification Agent: Intent analysis
• Context Agent: Domain-specific insights  
• Methodology Agent: Best practices application
• Enhancement Agent: Final optimization

**Let's get started!** Share your prompt idea, and I'll help you craft the perfect enhanced version through our conversation.`,
        timestamp: new Date(),
        metadata: {
          type: 'welcome',
          models_used: {
            classification: 'llama-3.1-8b-instant',
            enhancement: 'llama-3.3-70b-versatile'
          }
        }
      }
    ]);
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsTyping(true);
    setProcessingAgent("Classification Agent");
    setCurrentModel("llama-3.1-8b-instant");

    // Simulate processing stages
    const stages = [
      { agent: "Classification Agent", model: "llama-3.1-8b-instant", delay: 1000 },
      { agent: "Context Agent", model: "llama-3.3-70b-versatile", delay: 1500 },
      { agent: "Enhancement Agent", model: "moonshotai/kimi-k2-instruct", delay: 2000 }
    ];

    let stageIndex = 0;
    const advanceStage = () => {
      if (stageIndex < stages.length - 1) {
        stageIndex++;
        const stage = stages[stageIndex];
        setProcessingAgent(stage.agent);
        setCurrentModel(stage.model);
        setTimeout(advanceStage, stage.delay);
      }
    };

    setTimeout(advanceStage, stages[0].delay);

    try {
      const response = await axios.post(`${API}/enhance`, {
        prompt: inputMessage,
        mode: "multi",
        session_id: sessionId,
        conversation_history: messages.slice(1) // Exclude welcome message
      });

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.data.enhanced_prompt,
        timestamp: new Date(),
        metadata: {
          enhancement_type: response.data.enhancement_type,
          intent_analysis: response.data.agent_results?.intent_analysis,
          enhancement_ratio: response.data.enhancement_ratio,
          complexity_score: response.data.complexity_score,
          processing_time: response.data.processing_time || 0,
          models_used: response.data.agent_results?.models_used || {
            classification: 'llama-3.1-8b-instant',
            context: 'llama-3.3-70b-versatile',
            enhancement: 'moonshotai/kimi-k2-instruct'
          }
        }
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Enhancement error:", error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I apologize, but I encountered an error while processing your request: ${error.response?.data?.detail || error.message}

Please try rephrasing your prompt or check your connection.`,
        timestamp: new Date(),
        metadata: {
          type: 'error'
        }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setProcessingAgent("");
      setCurrentModel("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const copyToClipboard = async (content) => {
    try {
      await navigator.clipboard.writeText(content);
      // You might want to add a toast notification here
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="chat-container">
      {/* Enhanced Header */}
      <header className="chat-header">
        <div className="header-background"></div>
        <nav className="container">
          <div className="chat-nav-content">
            <div className="nav-left">
              <button
                onClick={onBack}
                className="btn btn-ghost hover-lift back-button"
              >
                ← Back to Single Mode
              </button>
              
              <div className="chat-brand">
                <div className="brand-logo animate-glow">
                  <div className="logo-icon">P</div>
                  <div className="status-indicator"></div>
                </div>
                <div className="chat-info">
                  <h1 className="chat-title">Pehance Interactive</h1>
                  <p className="chat-subtitle">Multi-Turn Enhancement Mode</p>
                </div>
              </div>
            </div>
            
            <div className="nav-right">
              <ThemeToggle className="hover-lift" />
              
              {/* Processing Status */}
              {isTyping && (
                <div className="processing-indicator animate-scale-in">
                  <div className="processing-spinner"></div>
                  <div className="processing-info">
                    <div className="processing-agent">{processingAgent}</div>
                    <div className="processing-model">{currentModel}</div>
                  </div>
                </div>
              )}
              
              <div className="chat-status">
                <div className="status-dot animate-pulse"></div>
                <span>Multi-Turn Active</span>
              </div>
              
              {modelStatus && (
                <div className="model-summary">
                  <span className="model-count">
                    {Object.values(modelStatus).filter(m => m.available).length}/{Object.keys(modelStatus).length}
                  </span>
                  <span className="model-label">Models</span>
                </div>
              )}
            </div>
          </div>
        </nav>
      </header>

      {/* Chat Messages */}
      <main className="chat-main">
        <div className="chat-messages">
          <div className="container chat-container-content">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-wrapper ${message.type}`}
              >
                <div className="message-container">
                  <div className={`message-bubble ${message.type}`}>
                    {/* Message Content */}
                    <div className="message-content">
                      {message.content}
                    </div>

                    {/* Message Metadata */}
                    {message.metadata && !message.metadata.type && (
                      <div className="message-metadata">
                        <div className="metadata-row">
                          {message.metadata.enhancement_type && (
                            <div className="metadata-tag enhancement-type">
                              {message.metadata.enhancement_type.replace('_', ' ')}
                            </div>
                          )}
                          {message.metadata.enhancement_ratio && (
                            <div className="metadata-tag enhancement-ratio">
                              {message.metadata.enhancement_ratio}x enhanced
                            </div>
                          )}
                          {message.metadata.intent_analysis && (
                            <div className="metadata-tag confidence">
                              {Math.round(message.metadata.intent_analysis.confidence * 100)}% confident
                            </div>
                          )}
                        </div>
                        
                        {/* Models Used */}
                        {message.metadata.models_used && (
                          <div className="models-used-section">
                            <div className="models-label">AI Models Used:</div>
                            <div className="models-list">
                              {Object.entries(message.metadata.models_used).map(([step, model]) => 
                                model && (
                                  <div key={step} className="model-tag">
                                    <span className="model-step">{step}</span>
                                    <span className="model-name">{model}</span>
                                  </div>
                                )
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Copy Button for Assistant Messages */}
                    {message.type === 'assistant' && !message.metadata?.type && (
                      <button
                        onClick={() => copyToClipboard(message.content)}
                        className="copy-button btn btn-ghost"
                        title="Copy to clipboard"
                      >
                        📋
                      </button>
                    )}

                    {/* Timestamp */}
                    <div className="message-timestamp">
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Enhanced Typing Indicator */}
            {isTyping && (
              <div className="message-wrapper assistant">
                <div className="message-container">
                  <div className="typing-indicator">
                    <div className="typing-content">
                      <div className="typing-dots">
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                      </div>
                      <div className="typing-text">
                        <div className="typing-title">Pehance is thinking...</div>
                        {processingAgent && (
                          <div className="typing-details">
                            <span className="typing-agent">{processingAgent}</span>
                            {currentModel && (
                              <span className="typing-model">using {currentModel}</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Enhanced Input Area */}
        <div className="chat-input-area">
          <div className="container chat-container-content">
            <div className="input-wrapper">
              <div className="input-container">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                  className="chat-input"
                  disabled={isTyping}
                  rows={1}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isTyping || !inputMessage.trim()}
                  className="send-button btn btn-primary press-scale light-trail"
                >
                  {isTyping ? (
                    <>
                      <div className="btn-spinner"></div>
                      <span>Sending...</span>
                    </>
                  ) : (
                    <>
                      <span className="send-icon">📤</span>
                      <span>Send</span>
                    </>
                  )}
                </button>
              </div>

              {/* Quick Actions */}
              <div className="quick-actions">
                {[
                  "Help me improve this prompt",
                  "What questions should I ask?", 
                  "Make it more specific",
                  "Add examples",
                  "Start fresh"
                ].map((action, index) => (
                  <button
                    key={index}
                    onClick={() => action === "Start fresh" 
                      ? setMessages(messages.slice(0, 1)) 
                      : setInputMessage(action)}
                    className="quick-action btn btn-ghost"
                    disabled={isTyping}
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      <style jsx>{`
        .chat-container {
          min-height: 100vh;
          background: var(--color-background);
          display: flex;
          flex-direction: column;
        }

        .chat-header {
          position: sticky;
          top: 0;
          z-index: 100;
          background: var(--gradient-glass);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid var(--color-border);
          box-shadow: var(--shadow-sm);
        }

        .chat-nav-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--space-4) 0;
          gap: var(--space-4);
        }

        .nav-left {
          display: flex;
          align-items: center;
          gap: var(--space-4);
        }

        .back-button {
          font-size: 0.875rem;
          padding: var(--space-2) var(--space-4);
        }

        .chat-brand {
          display: flex;
          align-items: center;
          gap: var(--space-3);
        }

        .chat-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--color-text-primary);
          margin: 0;
        }

        .chat-subtitle {
          font-size: 0.875rem;
          color: var(--color-brand-primary);
          margin: 0;
        }

        .nav-right {
          display: flex;
          align-items: center;
          gap: var(--space-4);
        }

        .processing-indicator {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          padding: var(--space-2) var(--space-4);
          background: var(--gradient-glass);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-full);
        }

        .processing-spinner {
          width: 16px;
          height: 16px;
          border: 2px solid var(--color-brand-primary);
          border-top: 2px solid transparent;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        .processing-info {
          display: flex;
          flex-direction: column;
          gap: var(--space-1);
        }

        .processing-agent {
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--color-text-primary);
        }

        .processing-model {
          font-size: 0.7rem;
          color: var(--color-text-tertiary);
          font-family: var(--font-mono);
        }

        .chat-status {
          display: flex;
          align-items: center;
          gap: var(--space-2);
          padding: var(--space-2) var(--space-3);
          background: rgba(245, 158, 11, 0.1);
          color: var(--color-brand-warning);
          border: 1px solid rgba(245, 158, 11, 0.2);
          border-radius: var(--radius-full);
          font-size: 0.875rem;
          font-weight: 500;
        }

        .chat-main {
          flex: 1;
          display: flex;
          flex-direction: column;
          max-height: calc(100vh - 80px);
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: var(--space-8) 0;
        }

        .chat-container-content {
          max-width: 900px;
        }

        .message-wrapper {
          margin-bottom: var(--space-6);
          animation: fadeInUp 0.3s ease-out;
        }

        .message-wrapper.user {
          display: flex;
          justify-content: flex-end;
        }

        .message-wrapper.assistant {
          display: flex;
          justify-content: flex-start;
        }

        .message-container {
          max-width: 70%;
          min-width: 200px;
        }

        .message-bubble {
          position: relative;
          border-radius: var(--radius-2xl);
          box-shadow: var(--shadow-lg);
          transition: var(--transition-all);
        }

        .message-bubble:hover {
          transform: translateY(-1px);
          box-shadow: var(--shadow-xl);
        }

        .message-bubble.user {
          background: var(--gradient-brand);
          color: var(--color-text-inverse);
          padding: var(--space-4) var(--space-6);
        }

        .message-bubble.assistant {
          background: var(--gradient-surface);
          color: var(--color-text-primary);
          border: 1px solid var(--color-border);
          padding: var(--space-6);
        }

        .message-content {
          white-space: pre-wrap;
          line-height: 1.6;
          font-size: 0.95rem;
        }

        .message-bubble.assistant .message-content {
          font-family: var(--font-mono);
        }

        .message-metadata {
          margin-top: var(--space-4);
          padding-top: var(--space-4);
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .metadata-row {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-2);
          margin-bottom: var(--space-3);
        }

        .metadata-tag {
          padding: var(--space-1) var(--space-2);
          border-radius: var(--radius-md);
          font-size: 0.75rem;
          font-weight: 500;
        }

        .enhancement-type {
          background: rgba(139, 92, 246, 0.1);
          color: var(--color-brand-accent);
          border: 1px solid rgba(139, 92, 246, 0.2);
        }

        .enhancement-ratio {
          background: rgba(5, 150, 105, 0.1);
          color: var(--color-brand-success);
          border: 1px solid rgba(5, 150, 105, 0.2);
        }

        .confidence {
          background: rgba(244, 63, 94, 0.1);
          color: var(--color-brand-error);
          border: 1px solid rgba(244, 63, 94, 0.2);
        }

        .models-used-section {
          margin-top: var(--space-3);
        }

        .models-label {
          font-size: 0.75rem;
          color: var(--color-text-tertiary);
          margin-bottom: var(--space-2);
          font-weight: 600;
        }

        .models-list {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-2);
        }

        .model-tag {
          display: flex;
          flex-direction: column;
          gap: var(--space-1);
          padding: var(--space-2) var(--space-3);
          background: var(--color-surface-elevated);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
        }

        .model-step {
          font-size: 0.7rem;
          color: var(--color-text-tertiary);
          text-transform: capitalize;
          font-weight: 500;
        }

        .model-name {
          font-size: 0.7rem;
          color: var(--color-brand-primary);
          font-family: var(--font-mono);
          word-break: break-all;
        }

        .copy-button {
          position: absolute;
          top: var(--space-2);
          right: var(--space-2);
          padding: var(--space-1);
          font-size: 0.75rem;
          opacity: 0.7;
        }

        .message-timestamp {
          margin-top: var(--space-2);
          font-size: 0.75rem;
          opacity: 0.6;
          text-align: right;
        }

        .message-bubble.user .message-timestamp {
          text-align: left;
        }

        .typing-indicator {
          background: var(--gradient-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-2xl);
          padding: var(--space-4) var(--space-6);
          box-shadow: var(--shadow-lg);
        }

        .typing-content {
          display: flex;
          align-items: center;
          gap: var(--space-4);
        }

        .typing-dots {
          display: flex;
          gap: var(--space-1);
        }

        .typing-dot {
          width: 8px;
          height: 8px;
          background: var(--color-brand-primary);
          border-radius: 50%;
          animation: pulse 1.4s ease-in-out infinite;
        }

        .typing-dot:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
          animation-delay: 0.4s;
        }

        .typing-text {
          flex: 1;
        }

        .typing-title {
          font-size: 0.875rem;
          color: var(--color-text-secondary);
          font-weight: 500;
        }

        .typing-details {
          display: flex;
          gap: var(--space-2);
          margin-top: var(--space-1);
          font-size: 0.75rem;
        }

        .typing-agent {
          color: var(--color-brand-primary);
          font-weight: 600;
        }

        .typing-model {
          color: var(--color-text-tertiary);
          font-family: var(--font-mono);
        }

        .chat-input-area {
          border-top: 1px solid var(--color-border);
          background: var(--gradient-surface);
          padding: var(--space-6) 0;
        }

        .input-wrapper {
          display: flex;
          flex-direction: column;
          gap: var(--space-4);
        }

        .input-container {
          display: flex;
          gap: var(--space-4);
          align-items: flex-end;
        }

        .chat-input {
          flex: 1;
          min-height: 48px;
          max-height: 200px;
          resize: none;
          font-size: 1rem;
          line-height: 1.5;
          padding: var(--space-3) var(--space-4);
        }

        .send-button {
          min-height: 48px;
          padding: var(--space-3) var(--space-6);
          display: flex;
          align-items: center;
          gap: var(--space-2);
        }

        .send-icon {
          font-size: 1.1rem;
        }

        .quick-actions {
          display: flex;
          flex-wrap: wrap;
          gap: var(--space-2);
        }

        .quick-action {
          font-size: 0.8rem;
          padding: var(--space-2) var(--space-3);
          opacity: 0.8;
        }

        .quick-action:hover {
          opacity: 1;
        }

        .quick-action:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(16px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .chat-nav-content {
            flex-direction: column;
            gap: var(--space-4);
          }
          
          .nav-left,
          .nav-right {
            flex-wrap: wrap;
            justify-content: center;
          }
          
          .message-container {
            max-width: 85%;
          }
          
          .input-container {
            flex-direction: column;
            gap: var(--space-3);
          }
          
          .send-button {
            width: 100%;
            justify-content: center;
          }
          
          .quick-actions {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;