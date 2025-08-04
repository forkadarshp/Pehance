import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import ChatInterface from "./ChatInterface";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
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
  
  // Processing stages with model information
  const stages = [
    { text: "Analyzing intent and context", icon: "⚡", duration: 2000, model: "Classification Agent" },
    { text: "Gathering domain insights", icon: "🎯", duration: 2200, model: "Context Agent" },
    { text: "Applying best practices", icon: "⚙️", duration: 1800, model: "Methodology Agent" },
    { text: "Crafting enhanced prompt", icon: "✨", duration: 2400, model: "Enhancement Agent" }
  ];
  
  const enhancedTextRef = useRef(null);
  const heroRef = useRef(null);
  const inputSectionRef = useRef(null);

  // Intersection observer for animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-fade-in-up');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    if (heroRef.current) observer.observe(heroRef.current);
    if (inputSectionRef.current) observer.observe(inputSectionRef.current);

    return () => observer.disconnect();
  }, []);

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
    const minHeight = 180;
    const maxHeight = 400;
    
    element.style.height = 'auto';
    const newHeight = Math.min(Math.max(element.scrollHeight, minHeight), maxHeight);
    element.style.height = newHeight + 'px';
  };

  // Typewriter effect
  const typewriterEffect = (text, callback) => {
    let index = 0;
    const speed = 15;
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

    // Processing stages - already defined at component level
    let currentStage = 0;
    
    const advanceStage = () => {
      if (currentStage < stages.length - 1) {
        currentStage++;
        setCurrentStageIndex(currentStage);
        setProcessingStage(stages[currentStage].text);
        setTimeout(advanceStage, stages[currentStage].duration);
      }
    };

    setProcessingStage(stages[0].text);
    setTimeout(advanceStage, stages[0].duration);

    const startTime = Date.now();

    try {
      const response = await axios.post(`${API}/enhance`, { 
        prompt,
        mode: mode
      });
      const endTime = Date.now();
      const processingTime = ((endTime - startTime) / 1000).toFixed(1);
      
      setProcessingStage("Enhancement complete");
      
      const metrics = {
        originalLength: prompt.length,
        enhancedLength: response.data.enhanced_prompt.length,
        improvementRatio: response.data.enhancement_ratio || (response.data.enhanced_prompt.length / prompt.length).toFixed(1),
        processingTime: processingTime,
        confidenceScore: response.data.agent_results.intent_analysis.confidence,
        agentSteps: response.data.agent_results.process_steps?.length || 4,
        enhancementType: response.data.enhancement_type || 'standard_enhancement',
        complexityScore: response.data.complexity_score || response.data.agent_results.complexity_score || 0.5,
        mode: response.data.mode || mode,
        modelsUsed: response.data.agent_results.models_used || null
      };
      
      setEnhancementMetrics(metrics);
      
      setTimeout(() => {
        typewriterEffect(response.data.enhanced_prompt, () => {
          setEnhancedPrompt(response.data.enhanced_prompt);
          setIntentAnalysis(response.data.agent_results.intent_analysis);
          setProcessingStage("");
          setCurrentStageIndex(0);
        });
      }, 1000);
      
    } catch (err) {
      console.error("Enhancement error:", err);
      const errorMessage = err.response?.data?.detail || 
        "Enhancement failed. Please try again in a moment.";
      setError(errorMessage);
      setProcessingStage("");
      setCurrentStageIndex(0);
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
  };

  if (showChatInterface) {
    return <ChatInterface onBack={() => setShowChatInterface(false)} />;
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--color-obsidian)' }}>
      {/* Header */}
      <header style={{
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        background: 'linear-gradient(180deg, var(--color-charcoal) 0%, var(--color-obsidian) 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Background Pattern */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `url("https://images.unsplash.com/photo-1644088379091-d574269d422f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwyfHxuZXVyYWwlMjBuZXR3b3JrfGVufDB8fHx8MTc1NDMzNDU1M3ww&ixlib=rb-4.1.0&q=85")`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 0.03,
          filter: 'blur(1px)'
        }}></div>
        
        <nav className="container" style={{ position: 'relative', zIndex: 2 }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: 'var(--space-8) 0'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
              <div style={{
                width: '56px',
                height: '56px',
                background: 'linear-gradient(135deg, var(--color-amber-primary) 0%, var(--color-amber-dark) 100%)',
                borderRadius: 'var(--radius-2xl)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--shadow-lg)',
                position: 'relative'
              }}>
                <span style={{
                  color: 'var(--color-slate-900)',
                  fontWeight: '800',
                  fontSize: '1.75rem',
                  fontFamily: 'var(--font-display)'
                }}>P</span>
                <div style={{
                  position: 'absolute',
                  top: '2px',
                  right: '2px',
                  width: '12px',
                  height: '12px',
                  background: 'var(--color-emerald)',
                  borderRadius: '50%',
                  border: '2px solid var(--color-charcoal)'
                }}></div>
              </div>
              <div>
                <h1 className="heading-lg" style={{ color: 'var(--color-pure-white)', marginBottom: 'var(--space-1)' }}>
                  Pehance
                </h1>
                <p className="text-sm" style={{
                  color: 'var(--color-amber-primary)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.15em',
                  fontWeight: '600'
                }}>
                  Precision Prompt Engineering
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
              <div className="status status-success animate-pulse">
                <div style={{
                  width: '8px',
                  height: '8px',
                  backgroundColor: 'var(--color-emerald)',
                  borderRadius: '50%'
                }}></div>
                System Active
              </div>
              
              {modelStatus && (
                <div className="status" style={{
                  background: 'rgba(59, 130, 246, 0.1)',
                  color: 'var(--color-blue)',
                  border: '1px solid rgba(59, 130, 246, 0.2)'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: Object.values(modelStatus).some(m => m.available) ? 'var(--color-blue)' : 'var(--color-error)',
                    borderRadius: '50%'
                  }}></div>
                  AI Models: {Object.values(modelStatus).filter(m => m.available).length}/{Object.keys(modelStatus).length}
                </div>
              )}
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section ref={heroRef} style={{ padding: 'var(--space-24) 0 var(--space-20) 0', position: 'relative' }}>
        <div className="container">
          <div style={{
            maxWidth: '900px',
            margin: '0 auto',
            textAlign: 'center',
            position: 'relative'
          }}>
            {/* Floating Badge */}
            <div className="animate-float" style={{
              display: 'inline-flex',
              marginBottom: 'var(--space-8)',
              padding: 'var(--space-3) var(--space-6)',
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%)',
              border: '1px solid rgba(245, 158, 11, 0.2)',
              borderRadius: 'var(--radius-full)',
              color: 'var(--color-amber-primary)',
              fontSize: '0.875rem',
              fontWeight: '600',
              letterSpacing: '0.05em'
            }}>
              <span style={{ marginRight: 'var(--space-2)' }}>✨</span>
              AI-Powered Enhancement Engine
            </div>
            
            {/* Main Headline */}
            <h1 className="display-xl animate-fade-in-up" style={{
              marginBottom: 'var(--space-8)',
              background: 'linear-gradient(135deg, var(--color-pure-white) 0%, var(--color-slate-300) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Precision
              <br />
              <span style={{
                background: 'linear-gradient(135deg, var(--color-amber-primary) 0%, var(--color-amber-light) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>Prompt Engineering</span>
            </h1>
            
            {/* Subtitle */}
            <div className="animate-fade-in-up delay-200" style={{ marginBottom: 'var(--space-12)' }}>
              <p className="text-xl" style={{
                maxWidth: '700px',
                margin: '0 auto var(--space-8)',
                lineHeight: '1.8',
                color: 'var(--color-slate-300)'
              }}>
                Transform ordinary prompts into precision-crafted instructions that unlock AI's full potential through our advanced multi-agent intelligence system.
              </p>
              
              {/* Process Indicators */}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'center',
                gap: 'var(--space-4)'
              }}>
                {[
                  { name: "Intent Analysis", icon: "🎯" },
                  { name: "Context Research", icon: "🔍" }, 
                  { name: "Best Practices", icon: "⚡" },
                  { name: "Dynamic Enhancement", icon: "✨" }
                ].map((step, index) => (
                  <div 
                    key={index}
                    className={`status animate-fade-in-up delay-${300 + (index * 100)}`}
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: 'var(--color-slate-400)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      fontSize: '0.8rem'
                    }}
                  >
                    <span style={{ fontSize: '1rem' }}>{step.icon}</span>
                    {step.name}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section ref={inputSectionRef} style={{ padding: '0 0 var(--space-24) 0' }}>
        <div className="container">
          <div className="grid grid-asymmetric">
            
            {/* Input Column */}
            <div className="animate-slide-in-left">
              <div className="card" style={{ marginBottom: 'var(--space-8)' }}>
                {/* Mode Toggle */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 'var(--space-8)',
                  padding: 'var(--space-6)',
                  background: 'rgba(255, 255, 255, 0.02)',
                  borderRadius: 'var(--radius-xl)',
                  border: '1px solid rgba(255, 255, 255, 0.08)'
                }}>
                  <div>
                    <h3 className="heading-md" style={{ marginBottom: 'var(--space-2)' }}>
                      Enhancement Mode
                    </h3>
                    <p className="text-sm" style={{ color: 'var(--color-slate-400)' }}>
                      {mode === "single" 
                        ? "Single Turn: Direct prompt enhancement" 
                        : "Multi Turn: Conversational enhancement"}
                    </p>
                  </div>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                    <span className={`text-sm ${mode === "single" ? "text-accent" : ""}`} style={{ fontWeight: '600' }}>
                      Single
                    </span>
                    <button 
                      onClick={() => setMode(mode === "single" ? "multi" : "single")}
                      style={{
                        width: '64px',
                        height: '32px',
                        background: mode === "single" ? 'var(--color-amber-primary)' : 'var(--color-slate-600)',
                        borderRadius: 'var(--radius-full)',
                        position: 'relative',
                        border: 'none',
                        cursor: 'pointer',
                        transition: 'var(--transition-all)'
                      }}
                      className="hover-lift"
                    >
                      <div style={{
                        width: '28px',
                        height: '28px',
                        background: 'var(--color-pure-white)',
                        borderRadius: '50%',
                        position: 'absolute',
                        top: '2px',
                        left: mode === "single" ? '2px' : '34px',
                        transition: 'var(--transition-all)',
                        boxShadow: 'var(--shadow-md)'
                      }}></div>
                    </button>
                    <span className={`text-sm ${mode === "multi" ? "text-accent" : ""}`} style={{ fontWeight: '600' }}>
                      Multi
                    </span>
                  </div>
                </div>
                
                {/* Input Header */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 'var(--space-6)'
                }}>
                  <h3 className="heading-md">Original Prompt</h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                    <div className="status" style={{
                      background: 'rgba(100, 116, 139, 0.1)',
                      color: 'var(--color-slate-400)',
                      border: '1px solid rgba(100, 116, 139, 0.2)',
                      fontSize: '0.75rem'
                    }}>
                      {prompt.length}/2000
                    </div>
                    {prompt.length > 0 && (
                      <div className="status status-success animate-scale-in">
                        Ready
                      </div>
                    )}
                  </div>
                </div>

                {/* Textarea */}
                <div className="surface" style={{ position: 'relative', marginBottom: 'var(--space-6)' }}>
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
                    style={{ 
                      minHeight: '180px',
                      maxHeight: '400px',
                      border: 'none',
                      background: 'transparent',
                      resize: 'none',
                      padding: 'var(--space-6)'
                    }}
                  />
                  
                  {/* Input Stats */}
                  <div style={{
                    position: 'absolute',
                    bottom: 'var(--space-4)',
                    right: 'var(--space-4)',
                    display: 'flex',
                    gap: 'var(--space-2)'
                  }}>
                    <div className="status" style={{
                      background: 'rgba(30, 41, 59, 0.8)',
                      border: '1px solid rgba(100, 116, 139, 0.3)',
                      fontSize: '0.75rem'
                    }}>
                      {prompt.split('\n').length} lines
                    </div>
                    <div className="status" style={{
                      background: 'rgba(30, 41, 59, 0.8)',
                      border: '1px solid rgba(100, 116, 139, 0.3)',
                      fontSize: '0.75rem'
                    }}>
                      {prompt.split(' ').filter(word => word.length > 0).length} words
                    </div>
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
                  <button
                    onClick={handleEnhance}
                    disabled={isLoading || !prompt.trim()}
                    className="btn btn-primary press-scale"
                    style={{ flex: 1, gap: 'var(--space-3)' }}
                  >
                    {isLoading ? (
                      <>
                        <div style={{
                          width: '20px',
                          height: '20px',
                          border: '2px solid rgba(15, 23, 42, 0.3)',
                          borderTop: '2px solid var(--color-slate-900)',
                          borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }}></div>
                        Enhancing...
                      </>
                    ) : (
                      <>
                        <span style={{ fontSize: '1.2rem' }}>✨</span>
                        Enhance Prompt
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleClear}
                    className="btn btn-secondary hover-lift press-scale"
                    style={{ gap: 'var(--space-2)' }}
                  >
                    <span>🗑️</span>
                    Clear
                  </button>
                </div>

                {/* Processing Stage */}
                {processingStage && (
                  <div className="animate-scale-in" style={{
                    marginTop: 'var(--space-6)',
                    padding: 'var(--space-6)',
                    background: 'rgba(245, 158, 11, 0.1)',
                    border: '2px solid rgba(245, 158, 11, 0.2)',
                    borderRadius: 'var(--radius-xl)',
                    boxShadow: 'var(--shadow-lg)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        border: '3px solid var(--color-amber-primary)',
                        borderTop: '3px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></div>
                      <div style={{ flex: 1 }}>
                        <div className="heading-md text-accent" style={{ marginBottom: 'var(--space-2)' }}>
                          {processingStage}
                        </div>
                        <div className="progress" style={{ height: '6px', marginBottom: 'var(--space-2)' }}>
                          <div 
                            className="progress-bar"
                            style={{ width: `${((currentStageIndex + 1) / 4) * 100}%` }}
                          ></div>
                        </div>
                        <div className="text-sm" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span>Step {currentStageIndex + 1} of 4</span>
                          <span style={{ 
                            background: 'rgba(245, 158, 11, 0.2)', 
                            padding: '2px 8px', 
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '500'
                          }}>
                            {stages[currentStageIndex]?.model || 'Processing...'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {error && (
                  <div className="animate-scale-in" style={{
                    marginTop: 'var(--space-6)',
                    padding: 'var(--space-6)',
                    background: 'rgba(220, 38, 38, 0.1)',
                    border: '2px solid rgba(220, 38, 38, 0.2)',
                    borderRadius: 'var(--radius-xl)',
                    boxShadow: 'var(--shadow-lg)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                      <span style={{ fontSize: '1.5rem' }}>⚠️</span>
                      <div>
                        <div className="heading-md" style={{ color: 'var(--color-error)', marginBottom: 'var(--space-1)' }}>
                          {error}
                        </div>
                        <div className="text-sm" style={{ color: 'var(--color-error)' }}>
                          Please check your connection and try again
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Intent Analysis */}
              {intentAnalysis && (
                <div className="card animate-fade-in-up">
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--space-8)'
                  }}>
                    <h3 className="heading-md">Analysis Results</h3>
                    <div className="status status-success">
                      Verified ✓
                    </div>
                  </div>
                  
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                    gap: 'var(--space-6)'
                  }}>
                    <div>
                      <div className="text-sm" style={{ 
                        marginBottom: 'var(--space-2)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Intent Category
                      </div>
                      <div className="btn-ghost" style={{
                        background: 'var(--color-amber-primary)',
                        color: 'var(--color-slate-900)',
                        borderRadius: 'var(--radius-xl)',
                        fontWeight: '600',
                        textTransform: 'capitalize',
                        pointerEvents: 'none'
                      }}>
                        {intentAnalysis.intent_category}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm" style={{ 
                        marginBottom: 'var(--space-2)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Confidence Score
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                        <div className="progress" style={{ flex: 1, height: '12px' }}>
                          <div 
                            className="progress-bar"
                            style={{ width: `${intentAnalysis.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-accent" style={{ fontWeight: '600', minWidth: '3rem' }}>
                          {Math.round(intentAnalysis.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm" style={{ 
                        marginBottom: 'var(--space-2)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Domain Expertise
                      </div>
                      <div className="btn-ghost" style={{
                        textTransform: 'capitalize'
                      }}>
                        {intentAnalysis.specific_domain || 'General'}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm" style={{ 
                        marginBottom: 'var(--space-2)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Complexity Level
                      </div>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--space-2)',
                        fontWeight: '600',
                        textTransform: 'capitalize'
                      }}>
                        <span style={{ fontSize: '1.5rem' }}>
                          {intentAnalysis.complexity_level === 'advanced' ? '🚀' : 
                           intentAnalysis.complexity_level === 'intermediate' ? '🎯' : '⚡'}
                        </span>
                        <span>{intentAnalysis.complexity_level || 'Basic'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Enhancement Metrics */}
                  {enhancementMetrics && (
                    <div style={{
                      marginTop: 'var(--space-8)',
                      paddingTop: 'var(--space-8)',
                      borderTop: '1px solid rgba(255, 255, 255, 0.1)'
                    }}>
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                        gap: 'var(--space-4)',
                        textAlign: 'center'
                      }}>
                        <div className="card-elevated" style={{ padding: 'var(--space-4)' }}>
                          <div className="text-accent" style={{ 
                            fontSize: '1.5rem',
                            fontWeight: '600',
                            marginBottom: 'var(--space-1)'
                          }}>
                            {enhancementMetrics.improvementRatio}x
                          </div>
                          <div className="text-sm">Enhancement Ratio</div>
                        </div>
                        <div className="card-elevated" style={{ padding: 'var(--space-4)' }}>
                          <div className="text-accent" style={{ 
                            fontSize: '1.5rem',
                            fontWeight: '600',
                            marginBottom: 'var(--space-1)'
                          }}>
                            {enhancementMetrics.processingTime}s
                          </div>
                          <div className="text-sm">Processing Time</div>
                        </div>
                        <div className="card-elevated" style={{ padding: 'var(--space-4)' }}>
                          <div className="text-accent" style={{ 
                            fontSize: '1.5rem',
                            fontWeight: '600',
                            marginBottom: 'var(--space-1)'
                          }}>
                            {enhancementMetrics.agentSteps}
                          </div>
                          <div className="text-sm">Agent Steps</div>
                        </div>
                        <div className="card-elevated" style={{ padding: 'var(--space-4)' }}>
                          <div className="text-accent" style={{ 
                            fontSize: '1rem',
                            fontWeight: '600',
                            marginBottom: 'var(--space-1)',
                            textTransform: 'capitalize'
                          }}>
                            {enhancementMetrics.mode}
                          </div>
                          <div className="text-sm">Mode Used</div>
                        </div>
                      </div>
                      
                      {/* Models Used Section */}
                      {enhancementMetrics.modelsUsed && (
                        <div style={{ marginTop: 'var(--space-6)' }}>
                          <h4 style={{ 
                            marginBottom: 'var(--space-4)', 
                            color: 'var(--color-slate-300)',
                            fontSize: '1rem',
                            fontWeight: '600'
                          }}>
                            🤖 Models Used
                          </h4>
                          <div style={{ 
                            display: 'grid', 
                            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                            gap: 'var(--space-4)' 
                          }}>
                            {Object.entries(enhancementMetrics.modelsUsed).map(([step, model]) => 
                              model && (
                                <div key={step} className="card-elevated" style={{ padding: 'var(--space-4)' }}>
                                  <div style={{ 
                                    fontSize: '0.875rem',
                                    fontWeight: '600',
                                    marginBottom: 'var(--space-2)',
                                    textTransform: 'capitalize',
                                    color: 'var(--color-slate-300)'
                                  }}>
                                    {step.replace('_', ' ')}
                                  </div>
                                  <div style={{ 
                                    fontSize: '0.75rem',
                                    color: 'var(--color-amber-primary)',
                                    fontFamily: 'Monaco, monospace',
                                    background: 'rgba(245, 158, 11, 0.1)',
                                    padding: '4px 8px',
                                    borderRadius: '4px',
                                    wordBreak: 'break-all'
                                  }}>
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
            <div className="animate-slide-in-right delay-200">
              {enhancedPrompt ? (
                <div className="card">
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--space-6)'
                  }}>
                    <h3 className="heading-md">Enhanced Prompt</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                      <div className="status" style={{
                        background: 'rgba(100, 116, 139, 0.1)',
                        color: 'var(--color-slate-400)',
                        border: '1px solid rgba(100, 116, 139, 0.2)',
                        fontSize: '0.75rem'
                      }}>
                        {enhancedPrompt.length} chars
                      </div>
                      <div className="status status-success">
                        ✓ Enhanced
                      </div>
                    </div>
                  </div>
                  
                  <div className="surface" style={{
                    padding: 'var(--space-6)',
                    maxHeight: '400px',
                    overflowY: 'auto',
                    marginBottom: 'var(--space-6)'
                  }}>
                    <pre 
                      ref={enhancedTextRef}
                      className="text-mono"
                      style={{
                        whiteSpace: 'pre-wrap',
                        color: 'var(--color-slate-200)',
                        fontSize: '0.9rem',
                        lineHeight: '1.7'
                      }}
                    >
                      {typingAnimation || enhancedPrompt}
                    </pre>
                    {typingAnimation && (
                      <span style={{
                        display: 'inline-block',
                        width: '2px',
                        height: '20px',
                        backgroundColor: 'var(--color-amber-primary)',
                        marginLeft: '2px',
                        animation: 'pulse 1s infinite'
                      }}></span>
                    )}
                  </div>
                  
                  <button
                    onClick={handleCopy}
                    className={`btn ${copySuccess ? 'btn-primary' : 'btn-primary'} hover-lift press-scale`}
                    style={{
                      width: '100%',
                      gap: 'var(--space-3)',
                      background: copySuccess ? 'var(--color-emerald)' : undefined
                    }}
                  >
                    <div style={{ width: '20px', height: '20px' }}>
                      {copySuccess ? (
                        <span style={{ fontSize: '1.2rem' }}>✓</span>
                      ) : (
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '100%', height: '100%' }}>
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      )}
                    </div>
                    {copySuccess ? 'Copied Successfully!' : 'Copy to Clipboard'}
                  </button>
                </div>
              ) : (
                <div className="card">
                  <h3 className="heading-md" style={{ marginBottom: 'var(--space-8)' }}>
                    Enhanced Prompt
                  </h3>
                  
                  <div className="surface" style={{
                    padding: 'var(--space-16)',
                    textAlign: 'center'
                  }}>
                    <div style={{
                      width: '120px',
                      height: '120px',
                      margin: '0 auto var(--space-8)',
                      color: 'var(--color-slate-600)'
                    }}>
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '100%', height: '100%' }}>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <p className="heading-md" style={{
                      marginBottom: 'var(--space-4)',
                      color: 'var(--color-slate-400)'
                    }}>
                      Your enhanced prompt will appear here
                    </p>
                    <p className="text-base" style={{
                      maxWidth: '400px',
                      margin: '0 auto',
                      color: 'var(--color-slate-500)'
                    }}>
                      Enter a prompt above and click "Enhance" to experience the power of AI-driven optimization
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: 'var(--space-24) 0',
        background: 'linear-gradient(180deg, var(--color-obsidian) 0%, var(--color-charcoal) 100%)',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <div className="container">
          <div className="card" style={{ 
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <div style={{ textAlign: 'center', marginBottom: 'var(--space-12)' }}>
              <h2 className="heading-xl" style={{
                marginBottom: 'var(--space-6)',
                color: 'var(--color-pure-white)'
              }}>
                Multi-Agent Enhancement Pipeline
              </h2>
              <p className="text-lg" style={{
                maxWidth: '600px',
                margin: '0 auto',
                lineHeight: '1.8'
              }}>
                Four specialized AI agents work in harmony to create the ultimate prompt enhancement experience through advanced machine learning and natural language processing
              </p>
            </div>
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: 'var(--space-8)'
            }}>
              {[
                { 
                  title: "Intent Classification", 
                  description: "Deep semantic analysis of your prompt's goal, domain expertise, and complexity requirements",
                  icon: "🎯",
                  color: "var(--color-rose)"
                },
                { 
                  title: "Context Research", 
                  description: "Advanced knowledge gathering with domain-specific insights and current best practices",
                  icon: "🔍",
                  color: "var(--color-blue)"
                },
                { 
                  title: "Best Practices", 
                  description: "Universal optimization techniques and enhancement methodologies for maximum effectiveness",
                  icon: "⚡",
                  color: "var(--color-violet)"
                },
                { 
                  title: "Dynamic Enhancement", 
                  description: "Precision-crafted prompt generation with contextual awareness and intelligent optimization",
                  icon: "✨",
                  color: "var(--color-emerald)"
                }
              ].map((step, index) => (
                <div 
                  key={index} 
                  className={`card-elevated hover-lift animate-fade-in-up delay-${index * 100}`}
                  style={{ textAlign: 'center' }}
                >
                  <div style={{
                    fontSize: '2.5rem',
                    marginBottom: 'var(--space-6)',
                    filter: `drop-shadow(0 0 20px ${step.color}40)`
                  }}>
                    {step.icon}
                  </div>
                  <h3 className="heading-md" style={{
                    marginBottom: 'var(--space-4)',
                    color: 'var(--color-pure-white)'
                  }}>
                    {step.title}
                  </h3>
                  <p className="text-base" style={{ lineHeight: '1.6' }}>
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
            
            <div style={{
              marginTop: 'var(--space-12)',
              paddingTop: 'var(--space-8)',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 'var(--space-6)',
              textAlign: 'center'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  background: 'linear-gradient(135deg, var(--color-amber-primary) 0%, var(--color-amber-dark) 100%)',
                  borderRadius: 'var(--radius-xl)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <span style={{
                    color: 'var(--color-slate-900)',
                    fontWeight: '800',
                    fontSize: '1.25rem'
                  }}>P</span>
                </div>
                <div>
                  <div className="text-base" style={{ color: 'var(--color-slate-400)' }}>
                    Powered by Advanced AI Intelligence
                  </div>
                  <div className="text-sm">
                    Next-generation prompt optimization technology
                  </div>
                </div>
              </div>
              
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-6)',
                flexWrap: 'wrap',
                justifyContent: 'center'
              }}>
                <div className="status">
                  v2.0.0 • 🚀 Production Ready
                </div>
                <div className="status">
                  ⚡ High Performance • 🔒 Enterprise Grade
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Spinning animation */}
      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default App;