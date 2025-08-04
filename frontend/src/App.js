import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";

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
  const [showTooltip, setShowTooltip] = useState("");
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [typingAnimation, setTypingAnimation] = useState("");
  const [enhancementMetrics, setEnhancementMetrics] = useState(null);
  const [mode, setMode] = useState("single"); // New state for mode toggle
  const [modelStatus, setModelStatus] = useState(null); // New state for model status
  
  const enhancedTextRef = useRef(null);
  const heroRef = useRef(null);
  const inputSectionRef = useRef(null);

  // Intersection observer for elegant staggered animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-elegant-reveal');
            setIsVisible(true);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    if (heroRef.current) observer.observe(heroRef.current);
    if (inputSectionRef.current) observer.observe(inputSectionRef.current);

    return () => observer.disconnect();
  }, []);

  // Professional textarea auto-resize
  const adjustTextareaHeight = (element) => {
    const minHeight = 200;
    const maxHeight = 400;
    
    element.style.height = 'auto';
    const newHeight = Math.min(Math.max(element.scrollHeight, minHeight), maxHeight);
    element.style.height = newHeight + 'px';
  };

  // Refined typewriter effect
  const typewriterEffect = (text, callback) => {
    let index = 0;
    const speed = 20;
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

    // Sophisticated processing stages
    const stages = [
      { text: "Analyzing intent and context", icon: "⚡", duration: 2000 },
      { text: "Gathering domain insights", icon: "🎯", duration: 2200 },
      { text: "Applying best practices", icon: "⚙️", duration: 1800 },
      { text: "Crafting enhanced prompt", icon: "✨", duration: 2400 }
    ];

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
      const response = await axios.post(`${API}/enhance`, { prompt });
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
        complexityScore: response.data.complexity_score || response.data.agent_results.complexity_score || 0.5
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

  const getIntentBadgeColor = (category) => {
    return "accent-bg";
  };

  const getComplexityIcon = (level) => {
    const icons = {
      basic: { icon: "⚡", label: "Basic" },
      intermediate: { icon: "🎯", label: "Intermediate" }, 
      advanced: { icon: "🚀", label: "Advanced" }
    };
    return icons[level] || icons.basic;
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--color-warm-gray-900)',
      color: 'var(--color-warm-gray-200)'
    }}>
      {/* Understated Navigation */}
      <nav style={{
        padding: 'var(--spacing-xl)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        backgroundColor: 'var(--color-warm-gray-800)'
      }}>
        <div className="container-sophisticated" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-lg)'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              backgroundColor: 'var(--color-accent)',
              borderRadius: 'var(--radius-lg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-subtle)'
            }}>
              <span style={{
                color: 'var(--color-soft-white)',
                fontWeight: '800',
                fontSize: '1.5rem'
              }}>P</span>
            </div>
            <div>
              <h1 className="typography-heading-large" style={{
                color: 'var(--color-soft-white)',
                fontWeight: '800'
              }}>
                Pehance
              </h1>
              <p className="typography-caption" style={{
                color: 'var(--color-warm-gray-500)',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '0.1em'
              }}>
                Precision Prompt Engineering
              </p>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-lg)'
          }}>
            <div className="status-indicator status-success">
              <span style={{
                width: '8px',
                height: '8px',
                backgroundColor: 'var(--color-success)',
                borderRadius: '50%',
                display: 'inline-block'
              }}></span>
              System Active
            </div>
          </div>
        </div>
      </nav>

      {/* Sophisticated Hero Section */}
      <section ref={heroRef} style={{
        padding: 'var(--spacing-3xl) 0',
        textAlign: 'center'
      }}>
        <div className="container-sophisticated">
          <div style={{ marginBottom: 'var(--spacing-3xl)' }}>
            {/* Status Badge */}
            <div className="status-indicator status-processing animate-subtle-fade-in" style={{
              display: 'inline-flex',
              marginBottom: 'var(--spacing-2xl)'
            }}>
              <span style={{
                width: '8px',
                height: '8px',
                backgroundColor: 'var(--color-accent)',
                borderRadius: '50%',
                display: 'inline-block'
              }}></span>
              AI-Powered Enhancement
            </div>
            
            {/* Main Headline - Typography as Hero */}
            <h2 className="typography-display-large animate-gentle-slide-up" style={{
              marginBottom: 'var(--spacing-xl)',
              textAlign: 'balance'
            }}>
              Precision
              <br />
              <span className="accent-text">Prompt Engineering</span>
            </h2>
            
            {/* Refined Subtitle */}
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              <p className="typography-body-large animate-gentle-slide-up animate-stagger-2" style={{
                marginBottom: 'var(--spacing-lg)',
                textAlign: 'balance'
              }}>
                Transform ordinary prompts into precision-crafted instructions that unlock AI's full potential through our advanced multi-agent intelligence system.
              </p>
              
              {/* Process Indicators - Understated */}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'center',
                gap: 'var(--spacing-md)',
                marginTop: 'var(--spacing-xl)'
              }}>
                {[
                  "Intent Analysis",
                  "Context Research", 
                  "Best Practices",
                  "Dynamic Enhancement"
                ].map((step, index) => (
                  <span 
                    key={index}
                    className="status-indicator animate-subtle-fade-in"
                    style={{
                      animationDelay: `${(index + 3) * 100}ms`,
                      backgroundColor: 'var(--color-warm-gray-800)',
                      color: 'var(--color-warm-gray-300)',
                      border: '1px solid var(--color-warm-gray-700)'
                    }}
                  >
                    {step}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Interface */}
      <section ref={inputSectionRef} style={{
        padding: '0 0 var(--spacing-3xl) 0'
      }}>
        <div className="container-sophisticated">
          <div className="grid-sophisticated grid-asymmetric">
            
            {/* Input Section */}
            <div>
              <div className="card-sophisticated animate-gentle-slide-up">
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 'var(--spacing-xl)'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-md)'
                  }}>
                    <h3 className="typography-heading-medium">
                      Original Prompt
                    </h3>
                    <div 
                      className="hover-lift"
                      style={{
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        border: '2px solid var(--color-warm-gray-500)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '12px',
                        fontWeight: '600',
                        color: 'var(--color-warm-gray-500)',
                        cursor: 'help',
                        transition: 'all var(--transition-duration-normal) var(--transition-smooth)'
                      }}
                      onMouseEnter={() => setShowTooltip("input")}
                      onMouseLeave={() => setShowTooltip("")}
                    >
                      ?
                    </div>
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-md)'
                  }}>
                    <span className="typography-caption" style={{
                      backgroundColor: 'var(--color-warm-gray-700)',
                      padding: 'var(--spacing-xs) var(--spacing-sm)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-warm-gray-600)'
                    }}>
                      {prompt.length}/2000
                    </span>
                    {prompt.length > 0 && (
                      <span className="status-indicator status-success animate-subtle-fade-in">
                        Ready
                      </span>
                    )}
                  </div>
                </div>

                {/* Professional Tooltip */}
                {showTooltip === "input" && (
                  <div style={{
                    position: 'absolute',
                    top: '80px',
                    left: '0',
                    zIndex: 30,
                    backgroundColor: 'var(--color-warm-gray-800)',
                    border: '1px solid var(--color-warm-gray-700)',
                    borderRadius: 'var(--radius-lg)',
                    padding: 'var(--spacing-lg)',
                    maxWidth: '320px',
                    boxShadow: 'var(--shadow-elevated)'
                  }}>
                    <div className="typography-body">
                      <div className="typography-heading-medium" style={{ 
                        marginBottom: 'var(--spacing-sm)',
                        color: 'var(--color-soft-white)'
                      }}>
                        💡 Pro Tip
                      </div>
                      Enter any prompt you'd like to enhance. Our AI agents will analyze intent, research context, and optimize it for maximum effectiveness.
                    </div>
                  </div>
                )}
                
                <div style={{ position: 'relative' }}>
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
                    className="input-sophisticated typography-code"
                    style={{ 
                      minHeight: '200px',
                      maxHeight: '400px',
                      resize: 'none',
                      overflow: 'hidden'
                    }}
                  />
                  <div style={{
                    position: 'absolute',
                    bottom: 'var(--spacing-md)',
                    right: 'var(--spacing-md)',
                    display: 'flex',
                    gap: 'var(--spacing-md)'
                  }}>
                    <span className="typography-caption" style={{
                      backgroundColor: 'var(--color-warm-gray-800)',
                      padding: 'var(--spacing-xs)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-warm-gray-700)'
                    }}>
                      {prompt.split('\n').length} lines
                    </span>
                    <span className="typography-caption" style={{
                      backgroundColor: 'var(--color-warm-gray-800)',
                      padding: 'var(--spacing-xs)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--color-warm-gray-700)'
                    }}>
                      {prompt.split(' ').filter(word => word.length > 0).length} words
                    </span>
                  </div>
                </div>
                
                <div style={{
                  display: 'flex',
                  gap: 'var(--spacing-lg)',
                  marginTop: 'var(--spacing-xl)'
                }}>
                  <button
                    onClick={handleEnhance}
                    disabled={isLoading || !prompt.trim()}
                    className="button-primary press-feedback"
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 'var(--spacing-md)',
                      padding: 'var(--spacing-lg) var(--spacing-xl)'
                    }}
                  >
                    {isLoading ? (
                      <>
                        <div style={{
                          width: '20px',
                          height: '20px',
                          border: '2px solid rgba(255, 255, 255, 0.3)',
                          borderTop: '2px solid var(--color-soft-white)',
                          borderRadius: '50%',
                          animation: 'spin 1s linear infinite'
                        }}></div>
                        <span>Enhancing...</span>
                      </>
                    ) : (
                      <>
                        <span style={{ fontSize: '1.2rem' }}>✨</span>
                        <span>Enhance Prompt</span>
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleClear}
                    className="button-secondary hover-lift press-feedback"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--spacing-sm)',
                      padding: 'var(--spacing-lg) var(--spacing-xl)'
                    }}
                  >
                    <span>🗑️</span>
                    <span>Clear</span>
                  </button>
                </div>

                {/* Professional Processing Stage */}
                {processingStage && (
                  <div style={{
                    marginTop: 'var(--spacing-xl)',
                    padding: 'var(--spacing-xl)',
                    backgroundColor: 'rgba(217, 119, 6, 0.1)',
                    border: '2px solid rgba(217, 119, 6, 0.2)',
                    borderRadius: 'var(--radius-lg)',
                    boxShadow: 'var(--shadow-subtle)'
                  }} className="animate-subtle-fade-in">
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--spacing-lg)'
                    }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        border: '3px solid var(--color-accent)',
                        borderTop: '3px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></div>
                      <div style={{ flex: 1 }}>
                        <div className="typography-heading-medium accent-text" style={{ marginBottom: 'var(--spacing-sm)' }}>
                          {processingStage}
                        </div>
                        <div className="progress-sophisticated" style={{ height: '4px', marginBottom: 'var(--spacing-sm)' }}>
                          <div 
                            className="progress-bar"
                            style={{ width: `${((currentStageIndex + 1) / 4) * 100}%` }}
                          ></div>
                        </div>
                        <div className="typography-caption">
                          Step {currentStageIndex + 1} of 4
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {error && (
                  <div style={{
                    marginTop: 'var(--spacing-xl)',
                    padding: 'var(--spacing-xl)',
                    backgroundColor: 'rgba(220, 38, 38, 0.1)',
                    border: '2px solid rgba(220, 38, 38, 0.2)',
                    borderRadius: 'var(--radius-lg)',
                    boxShadow: 'var(--shadow-subtle)'
                  }} className="animate-subtle-fade-in">
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--spacing-lg)'
                    }}>
                      <span style={{ fontSize: '1.5rem' }}>⚠️</span>
                      <div>
                        <div className="typography-heading-medium" style={{ color: 'var(--color-error)', marginBottom: 'var(--spacing-xs)' }}>
                          {error}
                        </div>
                        <div className="typography-body" style={{ color: 'var(--color-error)' }}>
                          Please check your connection and try again
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Intent Analysis Card */}
              {intentAnalysis && (
                <div className="card-sophisticated animate-gentle-slide-up" style={{ marginTop: 'var(--spacing-xl)' }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--spacing-xl)'
                  }}>
                    <h4 className="typography-heading-medium">
                      Analysis Results
                    </h4>
                    <span className="status-indicator status-success">
                      Verified ✓
                    </span>
                  </div>
                  
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: 'var(--spacing-xl)'
                  }}>
                    <div>
                      <div className="typography-caption" style={{ 
                        marginBottom: 'var(--spacing-sm)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Intent Category
                      </div>
                      <div className="accent-bg hover-lift" style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        padding: 'var(--spacing-md) var(--spacing-lg)',
                        borderRadius: 'var(--radius-lg)',
                        color: 'var(--color-soft-white)',
                        fontWeight: '600',
                        fontSize: '1.125rem',
                        textTransform: 'capitalize',
                        boxShadow: 'var(--shadow-subtle)'
                      }}>
                        {intentAnalysis.intent_category}
                      </div>
                    </div>
                    
                    <div>
                      <div className="typography-caption" style={{ 
                        marginBottom: 'var(--spacing-sm)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Confidence Score
                      </div>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--spacing-md)'
                      }}>
                        <div className="progress-sophisticated" style={{ 
                          flex: 1,
                          height: '12px'
                        }}>
                          <div 
                            className="progress-bar"
                            style={{ width: `${intentAnalysis.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="accent-text" style={{
                          fontWeight: '600',
                          fontSize: '1.125rem',
                          minWidth: '3rem'
                        }}>
                          {Math.round(intentAnalysis.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div>
                      <div className="typography-caption" style={{ 
                        marginBottom: 'var(--spacing-sm)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Domain Expertise
                      </div>
                      <div style={{
                        color: 'var(--color-warm-gray-200)',
                        fontWeight: '600',
                        fontSize: '1.125rem',
                        textTransform: 'capitalize',
                        backgroundColor: 'var(--color-warm-gray-700)',
                        padding: 'var(--spacing-sm) var(--spacing-md)',
                        borderRadius: 'var(--radius-lg)',
                        border: '1px solid var(--color-warm-gray-600)'
                      }}>
                        {intentAnalysis.specific_domain || 'General'}
                      </div>
                    </div>
                    
                    <div>
                      <div className="typography-caption" style={{ 
                        marginBottom: 'var(--spacing-sm)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em'
                      }}>
                        Complexity Level
                      </div>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--spacing-sm)',
                        fontWeight: '600',
                        fontSize: '1.125rem',
                        textTransform: 'capitalize',
                        color: 'var(--color-warm-gray-200)'
                      }}>
                        <span style={{ fontSize: '1.5rem' }}>
                          {getComplexityIcon(intentAnalysis.complexity_level).icon}
                        </span>
                        <span>
                          {getComplexityIcon(intentAnalysis.complexity_level).label}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Enhancement Metrics */}
                  {enhancementMetrics && (
                    <div style={{
                      marginTop: 'var(--spacing-xl)',
                      paddingTop: 'var(--spacing-xl)',
                      borderTop: '1px solid var(--color-warm-gray-700)'
                    }}>
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                        gap: 'var(--spacing-lg)',
                        textAlign: 'center'
                      }}>
                        <div className="surface-raised" style={{ padding: 'var(--spacing-lg)' }}>
                          <div className="accent-text" style={{ 
                            fontSize: '1.5rem',
                            fontWeight: '600',
                            marginBottom: 'var(--spacing-xs)'
                          }}>
                            {enhancementMetrics.improvementRatio}x
                          </div>
                          <div className="typography-caption">Enhancement Ratio</div>
                        </div>
                        <div className="surface-raised" style={{ padding: 'var(--spacing-lg)' }}>
                          <div className="accent-text" style={{ 
                            fontSize: '1.5rem',
                            fontWeight: '600',
                            marginBottom: 'var(--spacing-xs)'
                          }}>
                            {enhancementMetrics.processingTime}s
                          </div>
                          <div className="typography-caption">Processing Time</div>
                        </div>
                        <div className="surface-raised" style={{ padding: 'var(--spacing-lg)' }}>
                          <div className="accent-text" style={{ 
                            fontSize: '1.5rem',
                            fontWeight: '600',
                            marginBottom: 'var(--spacing-xs)'
                          }}>
                            {enhancementMetrics.agentSteps}
                          </div>
                          <div className="typography-caption">Agent Steps</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Output Section */}
            <div>
              {enhancedPrompt ? (
                <div className="card-sophisticated animate-gentle-slide-up animate-stagger-2">
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--spacing-xl)'
                  }}>
                    <h3 className="typography-heading-medium">
                      Enhanced Prompt
                    </h3>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--spacing-md)'
                    }}>
                      <span className="typography-caption" style={{
                        backgroundColor: 'var(--color-warm-gray-700)',
                        padding: 'var(--spacing-xs) var(--spacing-sm)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-warm-gray-600)'
                      }}>
                        {enhancedPrompt.length} chars
                      </span>
                      <span className="status-indicator status-success">
                        ✓ Enhanced
                      </span>
                    </div>
                  </div>
                  
                  <div className="surface-inset" style={{
                    padding: 'var(--spacing-xl)',
                    maxHeight: '400px',
                    overflowY: 'auto'
                  }}>
                    <pre 
                      ref={enhancedTextRef}
                      className="typography-code"
                      style={{
                        whiteSpace: 'pre-wrap',
                        color: 'var(--color-warm-gray-200)'
                      }}
                    >
                      {typingAnimation || enhancedPrompt}
                    </pre>
                    {typingAnimation && (
                      <span style={{
                        display: 'inline-block',
                        width: '2px',
                        height: '20px',
                        backgroundColor: 'var(--color-accent)',
                        marginLeft: '2px',
                        animation: 'subtlePulse 1s infinite'
                      }}></span>
                    )}
                  </div>
                  
                  <div style={{ marginTop: 'var(--spacing-xl)' }}>
                    <button
                      onClick={handleCopy}
                      className={`hover-lift press-feedback ${copySuccess ? 'button-primary' : 'button-primary'}`}
                      style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 'var(--spacing-md)',
                        padding: 'var(--spacing-lg)',
                        backgroundColor: copySuccess ? 'var(--color-success)' : undefined
                      }}
                    >
                      <div style={{
                        width: '20px',
                        height: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        {copySuccess ? (
                          <span style={{ fontSize: '1.2rem' }}>✓</span>
                        ) : (
                          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '100%', height: '100%' }}>
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>
                      <span style={{ fontWeight: '600' }}>
                        {copySuccess ? 'Copied Successfully!' : 'Copy to Clipboard'}
                      </span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="card-sophisticated">
                  <h3 className="typography-heading-medium" style={{ marginBottom: 'var(--spacing-xl)' }}>
                    Enhanced Prompt
                  </h3>
                  
                  <div className="surface-inset" style={{
                    padding: 'var(--spacing-3xl)',
                    textAlign: 'center'
                  }}>
                    <div style={{
                      width: '120px',
                      height: '120px',
                      margin: '0 auto var(--spacing-xl)',
                      color: 'var(--color-warm-gray-600)'
                    }}>
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ width: '100%', height: '100%' }}>
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <p className="typography-heading-medium" style={{
                      marginBottom: 'var(--spacing-md)',
                      color: 'var(--color-warm-gray-400)'
                    }}>
                      Your enhanced prompt will appear here
                    </p>
                    <p className="typography-body" style={{
                      maxWidth: '400px',
                      margin: '0 auto',
                      color: 'var(--color-warm-gray-600)'
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

      {/* Sophisticated Footer */}
      <footer style={{
        padding: 'var(--spacing-3xl) 0',
        backgroundColor: 'var(--color-warm-gray-800)',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)'
      }}>
        <div className="container-sophisticated">
          <div className="card-sophisticated" style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-2xl)' }}>
              <h4 className="typography-heading-large" style={{
                marginBottom: 'var(--spacing-lg)',
                color: 'var(--color-soft-white)'
              }}>
                Multi-Agent Enhancement Pipeline
              </h4>
              <p className="typography-body-large" style={{
                maxWidth: '600px',
                margin: '0 auto',
                textAlign: 'balance'
              }}>
                Four specialized AI agents work in harmony to create the ultimate prompt enhancement experience through advanced machine learning and natural language processing
              </p>
            </div>
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: 'var(--spacing-xl)'
            }}>
              {[
                { 
                  title: "Intent Classification", 
                  description: "Deep semantic analysis of your prompt's goal, domain expertise, and complexity requirements",
                  icon: "🎯"
                },
                { 
                  title: "Context Research", 
                  description: "Advanced knowledge gathering with domain-specific insights and current best practices",
                  icon: "🔍"
                },
                { 
                  title: "Best Practices", 
                  description: "Universal optimization techniques and enhancement methodologies for maximum effectiveness",
                  icon: "⚡"
                },
                { 
                  title: "Dynamic Enhancement", 
                  description: "Precision-crafted prompt generation with contextual awareness and intelligent optimization",
                  icon: "✨"
                }
              ].map((step, index) => (
                <div 
                  key={index} 
                  className="surface-raised hover-lift animate-subtle-fade-in"
                  style={{
                    padding: 'var(--spacing-xl)',
                    textAlign: 'center',
                    animationDelay: `${index * 100}ms`
                  }}
                >
                  <div style={{
                    fontSize: '2.5rem',
                    marginBottom: 'var(--spacing-lg)'
                  }}>
                    {step.icon}
                  </div>
                  <h5 className="typography-heading-medium" style={{
                    marginBottom: 'var(--spacing-md)',
                    color: 'var(--color-soft-white)'
                  }}>
                    {step.title}
                  </h5>
                  <p className="typography-body" style={{
                    lineHeight: '1.6'
                  }}>
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
            
            <div style={{
              marginTop: 'var(--spacing-2xl)',
              paddingTop: 'var(--spacing-xl)',
              borderTop: '1px solid var(--color-warm-gray-700)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--spacing-lg)',
              textAlign: 'center'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-md)'
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  backgroundColor: 'var(--color-accent)',
                  borderRadius: 'var(--radius-lg)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <span style={{
                    color: 'var(--color-soft-white)',
                    fontWeight: '800',
                    fontSize: '1.125rem'
                  }}>P</span>
                </div>
                <div>
                  <span className="typography-body" style={{ color: 'var(--color-warm-gray-400)' }}>
                    Powered by Advanced AI Intelligence
                  </span>
                  <div className="typography-caption">
                    Next-generation prompt optimization technology
                  </div>
                </div>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-lg)',
                flexWrap: 'wrap',
                justifyContent: 'center'
              }}>
                <div className="typography-caption" style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-xs)'
                }}>
                  <span className="status-indicator" style={{
                    backgroundColor: 'var(--color-warm-gray-700)',
                    border: '1px solid var(--color-warm-gray-600)',
                    fontSize: '0.75rem'
                  }}>v2.0.0</span>
                  <span>•</span>
                  <span>🚀 Production Ready</span>
                </div>
                <div className="typography-caption" style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-xs)'
                }}>
                  <span>⚡ High Performance</span>
                  <span>•</span>
                  <span>🔒 Enterprise Grade</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Add spinning animation keyframe */}
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