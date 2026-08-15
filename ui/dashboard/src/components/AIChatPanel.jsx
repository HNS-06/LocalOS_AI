import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles, Server, Terminal, ShieldAlert } from 'lucide-react';

export default function AIChatPanel({ onRequestAction }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am **LocalOS AI**, your privacy-first local OS Copilot. I continuously monitor system telemetry, process memory, and anomalies.\n\nAsk me anything about your system performance, active processes, or security events!',
      provider: 'ollama'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState(['qwen2.5', 'llama3.2']);
  const [selectedModel, setSelectedModel] = useState('qwen2.5');
  const [ollamaOnline, setOllamaOnline] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetch('/api/ai/models')
      .then(res => res.json())
      .then(data => {
        if (data.models) setModels(data.models);
        if (data.default) setSelectedModel(data.default);
        setOllamaOnline(data.ollama_online);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const text = queryText || input;
    if (!text.trim() || loading) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, model: selectedModel })
      });
      const data = await res.json();

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.content || 'Unable to generate response.',
        provider: data.provider,
        model: data.model
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Error communicating with LocalOS AI backend API.',
        provider: 'localos_rules'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    "Why is my PC slow?",
    "Which application is consuming the most RAM?",
    "What changed in my system recently?",
    "Are there any suspicious processes running?",
    "Clean temporary system cache"
  ];

  return (
    <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-5 flex flex-col h-[650px] shadow-sm">
      {/* Top Header & Model Selector */}
      <div className="flex items-center justify-between border-b border-gray-800 pb-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
            <Bot className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">AI OS Copilot</h2>
            <p className="text-xs text-gray-400">Natural language OS diagnosis & tool executor</p>
          </div>
        </div>

        {/* Ollama Model Selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 flex items-center gap-1 font-medium">
            <Server className="w-3.5 h-3.5 text-cyan-400" /> Ollama Model:
          </span>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-gray-950 border border-gray-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500/50 font-mono"
          >
            {models.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          return (
            <div key={idx} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {!isUser && (
                <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-cyan-400" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed ${
                isUser
                  ? 'bg-cyan-500 text-white font-medium rounded-tr-none'
                  : 'bg-gray-950 border border-gray-800 text-gray-200 rounded-tl-none space-y-2'
              }`}>
                <div className="whitespace-pre-wrap font-sans">{msg.content}</div>
                
                {!isUser && msg.provider && (
                  <div className="pt-2 border-t border-gray-800/60 text-[10px] text-gray-500 flex items-center justify-between">
                    <span>Provider: <strong className="text-cyan-400">{msg.provider}</strong></span>
                    {msg.model && <span>Model: <strong className="text-gray-400">{msg.model}</strong></span>}
                  </div>
                )}
              </div>
              {isUser && (
                <div className="w-8 h-8 rounded-xl bg-gray-800 border border-gray-700 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-gray-300" />
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shrink-0 animate-pulse">
              <Bot className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="bg-gray-950 border border-gray-800 rounded-2xl p-3 text-xs text-gray-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400 animate-spin" />
              <span>Analyzing OS telemetry & formatting explanation...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Questions */}
      <div className="flex gap-2 overflow-x-auto py-2 border-t border-gray-800/60 my-2">
        {sampleQuestions.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSend(q)}
            className="text-[11px] px-2.5 py-1 rounded-lg bg-gray-800/50 hover:bg-gray-800 border border-gray-700 text-gray-300 whitespace-nowrap transition-colors"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
        <input
          type="text"
          placeholder="Ask LocalOS AI about system resources, memory, or processes..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-white font-medium text-xs flex items-center gap-2 disabled:opacity-50 transition-colors"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Ask</span>
        </button>
      </form>
    </div>
  );
}
