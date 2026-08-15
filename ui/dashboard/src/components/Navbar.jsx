import React from 'react';
import { ShieldCheck, Cpu, Activity, Sparkles, Server } from 'lucide-react';

export default function Navbar({ isConnected, ollamaStatus }) {
  return (
    <header className="h-16 border-b border-gray-800 bg-[#0B0F19]/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Cpu className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-bold text-lg text-white tracking-tight">LocalOS AI</h1>
            <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Copilot v1.0
            </span>
          </div>
          <p className="text-xs text-gray-400">Privacy-First Local AI Systems Copilot</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Ollama Status Pill */}
        <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border ${
          ollamaStatus?.ollama_online 
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
            : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
        }`}>
          <Server className="w-3.5 h-3.5" />
          <span>Ollama: <strong>{ollamaStatus?.ollama_online ? 'Online' : 'Rules Fallback'}</strong></span>
        </div>

        {/* System Protection Pill */}
        <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
          <ShieldCheck className="w-4 h-4" />
          <span className="font-semibold">PROTECTED</span>
        </div>

        {/* Telemetry Stream Connection Indicator */}
        <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-gray-800/80 border border-gray-700 text-gray-300">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span>{isConnected ? 'Live Telemetry' : 'Disconnected'}</span>
        </div>
      </div>
    </header>
  );
}
