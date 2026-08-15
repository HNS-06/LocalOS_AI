import React from 'react';
import { ShieldAlert, ShieldCheck, AlertOctagon, Cpu, Network } from 'lucide-react';

export default function SecurityPanel({ anomalies = [], securityWarnings = [] }) {
  return (
    <div className="space-y-6">
      {/* ML Anomalies Section */}
      <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-5 space-y-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Machine Learning Anomaly Detection</h2>
            <p className="text-xs text-gray-400">IsolationForest multi-dimensional resource vector analysis</p>
          </div>
        </div>

        {anomalies.length === 0 ? (
          <div className="p-6 rounded-xl bg-gray-950 border border-gray-800 text-center space-y-2">
            <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto" />
            <p className="text-xs font-semibold text-gray-200">No ML Anomaly Spikes Detected</p>
            <p className="text-[11px] text-gray-500">System vector metrics are operating within normal baseline bounds.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {anomalies.map((anom, i) => (
              <div key={i} className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-purple-300">{anom.title}</h3>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono font-bold">
                    Confidence: {anom.confidence}%
                  </span>
                </div>
                <p className="text-xs text-gray-300 leading-relaxed">{anom.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Process Risk Scoring */}
      <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-5 space-y-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Process Behavior & Risk Scoring</h2>
            <p className="text-xs text-gray-400">Flags suspicious execution paths, parent shell spawns, and unresolvable binaries</p>
          </div>
        </div>

        {securityWarnings.length === 0 ? (
          <div className="p-6 rounded-xl bg-gray-950 border border-gray-800 text-center space-y-2">
            <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto" />
            <p className="text-xs font-semibold text-gray-200">Process Tree Clean</p>
            <p className="text-[11px] text-gray-500">No elevated risk process behaviors detected.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {securityWarnings.map((warn, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-gray-950 border border-gray-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white font-mono">{warn.name} (PID {warn.pid})</span>
                  <span className="text-xs px-2.5 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30">
                    Risk Score: {warn.risk_score}/100
                  </span>
                </div>
                <ul className="text-xs text-gray-400 space-y-1 list-disc list-inside">
                  {warn.reasons.map((r, rIdx) => (
                    <li key={rIdx}>{r}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
