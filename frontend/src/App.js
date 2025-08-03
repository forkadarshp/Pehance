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
  const enhancedTextRef = useRef(null);

  // Auto-resize textarea
  const adjustTextareaHeight = (element) => {
    element.style.height = 'auto';
    element.style.height = element.scrollHeight + 'px';
  };

  const handleEnhance = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt to enhance");
      return;
    }

    setIsLoading(true);
    setError("");
    setEnhancedPrompt("");
    setIntentAnalysis(null);
    setCopySuccess(false);

    // Simulate processing stages for better UX
    const stages = [
      "Analyzing intent and domain...",
      "Gathering context and research...",
      "Applying best practices...",
      "Generating enhanced prompt..."
    ];

    let stageIndex = 0;
    const stageInterval = setInterval(() => {
      if (stageIndex < stages.length) {
        setProcessingStage(stages[stageIndex]);
        stageIndex++;
      }
    }, 1500);

    try {
      const response = await axios.post(`${API}/enhance`, { prompt });
      clearInterval(stageInterval);
      setProcessingStage("Enhancement complete!");
      
      setTimeout(() => {
        setEnhancedPrompt(response.data.enhanced_prompt);
        setIntentAnalysis(response.data.agent_results.intent_analysis);
        setProcessingStage("");
      }, 500);
      
    } catch (err) {
      clearInterval(stageInterval);
      console.error("Enhancement error:", err);
      setError(
        err.response?.data?.detail || 
        "Enhancement failed. Please check your connection and try again."
      );
      setProcessingStage("");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(enhancedPrompt);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = enhancedPrompt;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleClear = () => {
    setPrompt("");
    setEnhancedPrompt("");
    setError("");
    setIntentAnalysis(null);
    setProcessingStage("");
    setCopySuccess(false);
  };

  const getIntentColor = (category) => {
    const colors = {
      creative: "from-pink-500 to-rose-500",
      technical: "from-blue-500 to-cyan-500", 
      business: "from-green-500 to-emerald-500",
      academic: "from-purple-500 to-violet-500",
      personal: "from-orange-500 to-amber-500",
      other: "from-gray-500 to-slate-500"
    };
    return colors[category] || colors.other;
  };

  const getComplexityIcon = (level) => {
    const icons = {
      basic: "⚡",
      intermediate: "🔥", 
      advanced: "🚀"
    };
    return icons[level] || "⚡";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-3/4 left-1/2 w-64 h-64 bg-pink-600/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
      </div>

      {/* Navigation Bar */}
      <nav className="relative z-10 p-6 border-b border-slate-800/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400">
              Pehance
            </h1>
          </div>
          <div className="hidden md:flex items-center space-x-6 text-sm text-slate-400">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>System Online</span>
            </div>
            <div className="bg-slate-800/50 px-3 py-1 rounded-full text-xs">
              Multi-Agent AI
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative z-10 px-6 py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h2 className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 mb-6 leading-tight">
              Precision
              <br />
              <span className="text-5xl md:text-7xl">Prompt Engineering</span>
            </h2>
            <p className="text-xl md:text-2xl text-slate-300 leading-relaxed max-w-3xl mx-auto">
              Transform ordinary prompts into 
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 font-semibold"> precision-crafted instructions </span>
              that unlock AI's full potential through our advanced multi-agent system.
            </p>
          </div>
          
          {/* Process Indicators */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
            {[
              { name: "Intent Analysis", icon: "🎯", color: "purple" },
              { name: "Context Research", icon: "🔍", color: "blue" },
              { name: "Best Practices", icon: "⚡", color: "cyan" },
              { name: "Enhancement", icon: "✨", color: "pink" }
            ].map((step, index) => (
              <div key={index} className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-4 hover:bg-slate-700/30 transition-all duration-300 group">
                <div className={`text-2xl mb-2 group-hover:scale-110 transition-transform duration-300`}>
                  {step.icon}
                </div>
                <div className="text-sm text-slate-300 font-medium">{step.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Interface */}
      <div className="relative z-10 px-6 pb-16">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8 items-start">
            
            {/* Input Section */}
            <div className="space-y-6">
              <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl hover:bg-slate-700/40 transition-all duration-500">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-white flex items-center">
                    <div className="w-3 h-3 bg-purple-500 rounded-full mr-3 animate-pulse"></div>
                    Original Prompt
                  </h3>
                  <div className="text-sm text-slate-400">
                    {prompt.length}/2000
                  </div>
                </div>
                
                <textarea
                  value={prompt}
                  onChange={(e) => {
                    setPrompt(e.target.value);
                    adjustTextareaHeight(e.target);
                  }}
                  placeholder="Enter your prompt here...

Examples to try:
• Write a compelling story about artificial intelligence
• Help me build a scalable React application
• Create a comprehensive marketing strategy for a startup
• Develop a research methodology for climate change study"
                  className="w-full min-h-[200px] max-h-[400px] bg-slate-900/50 border border-slate-600/50 rounded-2xl px-6 py-4 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 resize-none transition-all duration-300 text-lg leading-relaxed"
                  style={{ resize: 'none', overflow: 'hidden' }}
                />
                
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={handleEnhance}
                    disabled={isLoading || !prompt.trim()}
                    className="flex-1 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-700 hover:via-blue-700 hover:to-cyan-700 disabled:from-slate-600 disabled:via-slate-700 disabled:to-slate-800 text-white font-bold py-4 px-8 rounded-2xl transition-all duration-300 flex items-center justify-center space-x-3 shadow-xl hover:shadow-purple-500/25 disabled:shadow-none transform hover:scale-[1.02] disabled:scale-100 group"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span className="text-lg">Enhancing...</span>
                      </>
                    ) : (
                      <>
                        <div className="w-6 h-6 bg-white/20 rounded-lg flex items-center justify-center group-hover:bg-white/30 transition-colors duration-300">
                          <span className="text-sm">✨</span>
                        </div>
                        <span className="text-lg">Enhance Prompt</span>
                        <div className="w-2 h-2 bg-white/50 rounded-full group-hover:bg-white transition-colors duration-300"></div>
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleClear}
                    className="bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 font-medium py-4 px-6 rounded-2xl transition-all duration-300 border border-slate-600/50 hover:border-slate-500/50"
                  >
                    Clear
                  </button>
                </div>

                {/* Processing Stage */}
                {processingStage && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/30 rounded-2xl">
                    <div className="flex items-center space-x-3">
                      <div className="w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-purple-300 font-medium">{processingStage}</span>
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {error && (
                  <div className="mt-6 p-4 bg-red-900/20 border border-red-500/30 rounded-2xl">
                    <div className="flex items-center space-x-3">
                      <div className="w-5 h-5 text-red-400">⚠️</div>
                      <span className="text-red-300 font-medium">{error}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Intent Analysis Card */}
              {intentAnalysis && (
                <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl">
                  <h4 className="text-xl font-bold text-white mb-6 flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                    Analysis Results
                  </h4>
                  
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <div className="text-xs text-slate-500 uppercase tracking-wide font-semibold">Intent Category</div>
                      <div className={`inline-flex items-center px-4 py-2 rounded-xl text-white font-bold text-lg bg-gradient-to-r ${getIntentColor(intentAnalysis.intent_category)}`}>
                        {intentAnalysis.intent_category}
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="text-xs text-slate-500 uppercase tracking-wide font-semibold">Confidence</div>
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-slate-700 rounded-full h-2 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-1000 ease-out" 
                            style={{ width: `${intentAnalysis.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-green-400 font-bold">
                          {Math.round(intentAnalysis.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="text-xs text-slate-500 uppercase tracking-wide font-semibold">Domain</div>
                      <div className="text-blue-400 font-semibold text-lg capitalize">
                        {intentAnalysis.specific_domain || 'General'}
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="text-xs text-slate-500 uppercase tracking-wide font-semibold">Complexity</div>
                      <div className="text-amber-400 font-semibold text-lg capitalize flex items-center space-x-2">
                        <span>{getComplexityIcon(intentAnalysis.complexity_level)}</span>
                        <span>{intentAnalysis.complexity_level}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Output Section */}
            <div className="space-y-6">
              {enhancedPrompt ? (
                <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-white flex items-center">
                      <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                      Enhanced Prompt
                    </h3>
                    <div className="text-sm text-slate-400">
                      {enhancedPrompt.length} characters
                    </div>
                  </div>
                  
                  <div className="bg-slate-900/60 border border-slate-600/50 rounded-2xl p-6 max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
                    <pre 
                      ref={enhancedTextRef}
                      className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap font-mono selection:bg-purple-500/30"
                    >
                      {enhancedPrompt}
                    </pre>
                  </div>
                  
                  <div className="flex gap-4 mt-6">
                    <button
                      onClick={handleCopy}
                      className={`flex-1 font-bold py-3 px-6 rounded-2xl transition-all duration-300 flex items-center justify-center space-x-3 shadow-lg transform hover:scale-[1.02] ${
                        copySuccess 
                          ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white' 
                          : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white hover:shadow-blue-500/25'
                      }`}
                    >
                      <div className="w-5 h-5">
                        {copySuccess ? (
                          <span className="text-lg">✓</span>
                        ) : (
                          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>
                      <span>{copySuccess ? 'Copied Successfully!' : 'Copy to Clipboard'}</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
                    <div className="w-3 h-3 bg-slate-500 rounded-full mr-3"></div>
                    Enhanced Prompt
                  </h3>
                  
                  <div className="bg-slate-900/60 border border-slate-600/50 rounded-2xl p-12 text-center">
                    <div className="w-24 h-24 text-slate-600 mx-auto mb-6 animate-pulse">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <p className="text-slate-500 text-lg">
                      Your enhanced prompt will appear here
                    </p>
                    <p className="text-slate-600 text-sm mt-2">
                      Enter a prompt above and click "Enhance" to get started
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="relative z-10 px-6 pb-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-slate-800/30 backdrop-blur-xl border border-slate-700/30 rounded-3xl p-8">
            <div className="text-center mb-8">
              <h4 className="text-2xl font-bold text-white mb-2">
                Multi-Agent Enhancement Pipeline
              </h4>
              <p className="text-slate-400">
                Four specialized AI agents work in harmony to create the perfect prompt
              </p>
            </div>
            
            <div className="grid md:grid-cols-4 gap-6">
              {[
                { 
                  title: "Intent Classification", 
                  description: "Analyzes your prompt's goal, domain, and complexity level",
                  icon: "🎯",
                  color: "from-purple-500/20 to-purple-600/30",
                  border: "border-purple-500/30"
                },
                { 
                  title: "Context Research", 
                  description: "Gathers domain-specific knowledge and best practices",
                  icon: "🔍",
                  color: "from-blue-500/20 to-blue-600/30",
                  border: "border-blue-500/30"
                },
                { 
                  title: "Best Practices", 
                  description: "Applies universal optimization and enhancement techniques",
                  icon: "⚡",
                  color: "from-cyan-500/20 to-cyan-600/30",
                  border: "border-cyan-500/30"
                },
                { 
                  title: "Dynamic Enhancement", 
                  description: "Creates precision-crafted prompts with contextual awareness",
                  icon: "✨",
                  color: "from-pink-500/20 to-pink-600/30",
                  border: "border-pink-500/30"
                }
              ].map((step, index) => (
                <div key={index} className={`bg-gradient-to-br ${step.color} border ${step.border} rounded-2xl p-6 text-center hover:scale-105 transition-all duration-300 group`}>
                  <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">
                    {step.icon}
                  </div>
                  <h5 className="text-white font-bold mb-2 text-lg">
                    {step.title}
                  </h5>
                  <p className="text-slate-300 text-sm leading-relaxed">
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
