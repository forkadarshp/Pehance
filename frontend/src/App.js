import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import ChatInterface from "./ChatInterface";
import { ThemeProvider } from "./contexts/ThemeContext";
import ThemeToggle from "./components/ThemeToggle";
import ProcessingStatus from "./components/ProcessingStatus";
import ModelStatusBoard from "./components/ModelStatusBoard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AppContent = () => {
  const [prompt, setPrompt] = useState("");
  const [enhancedPrompt, setEnhancedPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [intentAnalysis, setIntentAnalysis] = useState(null);
  const [processingStage, setProcessingStage] = useState("");
  const [copySuccess, setCopySuccess] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [typingAnimation, setTypingAnimation] = useState("");
  const [enhancementMetrics, setEnhancementMetrics] = useState(null);
  const [mode, setMode] = useState("single");
  const [modelStatus, setModelStatus] = useState(null);
  const [showChatInterface, setShowChatInterface] = useState(false);
  const [showModelBoard, setShowModelBoard] = useState(false);
  const [currentModel, setCurrentModel] = useState("");
  const [processingTime, setProcessingTime] = useState(0);
  
  // Enhanced processing stages with detailed agent information
  const stages = [
    { 
      name: "Intent Analysis", 
      agent: "Classification Agent", 
      description: "Analyzing prompt intent and complexity",
      icon: "🎯",
      duration: 2000 
    },
    { 
      name: "Context Research", 
      agent: "Context Agent", 
      description: "Gathering domain-specific insights",
      icon: "🔍",
      duration: 2200 
    },
    { 
      name: "Best Practices", 
      agent: "Methodology Agent", 
      description: "Applying optimization frameworks",
      icon: "⚙️",
      duration: 1800 
    },
    { 
      name: "Enhancement", 
      agent: "Enhancement Agent", 
      description: "Crafting precision-enhanced output",
      icon: "✨",
      duration: 2400 
    }
  ];
  
  const enhancedTextRef = useRef(null);
  const heroRef = useRef(null);
  const inputSectionRef = useRef(null);
  const processingIntervalRef = useRef(null);
  
  // Scroll tracking for bidirectional animations
  const [lastScrollY, setLastScrollY] = useState(0);
  const [scrollDirection, setScrollDirection] = useState('down');

  // Bidirectional scroll detection and animations
  useEffect(() => {
    let ticking = false;
    
    const updateScrollDirection = () => {
      const scrollY = window.scrollY;
      
      if (Math.abs(scrollY - lastScrollY) < 10) {
        ticking = false;
        return;
      }
      
      setScrollDirection(scrollY > lastScrollY ? 'down' : 'up');
      setLastScrollY(scrollY);
      ticking = false;
    };

    const requestTick = () => {
      if (!ticking) {
        requestAnimationFrame(updateScrollDirection);
        ticking = true;
      }
    };

    const handleScroll = () => requestTick();

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  // Enhanced intersection observer for bidirectional animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const element = entry.target;
          const isHeroSection = element === heroRef.current;
          const isInputSection = element === inputSectionRef.current;
          
          // Remove all animation classes first
          element.classList.remove(
            'animate-fade-in-up', 'animate-fade-out-down',
            'animate-slide-in-left', 'animate-slide-out-left',
            'animate-slide-in-right', 'animate-slide-out-right'
          );
          
          if (entry.isIntersecting) {
            // Element is entering viewport
            if (scrollDirection === 'down') {
              // Scrolling down - elements appear
              if (isHeroSection) {
                element.classList.add('animate-fade-in-up');
              } else if (isInputSection) {
                // Add staggered animations to input section children
                const inputColumn = element.querySelector('.input-column');
                const outputColumn = element.querySelector('.output-column');
                
                if (inputColumn) {
                  inputColumn.classList.remove('animate-slide-out-left');
                  inputColumn.classList.add('animate-slide-in-left');
                }
                if (outputColumn) {
                  outputColumn.classList.remove('animate-slide-out-right');
                  setTimeout(() => {
                    outputColumn.classList.add('animate-slide-in-right');
                  }, 200);
                }
              }
            } else {
              // Scrolling up - elements appear (reverse entry)
              if (isHeroSection) {
                element.classList.add('animate-fade-in-up');
              } else if (isInputSection) {
                const inputColumn = element.querySelector('.input-column');
                const outputColumn = element.querySelector('.output-column');
                
                if (inputColumn) {
                  inputColumn.classList.remove('animate-slide-out-left');
                  inputColumn.classList.add('animate-slide-in-left');
                }
                if (outputColumn) {
                  outputColumn.classList.remove('animate-slide-out-right');
                  setTimeout(() => {
                    outputColumn.classList.add('animate-slide-in-right');
                  }, 200);
                }
              }
            }
          } else {
            // Element is leaving viewport
            if (scrollDirection === 'up') {
              // Scrolling up - elements disappear
              if (isInputSection) {
                const inputColumn = element.querySelector('.input-column');
                const outputColumn = element.querySelector('.output-column');
                
                if (outputColumn) {
                  outputColumn.classList.remove('animate-slide-in-right');
                  outputColumn.classList.add('animate-slide-out-right');
                }
                if (inputColumn) {
                  setTimeout(() => {
                    inputColumn.classList.remove('animate-slide-in-left');
                    inputColumn.classList.add('animate-slide-out-left');
                  }, 100);
                }
              } else if (isHeroSection) {
                element.classList.remove('animate-fade-in-up');
                element.classList.add('animate-fade-out-down');
              }
            }
          }
        });
      },
      { 
        threshold: [0.1, 0.25, 0.5, 0.75], 
        rootMargin: '0px 0px -20px 0px' 
      }
    );

    if (heroRef.current) observer.observe(heroRef.current);
    if (inputSectionRef.current) observer.observe(inputSectionRef.current);

    return () => observer.disconnect();
  }, [scrollDirection]);

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
    const interval = setInterval(checkModelStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Handle mode changes
  useEffect(() => {
    if (mode === "multi") {
      setShowChatInterface(true);
    } else {
      setShowChatInterface(false);
    }
  }, [mode]);

  // Auto-resize textarea
  const adjustTextareaHeight = (element) => {
    const minHeight = 120;
    const maxHeight = 300;
    
    element.style.height = 'auto';
    const newHeight = Math.min(Math.max(element.scrollHeight, minHeight), maxHeight);
    element.style.height = newHeight + 'px';
  };

  // Typewriter effect
  const typewriterEffect = (text, callback) => {
    let index = 0;
    const speed = 10;
    setTypingAnimation("");
    
    const type = () => {
      if (index < text.length) {
        setTypingAnimation((prev) => prev + text.charAt(index));
        index++;
        setTimeout(type, speed);
      } else {
        callback && callback();
      }
    };
    
    type();
  };

  const handleEnhance = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt to enhance");
      setTimeout(() => setError(""), 4000);
      return;
    }

    setIsLoading(true);
    setError("");
    setEnhancedPrompt("");
    setTypingAnimation("");
    setIntentAnalysis(null);
    setCopySuccess(false);
    setCurrentStageIndex(0);
    setEnhancementMetrics(null);
    setCurrentModel("");
    setProcessingTime(0);

    // Start processing timer
    const startTime = Date.now();
    processingIntervalRef.current = setInterval(() => {
      setProcessingTime(((Date.now() - startTime) / 1000).toFixed(1));
    }, 100);

    // Enhanced processing stages simulation
    let currentStage = 0;
    
    const advanceStage = () => {
      if (currentStage < stages.length - 1) {
        currentStage++;
        setCurrentStageIndex(currentStage);
        setProcessingStage(stages[currentStage].description);
        
        // Simulate model switching
        const models = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'moonshotai/kimi-k2-instruct'];
        setCurrentModel(models[currentStage % models.length]);
        
        setTimeout(advanceStage, stages[currentStage].duration);
      }
    };

    setProcessingStage(stages[0].description);
    setCurrentModel('llama-3.1-8b-instant');
    setTimeout(advanceStage, stages[0].duration);

    try {
      const response = await axios.post(`${API}/enhance`, { 
        prompt,
        mode: mode
      });
      
      clearInterval(processingIntervalRef.current);
      const endTime = Date.now();
      const totalProcessingTime = ((endTime - startTime) / 1000).toFixed(1);
      setProcessingTime(totalProcessingTime);
      
      setProcessingStage("Enhancement complete");
      
      const metrics = {
        originalLength: prompt.length,
        enhancedLength: response.data.enhanced_prompt.length,
        improvementRatio: response.data.enhancement_ratio || (response.data.enhanced_prompt.length / prompt.length).toFixed(1),
        processingTime: totalProcessingTime,
        confidenceScore: response.data.agent_results?.intent_analysis?.confidence || 0.85,
        agentSteps: response.data.agent_results?.process_steps?.length || 4,
        enhancementType: response.data.enhancement_type || 'standard_enhancement',
        complexityScore: response.data.complexity_score || response.data.agent_results?.complexity_score || 0.5,
        mode: response.data.mode || mode,
        modelsUsed: response.data.agent_results?.models_used || {
          classification: 'llama-3.1-8b-instant',
          context: 'llama-3.3-70b-versatile', 
          methodology: 'moonshotai/kimi-k2-instruct',
          enhancement: 'llama-3.3-70b-versatile'
        }
      };
      
      setEnhancementMetrics(metrics);
      
      setTimeout(() => {
        typewriterEffect(response.data.enhanced_prompt, () => {
          setEnhancedPrompt(response.data.enhanced_prompt);
          setIntentAnalysis(response.data.agent_results?.intent_analysis || {
            intent_category: 'creative',
            confidence: 0.85,
            specific_domain: 'Content Creation',
            complexity_level: 'intermediate'
          });
          setProcessingStage("");
          setCurrentStageIndex(0);
          setCurrentModel("");
        });
      }, 1000);
      
    } catch (err) {
      console.error("Enhancement error:", err);
      clearInterval(processingIntervalRef.current);
      const errorMessage = err.response?.data?.detail || 
        "Enhancement failed. Please try again in a moment.";
      setError(errorMessage);
      setProcessingStage("");
      setCurrentStageIndex(0);
      setCurrentModel("");
      setProcessingTime(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(enhancedPrompt);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 3000);
    } catch (err) {
      const textArea = document.createElement('textarea');
      textArea.value = enhancedPrompt;
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

  const handleClear = () => {
    setPrompt("");
    setEnhancedPrompt("");
    setTypingAnimation("");
    setError("");
    setIntentAnalysis(null);
    setProcessingStage("");
    setCopySuccess(false);
    setCurrentStageIndex(0);
    setEnhancementMetrics(null);
    setCurrentModel("");
    setProcessingTime(0);
    if (processingIntervalRef.current) {
      clearInterval(processingIntervalRef.current);
    }
  };

  if (showChatInterface) {
    return <ChatInterface onBack={() => setShowChatInterface(false)} />;
  }

  return (
    <div className="app-container moving-background">
      {/* Professional Header */}
      <header className="app-header">
        <div className="header-background"></div>
        <nav className="container">
          <div className="nav-content">
            <div className="brand-section">
              <div className="brand-logo animate-glow">
                <div className="logo-icon">P</div>
                <div className="status-indicator"></div>
              </div>
              <div className="brand-info">
                <h1 className="brand-title">Pehance</h1>
                <p className="brand-subtitle">AI-Powered Prompt Engineering</p>
              </div>
            </div>
            
            <div className="nav-actions">
              <ThemeToggle className="hover-lift" />
              
              <button
                onClick={() => setShowModelBoard(!showModelBoard)}
                className="btn btn-ghost hover-lift"
                title="View AI Model Status"
              >
                <span>🤖</span>
                AI Status
              </button>
              
              <div className="system-status">
                <div className="status-dot animate-pulse"></div>
                <span>System Active</span>
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

      {/* Model Status Board */}
      {showModelBoard && (
        <div className="model-board-overlay">
          <div className="container">
            <ModelStatusBoard 
              modelStatus={modelStatus} 
              className="animate-scale-in" 
            />
          </div>
        </div>
      )}

      {/* Hero Section */}
      <section ref={heroRef} className="hero-section light-trail">
        <div className="container">
          <div className="hero-content">
            {/* Floating Badge */}
            <div className="hero-badge animate-float">
              <span className="badge-icon">✨</span>
              <span>Advanced Multi-Agent Intelligence</span>
            </div>
            
            {/* Main Headline */}
            <h1 className="hero-title display-2xl">
              Just One Prompt!
            </h1>
            
            {/* Subtitle */}
            <div className="hero-subtitle animate-fade-in-up delay-200">
              <p className="text-xl">
                Transform your ideas into precision-crafted prompts using our sophisticated AI multi-agent system. 
                Professional-grade enhancement with real-time processing insights.
              </p>
              
              {/* Process Steps */}
              <div className="process-steps">
                {stages.map((step, index) => (
                  <div 
                    key={index}
                    className={`process-step animate-fade-in-up delay-${300 + (index * 100)}`}
                  >
                    <span className="step-icon">{step.icon}</span>
                    <span className="step-name">{step.name}</span>
                  </div>
                ))}
              </div>
              
              {/* Scroll hint */}
              <div className="scroll-hint animate-fade-in-up delay-600">
                <p className="text-sm">
                  <span className="scroll-arrow">↓</span>
                  Scroll down to start enhancing your prompts
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Scroll Progress Indicator */}
      <div className="scroll-indicator">
        <div 
          className={`scroll-dot ${window.scrollY < window.innerHeight * 0.5 ? 'active' : ''}`}
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          title="Hero Section"
        ></div>
        <div 
          className={`scroll-dot ${window.scrollY >= window.innerHeight * 0.5 ? 'active' : ''}`}
          onClick={() => window.scrollTo({ top: window.innerHeight, behavior: 'smooth' })}
          title="Prompt Enhancement"
        ></div>
      </div>

      {/* Main Content */}
      <section ref={inputSectionRef} className="main-content">
        <div className="container">
          <div className="content-grid grid-asymmetric">
            
            {/* Input Column */}
            <div className="input-column animate-slide-in-left">
              <div className="input-card card">
                {/* Mode Toggle */}
                <div className="mode-selector">
                  <div className="mode-info">
                    <h3 className="heading-md">Enhancement Mode</h3>
                    <p className="text-sm">
                      {mode === "single" 
                        ? "Single Turn: Direct comprehensive enhancement" 
                        : "Multi Turn: Interactive conversational refinement"}
                    </p>
                  </div>
                  
                  <div className="mode-toggle-group">
                    <span className={`mode-label ${mode === "single" ? "active" : ""}`}>
                      Single
                    </span>
                    <button 
                      onClick={() => setMode(mode === "single" ? "multi" : "single")}
                      className="mode-toggle hover-lift"
                    >
                      <div className="toggle-thumb"></div>
                    </button>
                    <span className={`mode-label ${mode === "multi" ? "active" : ""}`}>
                      Multi
                    </span>
                  </div>
                </div>
                
                {/* Input Section */}
                <div className="input-section">
                  <div className="input-header">
                    <h3 className="heading-md">Your Prompt</h3>
                    <div className="input-stats">
                      <div className="stat-item">
                        <span className="stat-value">{prompt.length}</span>
                        <span className="stat-label">characters</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-value">{prompt.split(' ').filter(w => w.length > 0).length}</span>
                        <span className="stat-label">words</span>
                      </div>
                      {prompt.length > 0 && (
                        <div className="stat-ready animate-scale-in">
                          Ready ✓
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="textarea-container surface">
                    <textarea
                      value={prompt}
                      onChange={(e) => {
                        setPrompt(e.target.value);
                        adjustTextareaHeight(e.target);
                      }}
                      placeholder="Enter your prompt here...

✨ Examples to try:
• Write a compelling story about artificial intelligence and human creativity
• Help me build a scalable React application with modern best practices  
• Create a comprehensive marketing strategy for a SaaS startup
• Develop a research methodology for studying climate change impact"
                      className="input textarea text-mono"
                      style={{ minHeight: '120px', maxHeight: '300px' }}
                    />
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="action-buttons">
                    <button
                      onClick={handleEnhance}
                      disabled={isLoading || !prompt.trim()}
                      className="btn btn-primary press-scale light-trail"
                    >
                      {isLoading ? (
                        <>
                          <div className="btn-spinner"></div>
                          <span>Enhancing...</span>
                        </>
                      ) : (
                        <>
                          <span className="btn-icon">✨</span>
                          <span>Enhance Prompt</span>
                        </>
                      )}
                    </button>
                    
                    <button
                      onClick={handleClear}
                      className="btn btn-secondary hover-lift press-scale"
                    >
                      <span className="btn-icon">🗑️</span>
                      <span>Clear</span>
                    </button>
                  </div>
                </div>

                {/* Processing Status */}
                <ProcessingStatus
                  stage={processingStage}
                  stageIndex={currentStageIndex}
                  stages={stages}
                  isActive={isLoading}
                  currentModel={currentModel}
                  processingTime={processingTime}
                />

                {/* Error Display */}
                {error && (
                  <div className="error-display animate-scale-in">
                    <div className="error-content">
                      <span className="error-icon">⚠️</span>
                      <div className="error-text">
                        <div className="error-title">{error}</div>
                        <div className="error-subtitle">Please check your connection and try again</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Analysis Results */}
              {intentAnalysis && (
                <div className="analysis-card card animate-fade-in-up">
                  <div className="analysis-header">
                    <h3 className="heading-md">Analysis Results</h3>
                    <div className="verification-badge">
                      <span>Verified ✓</span>
                    </div>
                  </div>
                  
                  <div className="analysis-grid">
                    <div className="analysis-item">
                      <div className="analysis-label">Intent Category</div>
                      <div className="category-badge">
                        {intentAnalysis.intent_category}
                      </div>
                    </div>
                    
                    <div className="analysis-item">
                      <div className="analysis-label">Confidence Score</div>
                      <div className="confidence-display">
                        <div className="confidence-bar">
                          <div 
                            className="confidence-fill"
                            style={{ width: `${intentAnalysis.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="confidence-value">
                          {Math.round(intentAnalysis.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="analysis-item">
                      <div className="analysis-label">Domain Expertise</div>
                      <div className="domain-badge">
                        {intentAnalysis.specific_domain || 'General'}
                      </div>
                    </div>
                    
                    <div className="analysis-item">
                      <div className="analysis-label">Complexity Level</div>
                      <div className="complexity-display">
                        <span className="complexity-icon">
                          {intentAnalysis.complexity_level === 'advanced' ? '🚀' : 
                           intentAnalysis.complexity_level === 'intermediate' ? '🎯' : '⚡'}
                        </span>
                        <span className="complexity-text">
                          {intentAnalysis.complexity_level || 'Basic'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Enhancement Metrics */}
                  {enhancementMetrics && (
                    <div className="metrics-section">
                      <div className="metrics-grid">
                        <div className="metric-item card-elevated">
                          <div className="metric-value text-brand">
                            {enhancementMetrics.improvementRatio}x
                          </div>
                          <div className="metric-label">Enhancement Ratio</div>
                        </div>
                        <div className="metric-item card-elevated">
                          <div className="metric-value text-brand">
                            {enhancementMetrics.processingTime}s
                          </div>
                          <div className="metric-label">Processing Time</div>
                        </div>
                        <div className="metric-item card-elevated">
                          <div className="metric-value text-brand">
                            {enhancementMetrics.agentSteps}
                          </div>
                          <div className="metric-label">Agent Steps</div>
                        </div>
                        <div className="metric-item card-elevated">
                          <div className="metric-value text-brand">
                            {enhancementMetrics.mode}
                          </div>
                          <div className="metric-label">Mode Used</div>
                        </div>
                      </div>
                      
                      {/* Models Used */}
                      {enhancementMetrics.modelsUsed && (
                        <div className="models-used">
                          <h4 className="models-title">🤖 AI Models Used</h4>
                          <div className="models-grid">
                            {Object.entries(enhancementMetrics.modelsUsed).map(([step, model]) => 
                              model && (
                                <div key={step} className="model-item card-elevated">
                                  <div className="model-step">
                                    {step.replace('_', ' ')}
                                  </div>
                                  <div className="model-name">
                                    {model}
                                  </div>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Output Column */}
            <div className="output-column animate-slide-in-right delay-200">
              {enhancedPrompt || typingAnimation ? (
                <div className="output-card card">
                  <div className="output-header">
                    <h3 className="heading-md">Enhanced Prompt</h3>
                    <div className="output-actions">
                      <div className="output-stats">
                        <span className="output-stat">
                          {enhancedPrompt.length || typingAnimation.length} chars
                        </span>
                        <span className="output-stat">
                          {(enhancedPrompt || typingAnimation).split(' ').filter(w => w.length > 0).length} words
                        </span>
                      </div>
                      <button
                        onClick={handleCopy}
                        className="btn btn-ghost hover-lift press-scale"
                        disabled={!enhancedPrompt}
                      >
                        {copySuccess ? '✅ Copied!' : '📋 Copy'}
                      </button>
                    </div>
                  </div>
                  
                  <div className="output-content surface">
                    <div 
                      ref={enhancedTextRef}
                      className="output-text text-mono"
                    >
                      {typingAnimation || enhancedPrompt}
                      {typingAnimation && !enhancedPrompt && (
                        <span className="typing-cursor animate-pulse">|</span>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="placeholder-card card">
                  <div className="placeholder-content">
                    <div className="placeholder-icon">✨</div>
                    <h3 className="placeholder-title">Enhanced Prompt Will Appear Here</h3>
                    <p className="placeholder-text">
                      Enter your prompt and click "Enhance Prompt" to see the AI-powered enhancement with real-time processing insights.
                    </p>
                    <div className="placeholder-features">
                      <div className="feature-item">
                        <span className="feature-icon">🎯</span>
                        <span>Intent Analysis</span>
                      </div>
                      <div className="feature-item">
                        <span className="feature-icon">⚡</span>
                        <span>Real-time Processing</span>
                      </div>
                      <div className="feature-item">
                        <span className="feature-icon">🤖</span>
                        <span>Multi-Agent System</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Professional Footer */}
      <footer className="app-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">
                <div className="logo-icon">P</div>
              </div>
              <div className="footer-info">
                <div className="footer-title">Powered by Advanced AI Intelligence</div>
                <div className="footer-subtitle">Next-generation prompt optimization technology</div>
              </div>
            </div>
            
            <div className="footer-badges">
              <div className="footer-badge">
                v2.0.0 • 🚀 Production Ready
              </div>
              <div className="footer-badge">
                ⚡ High Performance • 🔒 Enterprise Grade
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

const App = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};

export default App;