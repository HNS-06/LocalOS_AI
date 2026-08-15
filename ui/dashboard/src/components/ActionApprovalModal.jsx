import React, { useState } from 'react';
import { AlertTriangle, ShieldCheck, CheckCircle2, XCircle } from 'lucide-react';

export default function ActionApprovalModal({ actionData, onClose, onActionComplete }) {
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  if (!actionData) return null;

  const handleConfirm = async () => {
    setSubmitting(true);
    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: actionData.tool_name,
          params: actionData.params,
          user_approved: true,
          user_query: actionData.reason || 'User confirmed via UI action modal'
        })
      });
      const data = await res.json();
      setResult(data);
      if (onActionComplete) onActionComplete(data);
    } catch (e) {
      setResult({ success: False, message: 'Failed to execute requested action.' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl">
        <div className="flex items-center gap-3 border-b border-gray-800 pb-4">
          <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Action Approval Required</h3>
            <p className="text-xs text-gray-400">LocalOS AI Action Security Engine</p>
          </div>
        </div>

        {result ? (
          <div className="space-y-4">
            <div className={`p-4 rounded-xl text-xs border ${
              result.success 
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' 
                : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
            }`}>
              <p className="font-bold flex items-center gap-2 mb-1">
                {result.success ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                {result.success ? 'Action Executed Successfully' : 'Action Failed'}
              </p>
              <p className="font-mono text-[11px]">{result.message}</p>
            </div>
            <button
              onClick={onClose}
              className="w-full py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-medium text-xs transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          <>
            <div className="space-y-3 bg-gray-950 p-4 rounded-xl border border-gray-800/80 text-xs">
              <div className="flex justify-between text-gray-400">
                <span>Action:</span>
                <strong className="text-white font-mono">{actionData.tool_name}</strong>
              </div>
              {actionData.process_name && (
                <div className="flex justify-between text-gray-400">
                  <span>Target Process:</span>
                  <strong className="text-cyan-400 font-mono">{actionData.process_name} (PID {actionData.params?.pid})</strong>
                </div>
              )}
              {actionData.cpu !== undefined && (
                <div className="flex justify-between text-gray-400">
                  <span>Resource Impact:</span>
                  <span className="text-rose-400 font-mono font-bold">{actionData.cpu}% CPU, {actionData.ram} MB RAM</span>
                </div>
              )}
              <div className="pt-2 border-t border-gray-800/80 text-gray-400">
                <span className="block mb-1 text-[11px] uppercase tracking-wider font-semibold text-gray-500">Reason / Diagnosis:</span>
                <p className="text-gray-300 italic">{actionData.reason}</p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={onClose}
                disabled={submitting}
                className="flex-1 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium text-xs transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={submitting}
                className="flex-1 py-2.5 rounded-xl bg-rose-500 hover:bg-rose-400 text-white font-semibold text-xs flex items-center justify-center gap-2 transition-colors shadow-lg shadow-rose-500/20"
              >
                {submitting ? 'Executing...' : 'Approve & Execute'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
