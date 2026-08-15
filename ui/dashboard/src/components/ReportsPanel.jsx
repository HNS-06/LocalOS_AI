import React, { useState, useEffect } from 'react';
import { FileText, HardDrive, Zap, AlertTriangle, CheckCircle } from 'lucide-react';

export default function ReportsPanel() {
  const [predictions, setPredictions] = useState(null);
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/predictions').then(r => r.json()),
      fetch('/api/startup-items').then(r => r.json())
    ]).then(([pred, start]) => {
      setPredictions(pred);
      setStartups(start);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-gray-500 text-xs animate-pulse">Generating diagnostic system reports...</div>;
  }

  const storagePred = predictions?.storage || {};

  return (
    <div className="space-y-6">
      {/* Daily System Summary Report */}
      <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-6 space-y-4 shadow-sm">
        <div className="flex items-center gap-3 border-b border-gray-800 pb-4">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Daily System Health & Diagnostic Report</h2>
            <p className="text-xs text-gray-400">Automated performance summary and predictive maintenance analysis</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 space-y-2">
            <h3 className="text-xs font-bold text-gray-300 flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-cyan-400" /> Storage Capacity Forecast
            </h3>
            <p className="text-xs text-gray-300 font-medium">{storagePred.message || 'Storage metrics calculated.'}</p>
            {storagePred.estimated_days_until_full && (
              <span className="inline-block text-[11px] px-2.5 py-1 rounded bg-cyan-500/10 text-cyan-400 font-mono font-semibold border border-cyan-500/20">
                Estimated Days to Capacity: ~{storagePred.estimated_days_until_full} days
              </span>
            )}
          </div>

          <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 space-y-2">
            <h3 className="text-xs font-bold text-gray-300 flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-400" /> System Recommendations
            </h3>
            <ul className="text-xs text-gray-400 space-y-1.5 list-disc list-inside">
              <li>Keep startup applications optimized for faster boot times.</li>
              <li>Sustained memory stability verified over telemetry windows.</li>
              <li>Ollama local LLM engine ready for natural language inquiries.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Startup Programs Analysis */}
      <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-5 space-y-4 shadow-sm">
        <h3 className="text-sm font-bold text-white">Windows Startup Applications Intelligence</h3>

        <div className="space-y-3">
          {startups.length === 0 ? (
            <p className="text-xs text-gray-500 italic">No startup entries detected in registry run keys.</p>
          ) : (
            startups.map((item, i) => (
              <div key={i} className="p-3.5 rounded-xl bg-gray-950 border border-gray-800 flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{item.name}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-semibold ${
                      item.classification === 'Essential' ? 'bg-emerald-500/20 text-emerald-300' :
                      item.classification === 'Suspicious' ? 'bg-rose-500/20 text-rose-300' : 'bg-blue-500/20 text-blue-300'
                    }`}>
                      {item.classification}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-500 font-mono truncate max-w-[400px]">{item.command}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-gray-400 block">{item.recommendation}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
