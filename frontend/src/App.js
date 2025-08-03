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
  const enhancedTextRef = useRef(null);

  // Auto-resize textarea with smooth animation
  const adjustTextareaHeight = (element) => {
    element.style.height = 'auto';
    const newHeight = element.scrollHeight;
    element.style.height = newHeight + 'px';
    
    // Add smooth transition
    element.style.transition = 'height 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
  };

  const handleEnhance = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt to enhance");
      setTimeout(() => setError(""), 3000);
      return;
    }

    setIsLoading(true);
    setError("");
    setEnhancedPrompt("");
    setIntentAnalysis(null);
    setCopySuccess(false);
    setCurrentStageIndex(0);

    // Enhanced processing stages with more detail
    const stages = [
      { text: "Analyzing intent and domain expertise...", icon: "🎯", duration: 1800 },
      { text: "Gathering contextual research and insights...", icon: "🔍", duration: 2000 },
      { text: "Applying universal best practices...", icon: "⚡", duration: 1600 },
      { text: "Crafting precision-enhanced prompt...", icon: "✨", duration: 2200 }
    ];

    // Animated stage progression
    const stageInterval = setInterval(() => {
      setCurrentStageIndex(prev => {
        if (prev < stages.length - 1) {
          setProcessingStage(stages[prev + 1].text);
          return prev + 1;
        }
        return prev;
      });
    }, 1800);

    try {
      const response = await axios.post(`${API}/enhance`, { prompt });
      clearInterval(stageInterval);
      setProcessingStage("Enhancement complete! ✨");
      
      // Staggered reveal animation
      setTimeout(() => {
        setEnhancedPrompt(response.data.enhanced_prompt);
        setIntentAnalysis(response.data.agent_results.intent_analysis);
        setProcessingStage("");
        setCurrentStageIndex(0);
      }, 800);
      
    } catch (err) {
      clearInterval(stageInterval);
      console.error("Enhancement error:", err);
      setError(
        err.response?.data?.detail || 
        "Enhancement failed. Please check your connection and try again."
      );
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
      setTimeout(() => setCopySuccess(false), 2500);
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = enhancedPrompt;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2500);
    }
  };

  const handleClear = () => {
    setPrompt("");
    setEnhancedPrompt("");
    setError("");
    setIntentAnalysis(null);
    setProcessingStage("");
    setCopySuccess(false);
    setCurrentStageIndex(0);
  };

  const getIntentColor = (category) => {
    const colors = {
      creative: "from-rose-400 via-pink-500 to-purple-600",
      technical: "from-blue-400 via-cyan-500 to-indigo-600", 
      business: "from-emerald-400 via-green-500 to-teal-600",
      academic: "from-violet-400 via-purple-500 to-indigo-600",
      personal: "from-amber-400 via-orange-500 to-red-600",
      other: "from-slate-400 via-gray-500 to-zinc-600"
    };
    return colors[category] || colors.other;
  };

  const getComplexityIcon = (level) => {
    const icons = {
      basic: { icon: "⚡", color: "text-green-400" },
      intermediate: { icon: "🔥", color: "text-orange-400" }, 
      advanced: { icon: "🚀", color: "text-purple-400" }
    };
    return icons[level] || icons.basic;
  };

  // Enhanced processing stages with icons
  const processingStages = [
    { text: "Analyzing intent and domain expertise...", icon: "🎯", color: "from-purple-500 to-blue-500" },
    { text: "Gathering contextual research and insights...", icon: "🔍", color: "from-blue-500 to-cyan-500" },
    { text: "Applying universal best practices...", icon: "⚡", color: "from-cyan-500 to-emerald-500" },
    { text: "Crafting precision-enhanced prompt...", icon: "✨", color: "from-emerald-500 to-purple-500" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Enhanced animated background with multiple layers */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-purple-600/15 to-blue-600/15 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-to-r from-cyan-600/15 to-emerald-600/15 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-3/4 left-1/2 w-64 h-64 bg-gradient-to-r from-pink-600/15 to-rose-600/15 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
        
        {/* Additional depth layers */}
        <div className="absolute top-1/2 left-1/8 w-48 h-48 bg-gradient-to-r from-indigo-600/10 to-purple-600/10 rounded-full blur-2xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute bottom-1/8 right-1/8 w-56 h-56 bg-gradient-to-r from-teal-600/10 to-cyan-600/10 rounded-full blur-2xl animate-pulse" style={{animationDelay: '3s'}}></div>
      </div>

      {/* Enhanced Navigation Bar with glass morphism */}
      <nav className="relative z-10 p-6 border-b border-slate-800/50 backdrop-blur-xl bg-slate-900/20">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4 group">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/25 group-hover:shadow-purple-500/40 transition-all duration-500 group-hover:scale-105">
              <span className="text-white font-bold text-xl">P</span>
            </div>
            <div>
              <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 group-hover:from-purple-300 group-hover:via-blue-300 group-hover:to-cyan-300 transition-all duration-500">
                Pehance
              </h1>
              <p className="text-xs text-slate-500 font-medium tracking-wide">Precision Prompt Engineering</p>
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-8 text-sm">
            <div className="flex items-center space-x-3 bg-slate-800/40 backdrop-blur-sm px-4 py-2 rounded-full border border-slate-700/50">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50"></div>
              <span className="text-slate-300 font-medium">System Online</span>
            </div>
            <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-sm px-4 py-2 rounded-full text-xs font-semibold text-purple-300 border border-purple-500/30">
              Multi-Agent AI
            </div>
          </div>
        </div>
      </nav>

      {/* Enhanced Hero Section with better typography */}
      <div className="relative z-10 px-6 py-20 text-center">
        <div className="max-w-5xl mx-auto">
          <div className="mb-12">
            <div className="inline-flex items-center bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-sm px-6 py-3 rounded-full border border-purple-500/30 mb-8">
              <span className="text-purple-300 font-semibold text-sm">✨ AI-Powered Enhancement</span>
            </div>
            
            <h2 className="text-7xl md:text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 mb-6 leading-tight tracking-tight">
              Precision
              <br />
              <span className="text-6xl md:text-8xl bg-gradient-to-r from-cyan-400 via-emerald-400 to-purple-400 bg-clip-text text-transparent">Prompt Engineering</span>
            </h2>
            <p className="text-xl md:text-2xl text-slate-300 leading-relaxed max-w-4xl mx-auto font-light">
              Transform ordinary prompts into 
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 font-semibold"> precision-crafted instructions </span>
              that unlock AI's full potential through our advanced multi-agent intelligence system.
            </p>
          </div>
          
          {/* Enhanced Process Indicators with staggered animations */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { name: "Intent Analysis", icon: "🎯", color: "purple", delay: "0ms" },
              { name: "Context Research", icon: "🔍", color: "blue", delay: "150ms" },
              { name: "Best Practices", icon: "⚡", color: "cyan", delay: "300ms" },
              { name: "Enhancement", icon: "✨", color: "pink", delay: "450ms" }
            ].map((step, index) => (
              <div 
                key={index} 
                className="bg-slate-800/30 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-6 hover:bg-slate-700/40 transition-all duration-500 group hover:scale-105 hover:shadow-2xl shadow-lg"
                style={{
                  animationDelay: step.delay,
                  animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards'
                }}
              >
                <div className="text-3xl mb-4 group-hover:scale-125 transition-transform duration-500 filter drop-shadow-lg">
                  {step.icon}
                </div>
                <div className="text-sm text-slate-300 font-semibold tracking-wide">{step.name}</div>
                <div className={`w-full h-1 bg-gradient-to-r from-${step.color}-500 to-${step.color}-600 rounded-full mt-3 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500`}></div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Enhanced Main Interface with premium design */}
      <div className="relative z-10 px-6 pb-20">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-10 items-start">
            
            {/* Enhanced Input Section */}
            <div className="space-y-8">
              <div className="bg-slate-800/40 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl hover:bg-slate-700/40 transition-all duration-700 hover:shadow-purple-500/10 hover:border-slate-600/60 group">
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-2xl font-bold text-white flex items-center group">
                    <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full mr-4 animate-pulse shadow-lg shadow-purple-500/50"></div>
                    Original Prompt
                    <div 
                      className="ml-3 text-slate-400 hover:text-slate-300 cursor-help text-sm"
                      onMouseEnter={() => setShowTooltip("input")}
                      onMouseLeave={() => setShowTooltip("")}
                    >
                      ⓘ
                    </div>
                  </h3>
                  <div className="text-sm text-slate-400 bg-slate-700/50 px-3 py-1 rounded-full">
                    {prompt.length}/2000
                  </div>
                </div>

                {/* Tooltip */}
                {showTooltip === "input" && (
                  <div className="absolute z-20 bg-slate-900/95 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 mt-2 max-w-sm shadow-2xl">
                    <p className="text-sm text-slate-300">Enter any prompt you'd like to enhance. Our AI agents will analyze, research, and optimize it for maximum effectiveness.</p>
                  </div>
                )}
                
                <div className="relative">
                  <textarea
                    value={prompt}
                    onChange={(e) => {
                      setPrompt(e.target.value);
                      adjustTextareaHeight(e.target);
                    }}
                    placeholder="Enter your prompt here...

✨ Examples to try:
• Write a compelling story about artificial intelligence
• Help me build a scalable React application
• Create a comprehensive marketing strategy for a startup
• Develop a research methodology for climate change study"
                    className="w-full min-h-[240px] max-h-[500px] bg-slate-900/60 border-2 border-slate-600/50 rounded-2xl px-6 py-6 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-4 focus:ring-purple-500/30 focus:border-purple-500/70 resize-none transition-all duration-500 text-lg leading-relaxed font-mono tracking-wide shadow-inner"
                    style={{ resize: 'none', overflow: 'hidden' }}
                  />
                  <div className="absolute bottom-4 right-4 text-xs text-slate-500 bg-slate-800/80 px-2 py-1 rounded-lg">
                    {prompt.split('\n').length} lines
                  </div>
                </div>
                
                <div className="flex gap-4 mt-8">
                  <button
                    onClick={handleEnhance}
                    disabled={isLoading || !prompt.trim()}
                    className="flex-1 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-700 hover:via-blue-700 hover:to-cyan-700 disabled:from-slate-600 disabled:via-slate-700 disabled:to-slate-800 text-white font-bold py-5 px-8 rounded-2xl transition-all duration-500 flex items-center justify-center space-x-4 shadow-2xl hover:shadow-purple-500/30 disabled:shadow-none transform hover:scale-[1.02] disabled:scale-100 group relative overflow-hidden"
                  >
                    {/* Button shine effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                    
                    {isLoading ? (
                      <>
                        <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span className="text-lg font-semibold">Enhancing...</span>
                      </>
                    ) : (
                      <>
                        <div className="w-8 h-8 bg-white/20 rounded-xl flex items-center justify-center group-hover:bg-white/30 transition-all duration-500 group-hover:rotate-12">
                          <span className="text-lg">✨</span>
                        </div>
                        <span className="text-lg font-semibold">Enhance Prompt</span>
                        <div className="w-2 h-2 bg-white/60 rounded-full group-hover:bg-white transition-all duration-500 group-hover:scale-125"></div>
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleClear}
                    className="bg-slate-700/60 hover:bg-slate-600/60 text-slate-300 hover:text-white font-semibold py-5 px-8 rounded-2xl transition-all duration-500 border-2 border-slate-600/50 hover:border-slate-500/60 hover:shadow-lg group"
                  >
                    <div className="flex items-center space-x-2">
                      <span className="group-hover:rotate-180 transition-transform duration-500">🗑️</span>
                      <span>Clear</span>
                    </div>
                  </button>
                </div>

                {/* Enhanced Processing Stage with animations */}
                {processingStage && (
                  <div className="mt-8 p-6 bg-gradient-to-r from-purple-900/40 via-blue-900/40 to-cyan-900/40 border-2 border-purple-500/40 rounded-2xl shadow-xl backdrop-blur-sm">
                    <div className="flex items-center space-x-4">
                      <div className="relative">
                        <div className="w-8 h-8 border-3 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
                        <div className="absolute inset-0 w-8 h-8 border-3 border-cyan-400/30 rounded-full animate-ping"></div>
                      </div>
                      <div className="flex-1">
                        <div className="text-purple-300 font-semibold text-lg">{processingStage}</div>
                        <div className="flex space-x-2 mt-3">
                          {processingStages.map((stage, index) => (
                            <div 
                              key={index}
                              className={`w-2 h-2 rounded-full transition-all duration-500 ${
                                index <= currentStageIndex 
                                  ? 'bg-gradient-to-r from-purple-400 to-cyan-400 scale-125' 
                                  : 'bg-slate-600 scale-100'
                              }`}
                            ></div>
                          ))}
                        </div>
                      </div>
                      <div className="text-4xl animate-bounce">
                        {processingStages[currentStageIndex]?.icon || "✨"}
                      </div>
                    </div>
                  </div>
                )}

                {/* Enhanced Error Display */}
                {error && (
                  <div className="mt-8 p-6 bg-gradient-to-r from-red-900/40 to-rose-900/40 border-2 border-red-500/40 rounded-2xl shadow-xl backdrop-blur-sm animate-pulse">
                    <div className="flex items-center space-x-4">
                      <div className="w-6 h-6 text-red-400 animate-bounce">⚠️</div>
                      <span className="text-red-300 font-semibold text-lg">{error}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Enhanced Intent Analysis Card */}
              {intentAnalysis && (
                <div className="bg-slate-800/40 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl animate-fadeInUp">
                  <h4 className="text-2xl font-bold text-white mb-8 flex items-center">
                    <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full mr-4 shadow-lg shadow-green-500/50"></div>
                    Analysis Results
                    <div className="ml-auto text-sm text-slate-400 bg-slate-700/50 px-3 py-1 rounded-full">
                      AI Insights
                    </div>
                  </h4>
                  
                  <div className="grid grid-cols-2 gap-8">
                    <div className="space-y-3">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Intent Category</div>
                      <div className={`inline-flex items-center px-6 py-3 rounded-2xl text-white font-bold text-lg bg-gradient-to-r ${getIntentColor(intentAnalysis.intent_category)} shadow-lg hover:shadow-xl transition-all duration-500 hover:scale-105`}>
                        <span className="capitalize">{intentAnalysis.intent_category}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Confidence</div>
                      <div className="flex items-center space-x-3">
                        <div className="flex-1 bg-slate-700/50 rounded-full h-3 overflow-hidden shadow-inner">
                          <div 
                            className="h-full bg-gradient-to-r from-green-500 via-emerald-500 to-cyan-500 transition-all duration-1500 ease-out shadow-lg" 
                            style={{ width: `${intentAnalysis.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-green-400 font-bold text-lg">
                          {Math.round(intentAnalysis.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Domain</div>
                      <div className="text-blue-400 font-bold text-lg capitalize bg-blue-500/10 px-4 py-2 rounded-xl border border-blue-500/30">
                        {intentAnalysis.specific_domain || 'General'}
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Complexity</div>
                      <div className={`font-bold text-lg capitalize flex items-center space-x-3 px-4 py-2 rounded-xl border ${getComplexityIcon(intentAnalysis.complexity_level).color}`}>
                        <span className="text-2xl">{getComplexityIcon(intentAnalysis.complexity_level).icon}</span>
                        <span className="capitalize">{intentAnalysis.complexity_level}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Enhanced Output Section */}
            <div className="space-y-8">
              {enhancedPrompt ? (
                <div className="bg-slate-800/40 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl animate-fadeInRight">
                  <div className="flex items-center justify-between mb-8">
                    <h3 className="text-2xl font-bold text-white flex items-center">
                      <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full mr-4 shadow-lg shadow-green-500/50"></div>
                      Enhanced Prompt
                    </h3>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm text-slate-400 bg-slate-700/50 px-3 py-1 rounded-full">
                        {enhancedPrompt.length} chars
                      </div>
                      <div className="text-xs text-green-400 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/30">
                        ✓ Enhanced
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-900/80 border-2 border-slate-600/50 rounded-2xl p-8 max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800 shadow-inner backdrop-blur-sm">
                    <pre 
                      ref={enhancedTextRef}
                      className="text-slate-200 text-base leading-relaxed whitespace-pre-wrap font-mono selection:bg-purple-500/30 tracking-wide"
                    >
                      {enhancedPrompt}
                    </pre>
                  </div>
                  
                  <div className="flex gap-4 mt-8">
                    <button
                      onClick={handleCopy}
                      className={`flex-1 font-bold py-4 px-8 rounded-2xl transition-all duration-500 flex items-center justify-center space-x-4 shadow-lg transform hover:scale-[1.02] relative overflow-hidden group ${
                        copySuccess 
                          ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-green-500/30' 
                          : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white hover:shadow-blue-500/30'
                      }`}
                    >
                      {/* Button shine effect */}
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                      
                      <div className="w-6 h-6 transition-transform duration-500 group-hover:scale-110">
                        {copySuccess ? (
                          <span className="text-2xl">✓</span>
                        ) : (
                          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>
                      <span className="text-lg font-semibold">
                        {copySuccess ? 'Copied Successfully!' : 'Copy to Clipboard'}
                      </span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-800/40 backdrop-blur-2xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl">
                  <h3 className="text-2xl font-bold text-white mb-8 flex items-center">
                    <div className="w-4 h-4 bg-slate-500 rounded-full mr-4 animate-pulse"></div>
                    Enhanced Prompt
                  </h3>
                  
                  <div className="bg-slate-900/80 border-2 border-slate-600/50 rounded-2xl p-16 text-center shadow-inner">
                    <div className="w-32 h-32 text-slate-600 mx-auto mb-8 animate-pulse">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <p className="text-slate-400 text-xl font-semibold mb-3">
                      Your enhanced prompt will appear here
                    </p>
                    <p className="text-slate-600 text-base">
                      Enter a prompt above and click "Enhance" to experience the power of AI-driven optimization
                    </p>
                    
                    {/* Floating elements for visual interest */}
                    <div className="flex justify-center space-x-4 mt-8">
                      <div className="w-3 h-3 bg-purple-500/30 rounded-full animate-bounce"></div>
                      <div className="w-3 h-3 bg-blue-500/30 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      <div className="w-3 h-3 bg-cyan-500/30 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Footer with premium design */}
      <div className="relative z-10 px-6 pb-12">
        <div className="max-w-7xl mx-auto">
          <div className="bg-slate-800/30 backdrop-blur-2xl border border-slate-700/30 rounded-3xl p-10 shadow-2xl">
            <div className="text-center mb-12">
              <h4 className="text-3xl font-black text-white mb-4 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Multi-Agent Enhancement Pipeline
              </h4>
              <p className="text-slate-400 text-lg font-light leading-relaxed max-w-2xl mx-auto">
                Four specialized AI agents work in perfect harmony to create the ultimate prompt enhancement experience
              </p>
            </div>
            
            <div className="grid md:grid-cols-4 gap-8">
              {[
                { 
                  title: "Intent Classification", 
                  description: "Deep analysis of your prompt's goal, domain expertise, and complexity requirements",
                  icon: "🎯",
                  color: "from-purple-500/20 via-purple-600/30 to-purple-700/40",
                  border: "border-purple-500/40",
                  shadow: "hover:shadow-purple-500/20"
                },
                { 
                  title: "Context Research", 
                  description: "Advanced knowledge gathering with domain-specific insights and current best practices",
                  icon: "🔍",
                  color: "from-blue-500/20 via-blue-600/30 to-blue-700/40",
                  border: "border-blue-500/40",
                  shadow: "hover:shadow-blue-500/20"
                },
                { 
                  title: "Best Practices", 
                  description: "Universal optimization techniques and enhancement methodologies for maximum effectiveness",
                  icon: "⚡",
                  color: "from-cyan-500/20 via-cyan-600/30 to-cyan-700/40",
                  border: "border-cyan-500/40",
                  shadow: "hover:shadow-cyan-500/20"
                },
                { 
                  title: "Dynamic Enhancement", 
                  description: "Precision-crafted prompt generation with contextual awareness and intelligent optimization",
                  icon: "✨",
                  color: "from-emerald-500/20 via-emerald-600/30 to-emerald-700/40",
                  border: "border-emerald-500/40",
                  shadow: "hover:shadow-emerald-500/20"
                }
              ].map((step, index) => (
                <div 
                  key={index} 
                  className={`bg-gradient-to-br ${step.color} border-2 ${step.border} rounded-3xl p-8 text-center hover:scale-105 transition-all duration-700 group backdrop-blur-sm ${step.shadow} hover:shadow-2xl`}
                  style={{
                    animationDelay: `${index * 150}ms`,
                    animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards'
                  }}
                >
                  <div className="text-5xl mb-6 group-hover:scale-125 transition-transform duration-500 filter drop-shadow-lg">
                    {step.icon}
                  </div>
                  <h5 className="text-white font-bold mb-4 text-xl tracking-wide">
                    {step.title}
                  </h5>
                  <p className="text-slate-300 text-sm leading-relaxed font-light">
                    {step.description}
                  </p>
                  <div className="mt-6 w-full h-1 bg-gradient-to-r from-transparent via-white/30 to-transparent rounded-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700"></div>
                </div>
              ))}
            </div>
            
            {/* Additional premium footer elements */}
            <div className="mt-12 pt-8 border-t border-slate-700/50 flex flex-col md:flex-row items-center justify-between">
              <div className="flex items-center space-x-4 mb-4 md:mb-0">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">P</span>
                </div>
                <span className="text-slate-400 text-sm font-medium">Powered by Advanced AI Intelligence</span>
              </div>
              <div className="flex items-center space-x-6 text-xs text-slate-500">
                <span className="bg-slate-700/50 px-3 py-1 rounded-full">v2.0.0</span>
                <span>🚀 Production Ready</span>
                <span>⚡ High Performance</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;