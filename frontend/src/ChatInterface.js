import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatInterface = ({ onBack }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [modelStatus, setModelStatus] = useState(null);
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
  }, []);

  // Initialize chat with welcome message
  useEffect(() => {
    setMessages([
      {
        id: 1,
        type: 'assistant',
        content: `Welcome to Pehance's conversational prompt enhancement! 

I'm here to help you craft the perfect prompt through an interactive conversation. I can:

• **Ask clarifying questions** when your prompt needs more context
• **Suggest improvements** step by step
• **Provide multiple variations** for you to choose from
• **Explain my reasoning** behind each enhancement

**How it works:**
1. Share your initial prompt or idea
2. I'll analyze it and may ask follow-up questions
3. Together we'll refine it to perfection
4. You'll get a professionally enhanced prompt

What would you like help with today?`,
        timestamp: new Date(),
        metadata: {
          type: 'welcome'
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
          processing_time: response.data.processing_time || 0
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
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: 'var(--color-obsidian)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <header style={{
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        background: 'linear-gradient(180deg, var(--color-charcoal) 0%, var(--color-obsidian) 100%)',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <nav className="container" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--space-6) 0'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
            <button
              onClick={onBack}
              className="btn btn-ghost hover-lift"
              style={{ 
                padding: 'var(--space-2) var(--space-3)',
                fontSize: '1.2rem'
              }}
            >
              ← Back
            </button>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(135deg, var(--color-amber-primary) 0%, var(--color-amber-dark) 100%)',
                borderRadius: 'var(--radius-xl)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative'
              }}>
                <span style={{
                  color: 'var(--color-slate-900)',
                  fontWeight: '800',
                  fontSize: '1.25rem'
                }}>P</span>
                <div style={{
                  position: 'absolute',
                  top: '2px',
                  right: '2px',
                  width: '8px',
                  height: '8px',
                  background: 'var(--color-emerald)',
                  borderRadius: '50%',
                  border: '1px solid var(--color-charcoal)'
                }}></div>
              </div>
              <div>
                <h1 className="heading-md" style={{ color: 'var(--color-pure-white)', marginBottom: '2px' }}>
                  Pehance Chat
                </h1>
                <p className="text-sm" style={{ color: 'var(--color-amber-primary)' }}>
                  Multi-Turn Enhancement
                </p>
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            <div className="status status-processing">
              <div style={{
                width: '6px',
                height: '6px',
                backgroundColor: 'var(--color-amber-primary)',
                borderRadius: '50%'
              }}></div>
              Multi-Turn Mode
            </div>
            
            {modelStatus && (
              <div className="status" style={{
                background: 'rgba(59, 130, 246, 0.1)',
                color: 'var(--color-blue)',
                border: '1px solid rgba(59, 130, 246, 0.2)'
              }}>
                Models: {Object.values(modelStatus).filter(m => m.available).length}/{Object.keys(modelStatus).length}
              </div>
            )}
          </div>
        </nav>
      </header>

      {/* Chat Messages */}
      <main style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        maxHeight: 'calc(100vh - 200px)'
      }}>
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: 'var(--space-8) 0'
        }}>
          <div className="container" style={{ maxWidth: '900px' }}>
            {messages.map((message) => (
              <div
                key={message.id}
                style={{
                  display: 'flex',
                  justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                  marginBottom: 'var(--space-6)',
                  animation: 'fadeInUp 0.3s ease-out'
                }}
              >
                <div style={{
                  maxWidth: '70%',
                  minWidth: '200px'
                }}>
                  <div
                    className="card hover-lift"
                    style={{
                      background: message.type === 'user' 
                        ? 'linear-gradient(135deg, var(--color-amber-primary) 0%, var(--color-amber-dark) 100%)'
                        : 'var(--color-charcoal)',
                      color: message.type === 'user' ? 'var(--color-slate-900)' : 'var(--color-slate-200)',
                      padding: 'var(--space-6)',
                      position: 'relative',
                      border: message.type === 'assistant' ? '1px solid rgba(255, 255, 255, 0.1)' : 'none'
                    }}
                  >
                    {/* Message Content */}
                    <div style={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: '1.6',
                      fontSize: message.type === 'user' ? '1rem' : '0.95rem',
                      fontFamily: message.type === 'assistant' ? 'var(--font-mono)' : 'inherit'
                    }}>
                      {message.content}
                    </div>

                    {/* Message Metadata */}
                    {message.metadata && !message.metadata.type && (
                      <div style={{
                        marginTop: 'var(--space-4)',
                        paddingTop: 'var(--space-4)',
                        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 'var(--space-2)',
                        fontSize: '0.75rem'
                      }}>
                        {message.metadata.enhancement_type && (
                          <div className="status" style={{
                            background: 'rgba(139, 92, 246, 0.1)',
                            color: 'var(--color-violet)',
                            border: '1px solid rgba(139, 92, 246, 0.2)',
                            fontSize: '0.7rem'
                          }}>
                            {message.metadata.enhancement_type}
                          </div>
                        )}
                        {message.metadata.enhancement_ratio && (
                          <div className="status" style={{
                            background: 'rgba(16, 185, 129, 0.1)',
                            color: 'var(--color-emerald)',
                            border: '1px solid rgba(16, 185, 129, 0.2)',
                            fontSize: '0.7rem'
                          }}>
                            {message.metadata.enhancement_ratio}x
                          </div>
                        )}
                        {message.metadata.intent_analysis && (
                          <div className="status" style={{
                            background: 'rgba(244, 63, 94, 0.1)',
                            color: 'var(--color-rose)',
                            border: '1px solid rgba(244, 63, 94, 0.2)',
                            fontSize: '0.7rem'
                          }}>
                            {Math.round(message.metadata.intent_analysis.confidence * 100)}% confident
                          </div>
                        )}
                      </div>
                    )}

                    {/* Copy Button for Assistant Messages */}
                    {message.type === 'assistant' && !message.metadata?.type && (
                      <button
                        onClick={() => copyToClipboard(message.content)}
                        className="btn btn-ghost"
                        style={{
                          position: 'absolute',
                          top: 'var(--space-2)',
                          right: 'var(--space-2)',
                          padding: 'var(--space-1)',
                          fontSize: '0.75rem',
                          opacity: 0.7
                        }}
                        title="Copy to clipboard"
                      >
                        📋
                      </button>
                    )}

                    {/* Timestamp */}
                    <div style={{
                      marginTop: 'var(--space-2)',
                      fontSize: '0.75rem',
                      opacity: 0.6,
                      textAlign: message.type === 'user' ? 'right' : 'left'
                    }}>
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div style={{
                display: 'flex',
                justifyContent: 'flex-start',
                marginBottom: 'var(--space-6)'
              }}>
                <div className="card" style={{
                  background: 'var(--color-charcoal)',
                  padding: 'var(--space-4) var(--space-6)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-3)'
                }}>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      backgroundColor: 'var(--color-amber-primary)',
                      borderRadius: '50%',
                      animation: 'pulse 1.4s ease-in-out infinite'
                    }}></div>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      backgroundColor: 'var(--color-amber-primary)',
                      borderRadius: '50%',
                      animation: 'pulse 1.4s ease-in-out infinite 0.2s'
                    }}></div>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      backgroundColor: 'var(--color-amber-primary)',
                      borderRadius: '50%',
                      animation: 'pulse 1.4s ease-in-out infinite 0.4s'
                    }}></div>
                  </div>
                  <span className="text-sm" style={{ color: 'var(--color-slate-400)' }}>
                    Pehance is thinking...
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div style={{
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          background: 'var(--color-charcoal)',
          padding: 'var(--space-6) 0'
        }}>
          <div className="container" style={{ maxWidth: '900px' }}>
            <div style={{
              display: 'flex',
              gap: 'var(--space-4)',
              alignItems: 'flex-end'
            }}>
              <div style={{ flex: 1 }}>
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                  className="input textarea"
                  style={{
                    minHeight: '60px',
                    maxHeight: '200px',
                    resize: 'none',
                    fontSize: '1rem',
                    lineHeight: '1.5'
                  }}
                  disabled={isTyping}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={isTyping || !inputMessage.trim()}
                className="btn btn-primary press-scale"
                style={{
                  padding: 'var(--space-4) var(--space-6)',
                  minHeight: '60px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)'
                }}
              >
                {isTyping ? (
                  <>
                    <div style={{
                      width: '16px',
                      height: '16px',
                      border: '2px solid rgba(15, 23, 42, 0.3)',
                      borderTop: '2px solid var(--color-slate-900)',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }}></div>
                    Sending...
                  </>
                ) : (
                  <>
                    <span style={{ fontSize: '1.1rem' }}>📤</span>
                    Send
                  </>
                )}
              </button>
            </div>

            {/* Quick Actions */}
            <div style={{
              marginTop: 'var(--space-4)',
              display: 'flex',
              gap: 'var(--space-2)',
              flexWrap: 'wrap'
            }}>
              {[
                "Help me improve this prompt",
                "What questions should I ask?",
                "Make it more specific",
                "Add examples",
                "Clear conversation"
              ].map((action, index) => (
                <button
                  key={index}
                  onClick={() => action === "Clear conversation" 
                    ? setMessages(messages.slice(0, 1)) 
                    : setInputMessage(action)}
                  className="btn btn-ghost"
                  style={{
                    fontSize: '0.8rem',
                    padding: 'var(--space-2) var(--space-3)',
                    opacity: 0.8
                  }}
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>

      <style jsx>{`
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
      `}</style>
    </div>
  );
};

export default ChatInterface;