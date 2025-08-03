import React, { useState } from "react";
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

  const handleEnhance = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt to enhance");
      return;
    }

    setIsLoading(true);
    setError("");
    setEnhancedPrompt("");
    setIntentAnalysis(null);

    try {
      const response = await axios.post(`${API}/enhance`, { prompt });
      setEnhancedPrompt(response.data.enhanced_prompt);
      setIntentAnalysis(response.data.agent_results.intent_analysis);
    } catch (err) {
      console.error("Enhancement error:", err);
      setError(
        err.response?.data?.detail || 
        "Failed to enhance prompt. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(enhancedPrompt);
    alert("Enhanced prompt copied to clipboard!");
  };

  const handleClear = () => {
    setPrompt("");
    setEnhancedPrompt("");
    setError("");
    setIntentAnalysis(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20"></div>
        <div className="relative px-6 py-12 text-center">
          <div className="mx-auto max-w-4xl">
            <h1 className="text-5xl md:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 mb-6">
              Pehance
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 leading-relaxed">
              Transform any prompt into a precision-crafted masterpiece using our 
              <span className="text-purple-400 font-semibold"> AI-powered multi-agent system</span>
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-400">
              <div className="flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>Intent Classification</span>
              </div>
              <div className="flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span>Context Research</span>
              </div>
              <div className="flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                <span>Best Practices</span>
              </div>
              <div className="flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                <span>Dynamic Enhancement</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 pb-12">
        <div className="mx-auto max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-8">
            
            {/* Input Section */}
            <div className="space-y-6">
              <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
                <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                  <span className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center mr-3 text-sm font-bold">
                    1
                  </span>
                  Your Original Prompt
                </h2>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter any prompt you want to enhance... 

Examples:
• Write a story about a robot
• Help me build a todo app
• Create a marketing strategy
• Explain quantum physics"
                  className="w-full h-48 bg-slate-900/50 border border-slate-600/50 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                />
                
                <div className="flex flex-wrap gap-3 mt-4">
                  <button
                    onClick={handleEnhance}
                    disabled={isLoading || !prompt.trim()}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-purple-500/25"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Enhancing...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        <span>Enhance Prompt</span>
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={handleClear}
                    className="bg-slate-700/50 hover:bg-slate-600/50 text-gray-300 font-medium py-3 px-6 rounded-xl transition-all duration-200"
                  >
                    Clear
                  </button>
                </div>

                {error && (
                  <div className="mt-4 p-4 bg-red-900/20 border border-red-500/30 rounded-xl text-red-400 text-sm">
                    {error}
                  </div>
                )}
              </div>

              {/* Intent Analysis */}
              {intentAnalysis && (
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Analysis Results
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Intent</div>
                      <div className="text-purple-400 font-medium capitalize">
                        {intentAnalysis.intent_category}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Confidence</div>
                      <div className="text-green-400 font-medium">
                        {Math.round(intentAnalysis.confidence * 100)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Domain</div>
                      <div className="text-blue-400 font-medium capitalize">
                        {intentAnalysis.specific_domain || 'General'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 uppercase tracking-wide">Complexity</div>
                      <div className="text-yellow-400 font-medium capitalize">
                        {intentAnalysis.complexity_level}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Output Section */}
            <div className="space-y-6">
              {enhancedPrompt ? (
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
                  <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                    <span className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center mr-3 text-sm font-bold">
                      ✓
                    </span>
                    Enhanced Prompt
                  </h2>
                  <div className="bg-slate-900/50 border border-slate-600/50 rounded-xl p-4 max-h-96 overflow-y-auto">
                    <pre className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap font-mono">
                      {enhancedPrompt}
                    </pre>
                  </div>
                  <div className="flex gap-3 mt-4">
                    <button
                      onClick={handleCopy}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <span>Copy to Clipboard</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
                  <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
                    <span className="w-8 h-8 bg-gray-500 rounded-lg flex items-center justify-center mr-3 text-sm font-bold">
                      2
                    </span>
                    Enhanced Prompt
                  </h2>
                  <div className="bg-slate-900/50 border border-slate-600/50 rounded-xl p-8 text-center">
                    <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <p className="text-gray-500">Your enhanced prompt will appear here</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 pb-8">
        <div className="mx-auto max-w-4xl text-center">
          <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/30 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">How Pehance Works</h3>
            <div className="grid md:grid-cols-4 gap-4 text-sm">
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mx-auto mb-2">
                  <span className="text-purple-400 font-bold">1</span>
                </div>
                <div className="text-purple-400 font-medium mb-1">Intent Classification</div>
                <div className="text-gray-400">Analyzes your prompt's goal and complexity</div>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mx-auto mb-2">
                  <span className="text-blue-400 font-bold">2</span>
                </div>
                <div className="text-blue-400 font-medium mb-1">Context Research</div>
                <div className="text-gray-400">Gathers domain-specific knowledge</div>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center mx-auto mb-2">
                  <span className="text-green-400 font-bold">3</span>
                </div>
                <div className="text-green-400 font-medium mb-1">Best Practices</div>
                <div className="text-gray-400">Applies optimization techniques</div>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-yellow-500/20 rounded-xl flex items-center justify-center mx-auto mb-2">
                  <span className="text-yellow-400 font-bold">4</span>
                </div>
                <div className="text-yellow-400 font-medium mb-1">Enhancement</div>
                <div className="text-gray-400">Creates precision-crafted prompts</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
