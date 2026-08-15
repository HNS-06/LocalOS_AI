import React from 'react';
import { 
  LayoutDashboard, 
  Cpu, 
  Bot, 
  History, 
  ShieldAlert, 
  FileText, 
  Settings 
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'processes', label: 'Process Intelligence', icon: Cpu },
    { id: 'chat', label: 'AI OS Copilot', icon: Bot, badge: 'Ollama' },
    { id: 'changed', label: 'What Changed?', icon: History },
    { id: 'security', label: 'Security & Anomalies', icon: ShieldAlert },
    { id: 'reports', label: 'System Reports', icon: FileText },
  ];

  return (
    <aside className="w-64 border-r border-gray-800 bg-[#0B0F19] p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-6">
        <div className="px-3">
          <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Navigation</span>
        </div>
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-gray-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 font-semibold border border-blue-500/30">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="p-3 rounded-xl bg-gray-900/60 border border-gray-800 text-xs text-gray-400 space-y-2">
        <div className="flex items-center justify-between font-medium text-gray-300">
          <span>Engine Status</span>
          <span className="text-emerald-400">Active</span>
        </div>
        <p className="text-[11px] text-gray-500 leading-relaxed">
          Deterministic rules + ML IsolationForest + Ollama natural language context.
        </p>
      </div>
    </aside>
  );
}
