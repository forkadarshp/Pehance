import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import ChatInterface from "./ChatInterface";
import { ThemeProvider } from "./contexts/ThemeContext";
import ThemeToggle from "./components/ThemeToggle";
import ProcessingStatus from "./components/ProcessingStatus";
import ModelStatusBoard from "./components/ModelStatusBoard";
import ImageUpload from "./components/ImageUpload";
import EnhancedOutputDisplay from "./components/EnhancedOutputDisplay";
import ModelSelector from "./components/ModelSelector";
import CostBar from "./components/CostBar";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AppContent = () => {
  // Load last prompt from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('pehance:lastPrompt');
    if (saved) setPrompt(saved);
  }, []);

  // Persist prompt changes
  useEffect(() => {
    localStorage.setItem('pehance:lastPrompt', prompt);
  }, [prompt]);

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
  const [modelSummary, setModelSummary] = useState(null);
  const [showChatInterface, setShowChatInterface] = useState(false);
  const [showModelBoard, setShowModelBoard] = useState(false);
  const [currentModel, setCurrentModel] = useState("");
  const [processingTime, setProcessingTime] = useState(0);
  const [modelPreference, setModelPreference] = useState("balanced");
  
  // Multi-modal state
  const [inputMode, setInputMode] = useState("text"); // "text", "image", "both"
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imageAnalysis, setImageAnalysis] = useState(null);
  const [isProcessingImage, setIsProcessingImage] = useState(false);
  const [outputFormat, setOutputFormat] = useState("auto_detect");
  const [formattedOutput, setFormattedOutput] = useState(null);
  
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
  const [currentSection, setCurrentSection] = useState(0);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const checkModelStatus = async () => {
      try {
        const response = await axios.get(`${API}/test-models`);
        setModelStatus(response.data.models);
        setModelSummary(response.data.summary || null);
      } catch (err) {
        // fail silently, UI remains functional
      }
    };
    checkModelStatus();
  }, []);

  // Bidirectional scroll detection and animations
  useEffect(() => {
    let ticking = false;
    
    const updateScrollDirection = () => {
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      if (Math.abs(scrollY - lastScrollY) < 10) {
        ticking = false;
        return;
      }
      
      setScrollDirection(scrollY > lastScrollY ? 'down' : 'up');
      setLastScrollY(scrollY);
      
      if (scrollY < windowHeight * 0.5) {
        setCurrentSection(0); // Hero section
      } else {
        setCurrentSection(1); // Main content section
      }
      
      const scrollableHeight = documentHeight - windowHeight;
      const progress = Math.min((scrollY / scrollableHeight) * 100, 100);
      setScrollProgress(progress);
      
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

  // Initialize elements to hidden state on page load
  useEffect(() => {
    if (heroRef.current) {
      heroRef.current.classList.remove('animate-fade-in-up', 'animate-fade-out-down');
    }
    if (inputSectionRef.current) {
      const inputColumn = inputSectionRef.current.querySelector('.input-column');
      const outputColumn = inputSectionRef.current.querySelector('.output-column');
      
      if (inputColumn) {
        inputColumn.classList.remove('animate-slide-in-left', 'animate-slide-out-left');
      }
      if (outputColumn) {
        outputColumn.classList.remove('animate-slide-in-right', 'animate-slide-out-right');
      }
    }
  }, []);

  const typewriterEffect = (text, onDone) => {
    const words = text.split(' ');
    let index = 0;
    setTypingAnimation('');

    const interval = setInterval(() => {
      if (index < words.length) {
        setTypingAnimation(prev => (prev + (prev ? ' ' : '') + words[index]));
        index++;
      } else {
        clearInterval(interval);
        onDone && onDone();
      }
    }, 10);
  };

  const handleFormatChange = async (newFormat) => {
    setOutputFormat(newFormat);
    if (!enhancedPrompt) return;
    try {
      const { data } = await axios.post(`${API}/format-response`, {
        content: enhancedPrompt,
        target_format: newFormat,
        enhance_quality: true
      });
      setFormattedOutput({
        content: data.formatted_content,
        format: data.detected_format,
        metadata: data.metadata,
        codeBlocks: data.code_blocks
      });
    } catch (e) {
      // no-op
    }
  };

  const handleImageUpload = async (image) => {
    setIsProcessingImage(true);
    setUploadedImage(image);
    try {
      const { data } = await axios.post(`${API}/process-image`, {
        image_data: image.base64,
        analysis_type: "comprehensive"
      });
      setImageAnalysis({
        description: data.description,
        extractedText: data.extracted_text,
        suggestions: data.suggestions
      });
    } catch (e) {
      setImageAnalysis(null);
    } finally {
      setIsProcessingImage(false);
    }
  };

  const handleEnhance = async () => {
    if (!prompt.trim() && (!uploadedImage || !uploadedImage.base64)) return;

    setIsLoading(true);
    setError("");
    setEnhancedPrompt("");
    setTypingAnimation("");
    setEnhancementMetrics(null);

    const startTime = Date.now();

    const models = [
      'llama-3.1-8b-instant',
      'meta-llama/llama-4-scout-17b-16e-instruct', 
      'llama-3.3-70b-versatile', 
      'qwen/qwen3-32b',
      'meta-llama/llama-guard-4-12b'
    ];

    const stages = [
      { name: 'Intent Analysis', duration: 1800, icon: '🎯' },
      { name: 'Context Research', duration: 1600, icon: '🔍' },
      { name: 'Best Practices', duration: 1400, icon: '⚙️' },
      { name: 'Enhancement', duration: 1600, icon: '✨' }
    ];

    const advanceStage = () => {
      setCurrentStageIndex((prev) => (prev + 1) % stages.length);
      setProcessingStage(stages[(currentStageIndex + 1) % stages.length].name);
      const nextModel = models[(currentStageIndex + 1) % models.length];
      setCurrentModel(nextModel);
      setTimeout(advanceStage, stages[(currentStageIndex + 1) % stages.length].duration);
    };

    setProcessingStage(stages[0].name);
    setCurrentModel(models[0]);
    setTimeout(advanceStage, stages[0].duration);

    try {
      const endpoint = uploadedImage ? '/enhance-multimodal' : '/enhance';
      const requestData = {
        prompt: prompt || "",
        mode: mode,
        preferred_format: outputFormat
      };
      if (uploadedImage) {
        requestData.image_data = uploadedImage.base64;
      }

      const response = await axios.post(`${API}${endpoint}`, requestData);
      const endTime = Date.now();
      const totalProcessingTime = ((endTime - startTime) / 1000).toFixed(1);
      setProcessingTime(totalProcessingTime);

      setProcessingStage("Enhancement complete");

      // Build metrics
      const enhancedContent = response.data.enhanced_prompt || "";
      const intent = response.data.agent_results?.intent_analysis || null;
      const modelsUsed = response.data.agent_results?.models_used || response.data.agent_results?.model_used || null;

      const metrics = {
        originalLength: prompt.length,
        enhancedLength: enhancedContent.length,
        improvementRatio: response.data.enhancement_ratio || (enhancedContent.length / (prompt.length || 1)).toFixed(1),
        processingTime: totalProcessingTime,
        confidenceScore: intent?.confidence || 0.85,
        agentSteps: response.data.agent_results?.process_steps?.length || 4,
        enhancementType: response.data.enhancement_type || 'standard_enhancement',
        complexityScore: response.data.complexity_score || intent?.input_complexity_score || 0.5,
        mode: response.data.mode || mode,
        modelsUsed: modelsUsed,
        multimodal: !!uploadedImage,
        imageAnalysis: response.data.agent_results?.image_analysis || null,
      };

      setEnhancementMetrics(metrics);

      const isFormatted = response.data.agent_results?.format_metadata?.formatted;

      if (isFormatted) {
        setFormattedOutput({
          content: enhancedContent,
          format: response.data.agent_results.format_metadata.format_type,
          metadata: response.data.agent_results.format_metadata.format_metadata || {},
          codeBlocks: response.data.agent_results.format_metadata.code_blocks || []
        });
      }

      setTimeout(() => {
        typewriterEffect(enhancedContent, () => {
          setEnhancedPrompt(enhancedContent);
          setIntentAnalysis(intent || {
            intent_category: 'creative',
            confidence: 0.85,
            specific_domain: 'Content Creation',
            complexity_level: 'intermediate'
          });
          setProcessingStage("");
          setCurrentStageIndex(0);
          setCurrentModel("");
        });
      }, 800);

    } catch (err) {
      console.error("Enhancement error:", err);
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
    setUploadedImage(null);
    setImageAnalysis(null);
    setIsProcessingImage(false);
    setFormattedOutput(null);
    setOutputFormat("auto_detect");
    setInputMode("text");
  };

  if (showChatInterface) {
    return <ChatInterface onBack={() => setShowChatInterface(false)} />;
  }

  return (
    <div className="app-container moving-background">
      {/* Scroll Progress Bar */}
      <div 
        className="scroll-progress" 
        style={{ width: `${scrollProgress}%` }}
      ></div>
      
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
            <div className="hero-badge animate-float">
              <span className="badge-icon">✨</span>
              <span>Advanced Multi-Agent Intelligence</span>
            </div>
            
            <h1 className="hero-title display-2xl">
              One Single Prompt
              <br />
              <span className="title-accent">Is All It Takes</span>
            </h1>
            
            <div className="hero-subtitle animate-fade-in-up delay-200">
              <p className="text-xl">
                Our core philosophy: Transform any idea into a precision-crafted prompt with just one input. 
                Professional-grade enhancement powered by sophisticated AI multi-agent intelligence.
              </p>
              
              <div className="self-made-badge animate-fade-in-up delay-300">
                <span className="badge-sparkle">✨</span>
                <span className="badge-text">This website was created using Pehance itself</span>
                <span className="badge-icon">🚀</span>
              </div>
              
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

      {/* Scroll Indicator */}
      <div className="scroll-indicator">
        <div 
          className={`scroll-dot ${currentSection === 0 ? 'active' : ''}`}
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          title="Hero Section"
        ></div>
        <div 
          className={`scroll-dot ${currentSection === 1 ? 'active' : ''}`}
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
              <div className="input-card card enhanced-card">
                {/* Mode Toggle */}
                <div className="mode-selector enhanced-mode-selector">
                  <div className="mode-info">
                    <div className="mode-header">
                      <h3 className="heading-md">Enhancement Mode</h3>
                      <div className="mode-badge">
                        {mode === "single" ? "Single Turn" : "Multi Turn"}
                      </div>
                    </div>
                    <p className="text-sm mode-description">
                      {mode === "single" 
                        ? "Direct comprehensive enhancement - One prompt, maximum impact" 
                        : "Interactive conversational refinement - Collaborate with AI"}
                    </p>
                  </div>
                  
                  <div className="mode-toggle-group enhanced-toggle">
                    <span className={`mode-label ${mode === "single" ? "active" : ""}`}>
                      <span className="mode-icon">⚡</span>
                      Single
                    </span>
                    <button 
                      onClick={() => setMode(mode === "single" ? "multi" : "single")}
                      className="mode-toggle hover-lift"
                    >
                      <div className="toggle-thumb"></div>
                    </button>
                    <span className={`mode-label ${mode === "multi" ? "active" : ""}`}>
                      <span className="mode-icon">💬</span>
                      Multi
                    </span>
                  </div>
                </div>

                {/* Model Preference Selector */}
                <ModelSelector value={modelPreference} onChange={setModelPreference} className="animate-fade-in-up" />
                
                {/* Multi-modal Input Mode Toggle */}
                <div className="input-mode-toggle">
                  <span className="input-mode-label">Input Mode:</span>
                  <div className="input-mode-options">
                    <button
                      className={`input-mode-option ${inputMode === "text" ? "active" : ""}`}
                      onClick={() => setInputMode("text")}
                    >
                      <span className="input-mode-icon">📝</span>
                      Text Only
                    </button>
                    <button
                      className={`input-mode-option ${inputMode === "image" ? "active" : ""}`}
                      onClick={() => setInputMode("image")}
                    >
                      <span className="input-mode-icon">🖼️</span>
                      Image Only
                    </button>
                    <button
                      className={`input-mode-option ${inputMode === "both" ? "active" : ""}`}
                      onClick={() => setInputMode("both")}
                    >
                      <span className="input-mode-icon">🎯</span>
                      Text + Image
                    </button>
                  </div>
                </div>
                
                {/* Text Input Section */}
                {(inputMode === "text" || inputMode === "both") && (
                <div className="input-section enhanced-input-section">
                  <div className="input-header enhanced-input-header">
                    <div className="input-title-group">
                      <h3 className="heading-md">Your Prompt</h3>
                      <div className="input-subtitle">Transform your idea into precision-crafted output</div>
                    </div>
                    <div className="input-stats enhanced-stats">
                      <div className="stat-item">
                        <span className="stat-value">{prompt.length}</span>
                        <span className="stat-label">chars</span>
                      </div>
                      <div className="stat-divider"></div>
                      <div className="stat-item">
                        <span className="stat-value">{prompt.split(' ').filter(w => w.length > 0).length}</span>
                        <span className="stat-label">words</span>
                      </div>
                      {prompt.length > 0 && (
                        <>
                          <div className="stat-divider"></div>
                          <div className="stat-ready animate-scale-in">
                            <span className="ready-icon">✓</span>
                            Ready
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="textarea-container surface enhanced-textarea">
                    <textarea
                      value={prompt}
                      onChange={(e) => {
                        setPrompt(e.target.value);
                        const target = e.target;
                        if (target) {
                          target.style.height = 'auto';
                          target.style.height = Math.min(Math.max(140, target.scrollHeight), 320) + 'px';
                        }
                      }}
                      placeholder={`Enter your idea, question, or concept here...\n\n✨ Perfect examples to try:\n• Write a compelling story about artificial intelligence and human creativity\n• Help me build a scalable React application with modern best practices\n• Create a comprehensive marketing strategy for a SaaS startup\n• Develop a research methodology for studying climate change impact\n• Design a user onboarding flow for a mobile app`}
                      className="input textarea text-mono enhanced-textarea-input"
                      style={{ minHeight: '140px', maxHeight: '320px' }}
                    />
                    <div className="textarea-overlay">
                      <div className="character-limit">
                        <span className={prompt.length > 1800 ? 'limit-warning' : ''}>
                          {prompt.length}/2000
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Enhanced Action Buttons */}
                  <div className="action-buttons enhanced-actions">
                    <button
                      onClick={handleEnhance}
                      disabled={isLoading || !prompt.trim()}
                      className="btn btn-primary enhanced-primary press-scale light-trail"
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
                          <span className="btn-shortcut">⏎</span>
                        </>
                      )}
                    </button>
                    
                    <button
                      onClick={handleClear}
                      className="btn btn-secondary enhanced-secondary hover-lift press-scale"
                    >
                      <span className="btn-icon">🗑️</span>
                      <span>Clear</span>
                    </button>
                  </div>
                </div>
                )}

                {/* Image Input Section */}
                {(inputMode === "image" || inputMode === "both") && (
                  <ImageUpload
                    onImageUpload={handleImageUpload}
                    isProcessing={isProcessingImage}
                    className="multimodal-image-upload"
                  />
                )}

                {/* Image Analysis Display */}
                {imageAnalysis && (
                  <div className="image-analysis-card card animate-fade-in-up">
                    <div className="analysis-header">
                      <h3 className="heading-md">Image Analysis</h3>
                      <div className="analysis-badge">
                        <span className="badge-icon">🔍</span>
                        <span>AI Analyzed</span>
                      </div>
                    </div>
                    
                    <div className="analysis-content">
                      <div className="analysis-description">
                        <h4>Visual Analysis:</h4>
                        <p>{imageAnalysis.description}</p>
                      </div>
                      
                      {imageAnalysis.extractedText && (
                        <div className="extracted-text">
                          <h4>Extracted Text:</h4>
                          <pre className="text-content">{imageAnalysis.extractedText}</pre>
                        </div>
                      )}
                      
                      {imageAnalysis.suggestions && imageAnalysis.suggestions.length > 0 && (
                        <div className="suggestions">
                          <h4>Enhancement Suggestions:</h4>
                          <ul className="suggestion-list">
                            {imageAnalysis.suggestions.map((suggestion, index) => (
                              <li key={index} className="suggestion-item">
                                <span className="suggestion-icon">💡</span>
                                {suggestion}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

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
                            {typeof enhancementMetrics.modelsUsed === 'object' ? (
                              Object.entries(enhancementMetrics.modelsUsed).map(([step, model]) => 
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
                              )
                            ) : (
                              <div className="model-item card-elevated">
                                <div className="model-step">enhancement</div>
                                <div className="model-name">{enhancementMetrics.modelsUsed}</div>
                              </div>
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
              {/* Cost/Token Bar */}
              <CostBar 
                prompt={prompt}
                enhanced={enhancedPrompt || typingAnimation}
                processingTime={processingTime}
                modelsUsed={enhancementMetrics?.modelsUsed || null}
                preference={modelPreference}
                modelStatus={modelStatus}
                modelSummary={modelSummary}
              />

              {enhancedPrompt || typingAnimation ? (
                formattedOutput ? (
                  <EnhancedOutputDisplay
                    content={formattedOutput.content}
                    format={formattedOutput.format}
                    metadata={formattedOutput.metadata}
                    codeBlocks={formattedOutput.codeBlocks}
                    isLoading={isLoading}
                    onFormatChange={handleFormatChange}
                  />
                ) : (
                  <div className="output-card card enhanced-output-card">
                    <div className="output-header enhanced-output-header">
                      <div className="output-title-group">
                        <h3 className="heading-md">Enhanced Prompt</h3>
                        <div className="enhancement-badge">
                          {enhancementMetrics && (
                            <span className="enhancement-ratio">
                              {enhancementMetrics.improvementRatio}x Enhanced
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="output-actions enhanced-output-actions">
                        <div className="output-stats enhanced-output-stats">
                          <div className="stat-group">
                            <span className="output-stat">
                              <span className="stat-icon">📝</span>
                              {(enhancedPrompt.length || typingAnimation.length)} chars
                            </span>
                            <span className="output-stat">
                              <span className="stat-icon">📄</span>
                              {(enhancedPrompt || typingAnimation).split(' ').filter(w => w.length > 0).length} words
                            </span>
                          </div>
                        </div>
                        
                        <div className="format-selector">
                          <select
                            value={outputFormat}
                            onChange={(e) => handleFormatChange(e.target.value)}
                            className="format-select"
                            disabled={isLoading}
                          >
                            <option value="auto_detect">🎯 Auto Detect</option>
                            <option value="rich_text">📝 Rich Text</option>
                            <option value="code_blocks">💻 Code Blocks</option>
                            <option value="markdown">📄 Markdown</option>
                            <option value="plain_text">📋 Plain Text</option>
                          </select>
                        </div>
                        
                        <button
                          onClick={handleCopy}
                          className="btn btn-ghost enhanced-copy-btn hover-lift press-scale"
                          disabled={!enhancedPrompt}
                        >
                          {copySuccess ? (
                            <>
                              <span className="btn-icon success">✅</span>
                              <span>Copied!</span>
                            </>
                          ) : (
                            <>
                              <span className="btn-icon">📋</span>
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                    
                    <div className="output-content surface enhanced-output-content">
                      <div 
                        ref={enhancedTextRef}
                        className="output-text text-mono enhanced-output-text"
                      >
                        {typingAnimation || enhancedPrompt}
                        {typingAnimation && !enhancedPrompt && (
                          <span className="typing-cursor animate-pulse">|</span>
                        )}
                      </div>
                      
                      {enhancedPrompt && enhancementMetrics && (
                        <div className="quality-indicators">
                          <div className="quality-item">
                            <span className="quality-label">Enhancement Quality</span>
                            <div className="quality-bar">
                              <div 
                                className="quality-fill" 
                                style={{ width: `${Math.min(enhancementMetrics.improvementRatio * 10, 100)}%` }}
                              ></div>
                            </div>
                          </div>
                          <div className="quality-item">
                            <span className="quality-label">Processing Time</span>
                            <span className="quality-value">{enhancementMetrics.processingTime}s</span>
                          </div>
                          {enhancementMetrics.multimodal && (
                            <div className="quality-item">
                              <span className="quality-icon">🎯</span>
                              <span className="quality-label">Multi-modal Enhanced</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )
              ) : (
                <div className="placeholder-card card enhanced-placeholder">
                  <div className="placeholder-content">
                    <div className="placeholder-animation">
                      <div className="placeholder-icon">✨</div>
                      <div className="placeholder-particles">
                        <span className="particle">⚡</span>
                        <span className="particle">🎯</span>
                        <span className="particle">🚀</span>
                      </div>
                    </div>
                    <h3 className="placeholder-title">Enhanced Prompt Will Appear Here</h3>
                    <p className="placeholder-text">
                      Enter your prompt and click "Enhance Prompt" to witness the transformation. 
                      Our AI agents will analyze, research, and craft a precision-enhanced version.
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
                      <div className="feature-item">
                        <span className="feature-icon">✨</span>
                        <span>Professional Enhancement</span>
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