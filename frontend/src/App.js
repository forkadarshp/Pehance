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
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);
  const [typingAnimation, setTypingAnimation] = useState("");
  const [enhancementMetrics, setEnhancementMetrics] = useState(null);
  
  const enhancedTextRef = useRef(null);
  const heroRef = useRef(null);
  const inputSectionRef = useRef(null);

  // Advanced mouse tracking for subtle parallax effects
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Intersection observer for staggered animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-reveal');
            setIsVisible(true);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -100px 0px' }
    );

    if (heroRef.current) observer.observe(heroRef.current);
    if (inputSectionRef.current) observer.observe(inputSectionRef.current);

    return () => observer.disconnect();
  }, []);

  // Sophisticated textarea auto-resize with momentum
  const adjustTextareaHeight = (element) => {
    const minHeight = 240;
    const maxHeight = 500;
    
    element.style.height = 'auto';
    const newHeight = Math.min(Math.max(element.scrollHeight, minHeight), maxHeight);
    element.style.height = newHeight + 'px';
    
    // Add momentum-based transition
    element.style.transition = 'height 0.4s cubic-bezier(0.23, 1, 0.32, 1), box-shadow 0.3s ease';
  };

  // Typewriter effect for enhanced prompts
  const typewriterEffect = (text, callback) => {
    let index = 0;
    const speed = 15; // Adjust typing speed
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

    // Enhanced processing stages with precise timing
    const stages = [
      { text: "Analyzing intent and domain expertise...", icon: "🎯", duration: 2200, color: "from-purple-500 to-blue-500" },
      { text: "Gathering contextual research and insights...", icon: "🔍", duration: 2400, color: "from-blue-500 to-cyan-500" },
      { text: "Applying universal best practices...", icon: "⚡", duration: 1800, color: "from-cyan-500 to-emerald-500" },
      { text: "Crafting precision-enhanced prompt...", icon: "✨", duration: 2600, color: "from-emerald-500 to-purple-500" }
    ];

    // Orchestrated stage progression with realistic timing
    let totalStages = stages.length;
    let currentStage = 0;
    
    const advanceStage = () => {
      if (currentStage < totalStages - 1) {
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
      
      setProcessingStage("Enhancement complete! ✨");
      
      // Calculate enhancement metrics
      const metrics = {
        originalLength: prompt.length,
        enhancedLength: response.data.enhanced_prompt.length,
        improvementRatio: (response.data.enhanced_prompt.length / prompt.length).toFixed(1),
        processingTime: processingTime,
        confidenceScore: response.data.agent_results.intent_analysis.confidence,
        agentSteps: response.data.agent_results.process_steps?.length || 4
      };
      
      setEnhancementMetrics(metrics);
      
      setTimeout(() => {
        // Start typewriter effect for enhanced prompt
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
        "Enhancement failed. Our AI agents are experiencing high demand. Please try again in a moment.";
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
      
      // Haptic feedback simulation through visual feedback
      const button = document.querySelector('.copy-button');
      if (button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
          button.style.transform = 'scale(1)';
        }, 100);
      }
      
      setTimeout(() => setCopySuccess(false), 3000);
    } catch (err) {
      // Enhanced fallback with better UX
      const textArea = document.createElement('textarea');
      textArea.value = enhancedPrompt;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
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
      basic: { icon: "⚡", color: "text-green-400", bg: "bg-green-400/10" },
      intermediate: { icon: "🔥", color: "text-orange-400", bg: "bg-orange-400/10" }, 
      advanced: { icon: "🚀", color: "text-purple-400", bg: "bg-purple-400/10" }
    };
    return icons[level] || icons.basic;
  };

  // Enhanced processing stages with precise UI coordination
  const processingStages = [
    { text: "Analyzing intent and domain expertise...", icon: "🎯", color: "from-purple-500 to-blue-500" },
    { text: "Gathering contextual research and insights...", icon: "🔍", color: "from-blue-500 to-cyan-500" },
    { text: "Applying universal best practices...", icon: "⚡", color: "from-cyan-500 to-emerald-500" },
    { text: "Crafting precision-enhanced prompt...", icon: "✨", color: "from-emerald-500 to-purple-500" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Advanced dynamic background with mouse-reactive elements */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Primary background layers */}
        <div 
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-purple-600/12 to-blue-600/12 rounded-full blur-3xl animate-pulse"
          style={{
            transform: `translate(${(mousePosition.x - 50) * 0.02}px, ${(mousePosition.y - 50) * 0.02}px)`
          }}
        ></div>
        <div 
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-to-r from-cyan-600/12 to-emerald-600/12 rounded-full blur-3xl animate-pulse" 
          style={{
            animationDelay: '2s',
            transform: `translate(${(mousePosition.x - 50) * -0.015}px, ${(mousePosition.y - 50) * -0.015}px)`
          }}
        ></div>
        <div 
          className="absolute top-3/4 left-1/2 w-64 h-64 bg-gradient-to-r from-pink-600/12 to-rose-600/12 rounded-full blur-3xl animate-pulse" 
          style={{
            animationDelay: '4s',
            transform: `translate(${(mousePosition.x - 50) * 0.01}px, ${(mousePosition.y - 50) * 0.01}px)`
          }}
        ></div>
        
        {/* Secondary depth layers with subtle motion */}
        <div 
          className="absolute top-1/2 left-1/8 w-48 h-48 bg-gradient-to-r from-indigo-600/8 to-purple-600/8 rounded-full blur-2xl animate-pulse" 
          style={{
            animationDelay: '1s',
            transform: `translate(${(mousePosition.x - 50) * 0.008}px, ${(mousePosition.y - 50) * 0.005}px)`
          }}
        ></div>
        <div 
          className="absolute bottom-1/8 right-1/8 w-56 h-56 bg-gradient-to-r from-teal-600/8 to-cyan-600/8 rounded-full blur-2xl animate-pulse" 
          style={{
            animationDelay: '3s',
            transform: `translate(${(mousePosition.x - 50) * -0.01}px, ${(mousePosition.y - 50) * 0.007}px)`
          }}
        ></div>

        {/* Sophisticated mesh gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-slate-900/20 to-transparent opacity-60"></div>
        
        {/* Subtle texture overlay */}
        <div className="absolute inset-0 opacity-[0.015]" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Ccircle cx='7' cy='7' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          backgroundSize: '60px 60px'
        }}></div>
      </div>

      {/* Sophisticated Navigation with subtle interactions */}
      <nav className="relative z-10 p-6 border-b border-slate-800/40 backdrop-blur-2xl bg-slate-900/10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-5 group cursor-pointer">
            <div className="relative">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/25 group-hover:shadow-purple-500/40 transition-all duration-700 group-hover:scale-105 relative overflow-hidden">
                <span className="text-white font-black text-xl relative z-10">P</span>
                {/* Subtle shine effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              </div>
              {/* Pulsing ring indicator */}
              <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-700 animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 group-hover:from-purple-300 group-hover:via-blue-300 group-hover:to-cyan-300 transition-all duration-700">
                Pehance
              </h1>
              <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase opacity-80 group-hover:opacity-100 transition-opacity duration-500">
                Precision Prompt Engineering
              </p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <div className="flex items-center space-x-3 bg-slate-800/30 backdrop-blur-xl px-5 py-3 rounded-2xl border border-slate-700/40 hover:border-slate-600/60 transition-all duration-500 group">
              <div className="w-2.5 h-2.5 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/60"></div>
              <span className="text-slate-300 font-semibold text-sm">System Online</span>
              <div className="text-xs text-slate-500 bg-slate-700/50 px-2 py-1 rounded-lg">99.9%</div>
            </div>
            
            <div className="bg-gradient-to-r from-purple-600/15 to-blue-600/15 backdrop-blur-xl px-5 py-3 rounded-2xl border border-purple-500/25 hover:border-purple-500/40 transition-all duration-500 group">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-ping"></div>
                <span className="text-sm font-bold text-purple-300">Multi-Agent AI</span>
                <span className="text-xs text-purple-400 bg-purple-500/20 px-2 py-0.5 rounded-full">v2.0</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Enhanced Hero Section with sophisticated typography and animations */}
      <div ref={heroRef} className="relative z-10 px-6 py-24 text-center">
        <div className="max-w-6xl mx-auto">
          <div className="mb-16">
            {/* Status badge with subtle animation */}
            <div className="inline-flex items-center bg-gradient-to-r from-purple-600/15 to-blue-600/15 backdrop-blur-xl px-8 py-4 rounded-2xl border border-purple-500/25 mb-12 group hover:border-purple-500/40 transition-all duration-700">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-3 h-3 bg-purple-400 rounded-full animate-pulse"></div>
                  <div className="absolute inset-0 w-3 h-3 bg-purple-400 rounded-full animate-ping opacity-30"></div>
                </div>
                <span className="text-purple-300 font-bold text-sm tracking-wide">✨ AI-Powered Enhancement</span>
                <div className="text-xs text-purple-400 bg-purple-500/20 px-3 py-1 rounded-full font-semibold">LIVE</div>
              </div>
            </div>
            
            {/* Main headline with advanced typography */}
            <h2 className="text-8xl md:text-10xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 mb-8 leading-[0.85] tracking-tight">
              Precision
              <br />
              <span className="text-7xl md:text-9xl bg-gradient-to-r from-cyan-400 via-emerald-400 to-purple-400 bg-clip-text text-transparent relative">
                Prompt Engineering
                {/* Subtle text shadow effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/20 via-emerald-400/20 to-purple-400/20 blur-xl -z-10"></div>
              </span>
            </h2>
            
            {/* Enhanced subtitle with better hierarchy */}
            <div className="max-w-4xl mx-auto">
              <p className="text-2xl md:text-3xl text-slate-300 leading-relaxed font-light mb-6">
                Transform ordinary prompts into 
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 font-semibold mx-2">precision-crafted instructions</span>
                that unlock AI's full potential through our advanced multi-agent intelligence system.
              </p>
              <div className="flex flex-wrap justify-center gap-4 text-sm text-slate-500">
                <span className="bg-slate-800/40 px-4 py-2 rounded-full border border-slate-700/50">
                  🎯 Intent Analysis
                </span>
                <span className="bg-slate-800/40 px-4 py-2 rounded-full border border-slate-700/50">
                  🔍 Context Research
                </span>
                <span className="bg-slate-800/40 px-4 py-2 rounded-full border border-slate-700/50">
                  ⚡ Best Practices
                </span>
                <span className="bg-slate-800/40 px-4 py-2 rounded-full border border-slate-700/50">
                  ✨ Dynamic Enhancement
                </span>
              </div>
            </div>
          </div>
          
          {/* Enhanced Process Indicators with sophisticated staggered reveal */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {[
              { name: "Intent Analysis", icon: "🎯", color: "purple", delay: "0ms", desc: "Domain & Complexity" },
              { name: "Context Research", icon: "🔍", color: "blue", delay: "200ms", desc: "Industry Insights" },
              { name: "Best Practices", icon: "⚡", color: "cyan", delay: "400ms", desc: "Universal Optimization" },
              { name: "Enhancement", icon: "✨", color: "emerald", delay: "600ms", desc: "Precision Crafting" }
            ].map((step, index) => (
              <div 
                key={index} 
                className={`bg-slate-800/25 backdrop-blur-2xl border border-slate-700/40 rounded-3xl p-8 hover:bg-slate-700/30 transition-all duration-700 group hover:scale-105 hover:shadow-2xl shadow-lg opacity-0 animate-reveal-stagger cursor-pointer`}
                style={{
                  animationDelay: step.delay,
                  animationFillMode: 'forwards'
                }}
              >
                <div className="text-4xl mb-6 group-hover:scale-125 transition-transform duration-700 filter drop-shadow-2xl">
                  {step.icon}
                </div>
                <div className="text-base text-slate-300 font-bold tracking-wide mb-2">{step.name}</div>
                <div className="text-xs text-slate-500 font-medium">{step.desc}</div>
                <div className={`w-full h-1 bg-gradient-to-r from-${step.color}-500 to-${step.color}-600 rounded-full mt-4 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 origin-left`}></div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Enhanced Main Interface with expert-level sophistication */}
      <div ref={inputSectionRef} className="relative z-10 px-6 pb-24">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-start">
            
            {/* Sophisticated Input Section */}
            <div className="space-y-8">
              <div className="bg-slate-800/30 backdrop-blur-2xl border border-slate-700/40 rounded-3xl p-10 shadow-2xl hover:bg-slate-700/35 transition-all duration-700 hover:shadow-purple-500/5 hover:border-slate-600/50 group relative overflow-hidden">
                {/* Subtle animated border */}
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-transparent to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-1000 pointer-events-none"></div>
                
                <div className="flex items-center justify-between mb-10 relative z-10">
                  <div className="flex items-center space-x-4">
                    <h3 className="text-2xl font-bold text-white flex items-center">
                      <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full mr-4 animate-pulse shadow-lg shadow-purple-500/60 relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-ping opacity-30"></div>
                      </div>
                      Original Prompt
                    </h3>
                    <div 
                      className="ml-2 text-slate-400 hover:text-slate-300 cursor-help text-sm transition-colors duration-300 relative group-tooltip"
                      onMouseEnter={() => setShowTooltip("input")}
                      onMouseLeave={() => setShowTooltip("")}
                    >
                      <div className="w-5 h-5 rounded-full border border-slate-500 flex items-center justify-center text-xs font-bold hover:border-slate-400 transition-colors duration-300">
                        ?
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-sm text-slate-400 bg-slate-700/40 px-4 py-2 rounded-full border border-slate-600/40">
                      {prompt.length}/2000
                    </div>
                    {prompt.length > 0 && (
                      <div className="text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/30 animate-fadeIn">
                        Ready
                      </div>
                    )}
                  </div>
                </div>

                {/* Advanced Tooltip */}
                {showTooltip === "input" && (
                  <div className="absolute top-20 left-10 z-30 bg-slate-900/95 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 max-w-sm shadow-2xl animate-fadeIn">
                    <div className="text-sm text-slate-300 leading-relaxed">
                      <div className="text-white font-semibold mb-2">💡 Pro Tip</div>
                      Enter any prompt you'd like to enhance. Our AI agents will analyze intent, research context, and optimize it for maximum effectiveness.
                    </div>
                    <div className="absolute -top-2 left-8 w-4 h-4 bg-slate-900 border-l border-t border-slate-700/50 transform rotate-45"></div>
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
• Write a compelling story about artificial intelligence and human creativity
• Help me build a scalable React application with modern best practices
• Create a comprehensive marketing strategy for a SaaS startup targeting small businesses
• Develop a research methodology for studying climate change impact on coastal ecosystems"
                    className="w-full min-h-[260px] max-h-[600px] bg-slate-900/50 border-2 border-slate-600/40 rounded-2xl px-8 py-8 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-4 focus:ring-purple-500/25 focus:border-purple-500/60 resize-none transition-all duration-500 text-lg leading-relaxed font-mono tracking-wide shadow-inner backdrop-blur-sm"
                    style={{ resize: 'none', overflow: 'hidden' }}
                  />
                  <div className="absolute bottom-6 right-6 flex items-center space-x-4">
                    <div className="text-xs text-slate-500 bg-slate-800/60 px-3 py-1 rounded-lg border border-slate-700/40">
                      {prompt.split('\n').length} lines
                    </div>
                    <div className="text-xs text-slate-500 bg-slate-800/60 px-3 py-1 rounded-lg border border-slate-700/40">
                      {prompt.split(' ').filter(word => word.length > 0).length} words
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-6 mt-10">
                  <button
                    onClick={handleEnhance}
                    disabled={isLoading || !prompt.trim()}
                    className="flex-1 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-700 hover:via-blue-700 hover:to-cyan-700 disabled:from-slate-600 disabled:via-slate-700 disabled:to-slate-800 text-white font-bold py-6 px-10 rounded-2xl transition-all duration-500 flex items-center justify-center space-x-4 shadow-2xl hover:shadow-purple-500/30 disabled:shadow-none transform hover:scale-[1.02] disabled:scale-100 group relative overflow-hidden"
                  >
                    {/* Advanced button shine effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/25 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1200"></div>
                    
                    {isLoading ? (
                      <>
                        <div className="relative">
                          <div className="w-7 h-7 border-3 border-white/80 border-t-transparent rounded-full animate-spin"></div>
                          <div className="absolute inset-0 w-7 h-7 border-3 border-cyan-400/40 rounded-full animate-ping"></div>
                        </div>
                        <span className="text-lg font-bold">Enhancing...</span>
                      </>
                    ) : (
                      <>
                        <div className="w-10 h-10 bg-white/15 rounded-xl flex items-center justify-center group-hover:bg-white/25 transition-all duration-500 group-hover:rotate-12 shadow-lg">
                          <span className="text-xl">✨</span>
                        </div>
                        <span className="text-lg font-bold">Enhance Prompt</span>
                        <div className="w-2 h-2 bg-white/70 rounded-full group-hover:bg-white transition-all duration-500 group-hover:scale-150 shadow-sm"></div>
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleClear}
                    className="bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-white font-bold py-6 px-10 rounded-2xl transition-all duration-500 border-2 border-slate-600/40 hover:border-slate-500/60 hover:shadow-xl group relative overflow-hidden"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-lg group-hover:rotate-180 transition-transform duration-500">🗑️</span>
                      <span>Clear</span>
                    </div>
                  </button>
                </div>

                {/* Sophisticated Processing Stage with orchestrated animations */}
                {processingStage && (
                  <div className="mt-10 p-8 bg-gradient-to-r from-purple-900/30 via-blue-900/30 to-cyan-900/30 border-2 border-purple-500/30 rounded-2xl shadow-2xl backdrop-blur-xl animate-fadeIn">
                    <div className="flex items-center space-x-6">
                      <div className="relative">
                        <div className="w-10 h-10 border-3 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
                        <div className="absolute inset-0 w-10 h-10 border-3 border-cyan-400/20 rounded-full animate-ping"></div>
                        <div className="absolute inset-2 w-6 h-6 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-full animate-pulse opacity-60"></div>
                      </div>
                      <div className="flex-1">
                        <div className="text-purple-300 font-bold text-xl mb-2">{processingStage}</div>
                        <div className="flex space-x-2 mb-3">
                          {processingStages.map((stage, index) => (
                            <div 
                              key={index}
                              className={`w-3 h-3 rounded-full transition-all duration-700 ${
                                index <= currentStageIndex 
                                  ? 'bg-gradient-to-r from-purple-400 to-cyan-400 scale-125 shadow-lg shadow-purple-400/50' 
                                  : 'bg-slate-600/60 scale-100'
                              }`}
                            ></div>
                          ))}
                        </div>
                        <div className="text-sm text-purple-400/80 font-medium">
                          Step {currentStageIndex + 1} of {processingStages.length}
                        </div>
                      </div>
                      <div className="text-5xl animate-bounce-subtle">
                        {processingStages[currentStageIndex]?.icon || "✨"}
                      </div>
                    </div>
                  </div>
                )}

                {/* Enhanced Error Display with better UX */}
                {error && (
                  <div className="mt-10 p-8 bg-gradient-to-r from-red-900/30 to-rose-900/30 border-2 border-red-500/30 rounded-2xl shadow-2xl backdrop-blur-xl animate-shake">
                    <div className="flex items-center space-x-6">
                      <div className="w-8 h-8 text-red-400 animate-bounce-subtle">⚠️</div>
                      <div>
                        <div className="text-red-300 font-bold text-lg mb-1">{error}</div>
                        <div className="text-red-400/80 text-sm">Please check your connection and try again</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Sophisticated Intent Analysis Card */}
              {intentAnalysis && (
                <div className="bg-slate-800/30 backdrop-blur-2xl border border-slate-700/40 rounded-3xl p-10 shadow-2xl animate-slideInUp">
                  <div className="flex items-center justify-between mb-10">
                    <h4 className="text-2xl font-bold text-white flex items-center">
                      <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full mr-4 shadow-lg shadow-green-500/60 relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full animate-ping opacity-30"></div>
                      </div>
                      Analysis Results
                    </h4>
                    <div className="flex items-center space-x-3">
                      <div className="text-sm text-slate-400 bg-slate-700/40 px-4 py-2 rounded-full border border-slate-600/40">
                        AI Insights
                      </div>
                      <div className="text-xs text-green-400 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/30">
                        Verified ✓
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-10">
                    <div className="space-y-4">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Intent Category</div>
                      <div className={`inline-flex items-center px-8 py-4 rounded-2xl text-white font-bold text-xl bg-gradient-to-r ${getIntentColor(intentAnalysis.intent_category)} shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-105 relative overflow-hidden group`}>
                        <span className="capitalize relative z-10">{intentAnalysis.intent_category}</span>
                        <div className="absolute inset-0 bg-white/10 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Confidence Score</div>
                      <div className="flex items-center space-x-4">
                        <div className="flex-1 bg-slate-700/40 rounded-full h-4 overflow-hidden shadow-inner border border-slate-600/40">
                          <div 
                            className="h-full bg-gradient-to-r from-green-500 via-emerald-500 to-cyan-500 transition-all duration-2000 ease-out shadow-lg relative overflow-hidden" 
                            style={{ width: `${intentAnalysis.confidence * 100}%` }}
                          >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent transform -skew-x-12 animate-shimmer"></div>
                          </div>
                        </div>
                        <span className="text-green-400 font-bold text-xl min-w-[4rem]">
                          {Math.round(intentAnalysis.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Domain Expertise</div>
                      <div className="text-blue-400 font-bold text-xl capitalize bg-blue-500/10 px-6 py-3 rounded-2xl border border-blue-500/25 hover:border-blue-500/40 transition-all duration-500 hover:bg-blue-500/15">
                        {intentAnalysis.specific_domain || 'General'}
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Complexity Level</div>
                      <div className={`font-bold text-xl capitalize flex items-center space-x-4 px-6 py-3 rounded-2xl border transition-all duration-500 hover:scale-105 ${getComplexityIcon(intentAnalysis.complexity_level).bg} ${getComplexityIcon(intentAnalysis.complexity_level).color} border-current/25 hover:border-current/40`}>
                        <span className="text-3xl">{getComplexityIcon(intentAnalysis.complexity_level).icon}</span>
                        <span className="capitalize">{intentAnalysis.complexity_level}</span>
                      </div>
                    </div>
                  </div>

                  {/* Enhancement Metrics */}
                  {enhancementMetrics && (
                    <div className="mt-10 pt-8 border-t border-slate-700/40">
                      <div className="grid grid-cols-3 gap-8 text-center">
                        <div className="bg-slate-900/40 rounded-2xl p-6 border border-slate-700/30">
                          <div className="text-2xl font-bold text-purple-400 mb-2">{enhancementMetrics.improvementRatio}x</div>
                          <div className="text-sm text-slate-500 font-medium">Enhancement Ratio</div>
                        </div>
                        <div className="bg-slate-900/40 rounded-2xl p-6 border border-slate-700/30">
                          <div className="text-2xl font-bold text-cyan-400 mb-2">{enhancementMetrics.processingTime}s</div>
                          <div className="text-sm text-slate-500 font-medium">Processing Time</div>
                        </div>
                        <div className="bg-slate-900/40 rounded-2xl p-6 border border-slate-700/30">
                          <div className="text-2xl font-bold text-emerald-400 mb-2">{enhancementMetrics.agentSteps}</div>
                          <div className="text-sm text-slate-500 font-medium">Agent Steps</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Sophisticated Output Section */}
            <div className="space-y-8">
              {enhancedPrompt ? (
                <div className="bg-slate-800/30 backdrop-blur-2xl border border-slate-700/40 rounded-3xl p-10 shadow-2xl animate-slideInRight">
                  <div className="flex items-center justify-between mb-10">
                    <h3 className="text-2xl font-bold text-white flex items-center">
                      <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full mr-4 shadow-lg shadow-green-500/60 relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full animate-ping opacity-30"></div>
                      </div>
                      Enhanced Prompt
                    </h3>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm text-slate-400 bg-slate-700/40 px-4 py-2 rounded-full border border-slate-600/40">
                        {enhancedPrompt.length} chars
                      </div>
                      <div className="text-xs text-green-400 bg-green-500/10 px-3 py-1 rounded-full border border-green-500/30 animate-pulse">
                        ✓ Enhanced
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-900/60 border-2 border-slate-600/40 rounded-2xl p-10 max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800 shadow-inner backdrop-blur-sm relative">
                    <pre 
                      ref={enhancedTextRef}
                      className="text-slate-200 text-base leading-relaxed whitespace-pre-wrap font-mono selection:bg-purple-500/30 tracking-wide"
                    >
                      {typingAnimation || enhancedPrompt}
                    </pre>
                    {typingAnimation && (
                      <span className="inline-block w-0.5 h-5 bg-purple-400 animate-blink ml-1"></span>
                    )}
                  </div>
                  
                  <div className="flex gap-6 mt-10">
                    <button
                      onClick={handleCopy}
                      className={`copy-button flex-1 font-bold py-5 px-10 rounded-2xl transition-all duration-500 flex items-center justify-center space-x-4 shadow-xl transform hover:scale-[1.02] relative overflow-hidden group ${
                        copySuccess 
                          ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-green-500/40' 
                          : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white hover:shadow-blue-500/40'
                      }`}
                    >
                      {/* Advanced button shine effect */}
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/25 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1200"></div>
                      
                      <div className="w-7 h-7 transition-transform duration-500 group-hover:scale-110 relative z-10">
                        {copySuccess ? (
                          <div className="w-full h-full flex items-center justify-center">
                            <span className="text-2xl animate-bounceIn">✓</span>
                          </div>
                        ) : (
                          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>
                      <span className="text-lg font-bold relative z-10">
                        {copySuccess ? 'Copied Successfully!' : 'Copy to Clipboard'}
                      </span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-800/30 backdrop-blur-2xl border border-slate-700/40 rounded-3xl p-10 shadow-2xl">
                  <h3 className="text-2xl font-bold text-white mb-10 flex items-center">
                    <div className="w-4 h-4 bg-slate-500 rounded-full mr-4 animate-pulse"></div>
                    Enhanced Prompt
                  </h3>
                  
                  <div className="bg-slate-900/60 border-2 border-slate-600/40 rounded-2xl p-20 text-center shadow-inner relative overflow-hidden">
                    {/* Animated background pattern */}
                    <div className="absolute inset-0 opacity-[0.02]">
                      <div className="w-full h-full bg-gradient-to-br from-purple-500 via-blue-500 to-cyan-500 animate-pulse"></div>
                    </div>
                    
                    <div className="relative z-10">
                      <div className="w-40 h-40 text-slate-600 mx-auto mb-10 animate-float">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <p className="text-slate-400 text-2xl font-bold mb-4">
                        Your enhanced prompt will appear here
                      </p>
                      <p className="text-slate-600 text-lg leading-relaxed max-w-md mx-auto">
                        Enter a prompt above and click "Enhance" to experience the power of AI-driven optimization
                      </p>
                      
                      {/* Sophisticated floating elements */}
                      <div className="flex justify-center space-x-6 mt-12">
                        <div className="w-4 h-4 bg-purple-500/20 rounded-full animate-bounce"></div>
                        <div className="w-4 h-4 bg-blue-500/20 rounded-full animate-bounce" style={{animationDelay: '0.3s'}}></div>
                        <div className="w-4 h-4 bg-cyan-500/20 rounded-full animate-bounce" style={{animationDelay: '0.6s'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Premium Footer with expert-level attention to detail */}
      <div className="relative z-10 px-6 pb-16">
        <div className="max-w-7xl mx-auto">
          <div className="bg-slate-800/25 backdrop-blur-2xl border border-slate-700/25 rounded-3xl p-12 shadow-2xl relative overflow-hidden">
            {/* Subtle animated background */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/5 via-transparent to-cyan-600/5 animate-pulse"></div>
            
            <div className="relative z-10">
              <div className="text-center mb-16">
                <h4 className="text-4xl font-black text-white mb-6 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                  Multi-Agent Enhancement Pipeline
                </h4>
                <p className="text-slate-400 text-xl font-light leading-relaxed max-w-3xl mx-auto">
                  Four specialized AI agents work in perfect harmony to create the ultimate prompt enhancement experience through advanced machine learning and natural language processing
                </p>
              </div>
              
              <div className="grid md:grid-cols-4 gap-10">
                {[
                  { 
                    title: "Intent Classification", 
                    description: "Deep semantic analysis of your prompt's goal, domain expertise, and complexity requirements using advanced NLP models",
                    icon: "🎯",
                    color: "from-purple-500/15 via-purple-600/25 to-purple-700/35",
                    border: "border-purple-500/35",
                    shadow: "hover:shadow-purple-500/15",
                    accent: "purple"
                  },
                  { 
                    title: "Context Research", 
                    description: "Advanced knowledge gathering with domain-specific insights, current best practices, and industry standards",
                    icon: "🔍",
                    color: "from-blue-500/15 via-blue-600/25 to-blue-700/35",
                    border: "border-blue-500/35",
                    shadow: "hover:shadow-blue-500/15",
                    accent: "blue"
                  },
                  { 
                    title: "Best Practices", 
                    description: "Universal optimization techniques and enhancement methodologies for maximum effectiveness and clarity",
                    icon: "⚡",
                    color: "from-cyan-500/15 via-cyan-600/25 to-cyan-700/35",
                    border: "border-cyan-500/35",
                    shadow: "hover:shadow-cyan-500/15",
                    accent: "cyan"
                  },
                  { 
                    title: "Dynamic Enhancement", 
                    description: "Precision-crafted prompt generation with contextual awareness and intelligent optimization algorithms",
                    icon: "✨",
                    color: "from-emerald-500/15 via-emerald-600/25 to-emerald-700/35",
                    border: "border-emerald-500/35",
                    shadow: "hover:shadow-emerald-500/15",
                    accent: "emerald"
                  }
                ].map((step, index) => (
                  <div 
                    key={index} 
                    className={`bg-gradient-to-br ${step.color} border-2 ${step.border} rounded-3xl p-10 text-center hover:scale-105 transition-all duration-700 group backdrop-blur-xl ${step.shadow} hover:shadow-2xl cursor-pointer relative overflow-hidden`}
                    style={{
                      animationDelay: `${index * 200}ms`,
                      animation: 'fadeInUp 1s cubic-bezier(0.4, 0, 0.2, 1) forwards'
                    }}
                  >
                    {/* Subtle hover glow effect */}
                    <div className={`absolute inset-0 bg-gradient-to-br from-${step.accent}-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700`}></div>
                    
                    <div className="relative z-10">
                      <div className="text-6xl mb-8 group-hover:scale-125 transition-transform duration-700 filter drop-shadow-2xl">
                        {step.icon}
                      </div>
                      <h5 className="text-white font-bold mb-6 text-2xl tracking-wide">
                        {step.title}
                      </h5>
                      <p className="text-slate-300 text-sm leading-relaxed font-light">
                        {step.description}
                      </p>
                      <div className={`mt-8 w-full h-1 bg-gradient-to-r from-transparent via-${step.accent}-400/60 to-transparent rounded-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700`}></div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Expert-level footer details */}
              <div className="mt-16 pt-10 border-t border-slate-700/40 flex flex-col md:flex-row items-center justify-between">
                <div className="flex items-center space-x-6 mb-6 md:mb-0">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-500/25">
                    <span className="text-white font-black text-lg">P</span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-base font-semibold">Powered by Advanced AI Intelligence</span>
                    <div className="text-slate-600 text-sm">Next-generation prompt optimization technology</div>
                  </div>
                </div>
                <div className="flex items-center space-x-8 text-xs text-slate-500">
                  <div className="flex items-center space-x-2">
                    <span className="bg-slate-700/40 px-3 py-1 rounded-full border border-slate-600/40">v2.0.0</span>
                    <span className="text-slate-600">•</span>
                    <span>🚀 Production Ready</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>⚡ High Performance</span>
                    <span className="text-slate-600">•</span>
                    <span>🔒 Enterprise Grade</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;