import React, { useState, useEffect } from 'react';
import { History, TrendingUp, TrendingDown, AlertCircle, Clock } from 'lucide-react';

export default function WhatChangedPanel() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/what-changed?hours=24')
      .then(res => res.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-gray-500 text-xs animate-pulse">Loading baseline comparison data...</div>;
  }

  const diff = data?.telemetry_diff || {};
  const events = data?.events || [];

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-5 space-y-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">"What Changed?" System Comparison</h2>
            <p className="text-xs text-gray-400">Compares recent 12h telemetry metrics against 24h historical baseline</p>
          </div>
        </div>

        {/* Diff Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 space-y-2">
            <span className="text-xs text-gray-400 font-medium">CPU Utilization Variation</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold font-mono text-white">
                {diff.cpu_diff > 0 ? `+${diff.cpu_diff}%` : `${diff.cpu_diff}%`}
              </span>
              {diff.cpu_diff > 0 ? (
                <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" /> Increased
                </span>
              ) : (
                <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold flex items-center gap-1">
                  <TrendingDown className="w-3 h-3" /> Decreased
                </span>
              )}
            </div>
            <p className="text-[11px] text-gray-500">Comparing earlier period average vs recent system load.</p>
          </div>

          <div className="p-4 rounded-xl bg-gray-950 border border-gray-800 space-y-2">
            <span className="text-xs text-gray-400 font-medium">RAM Footprint Variation</span>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold font-mono text-white">
                {diff.ram_diff > 0 ? `+${diff.ram_diff}%` : `${diff.ram_diff}%`}
              </span>
              {diff.ram_diff > 0 ? (
                <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" /> Increased
                </span>
              ) : (
                <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold flex items-center gap-1">
                  <TrendingDown className="w-3 h-3" /> Stable
                </span>
              )}
            </div>
            <p className="text-[11px] text-gray-500">Memory usage change over time windows.</p>
          </div>
        </div>
      </div>

      {/* System Event Timeline */}
      <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-5 space-y-4 shadow-sm">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" /> Chronological System Timeline
        </h3>

        <div className="space-y-3">
          {events.length === 0 ? (
            <p className="text-xs text-gray-500 italic">No historical timeline events recorded yet.</p>
          ) : (
            events.map((evt, idx) => (
              <div key={idx} className="flex gap-4 p-3 rounded-xl bg-gray-950 border border-gray-800/80 items-start">
                <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs shrink-0 font-mono">
                  {new Date(evt.timestamp * 1000).toLocaleTimeString()}
                </div>
                <div className="space-y-1">
                  <h4 className="text-xs font-bold text-white">{evt.title}</h4>
                  <p className="text-xs text-gray-400">{evt.description}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
