import React, { useState } from 'react';
import { Search, XCircle, AlertTriangle, ShieldCheck, ArrowUpDown } from 'lucide-react';

export default function ProcessTable({ processes = [], onRequestAction }) {
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('memory_mb');
  const [sortAsc, setSortAsc] = useState(false);

  const filtered = processes.filter(p => 
    p.name.toLowerCase().includes(search.toLowerCase()) || 
    String(p.pid).includes(search) ||
    (p.exe && p.exe.toLowerCase().includes(search.toLowerCase()))
  );

  const sorted = [...filtered].sort((a, b) => {
    let valA = a[sortBy];
    let valB = b[sortBy];
    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();

    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="rounded-2xl bg-gray-900/60 border border-gray-800 p-5 space-y-4 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white">Process Intelligence</h2>
          <p className="text-xs text-gray-400">Real-time process tree & resource consumption monitoring</p>
        </div>

        <div className="relative w-64">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search PID, name, or path..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-950 border border-gray-800 rounded-xl pl-9 pr-4 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-800">
        <table className="w-full text-left text-xs text-gray-300">
          <thead className="bg-gray-950 text-gray-400 uppercase tracking-wider font-semibold border-b border-gray-800">
            <tr>
              <th className="px-4 py-3 cursor-pointer" onClick={() => toggleSort('name')}>
                <div className="flex items-center gap-1">Process Name <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => toggleSort('pid')}>
                <div className="flex items-center gap-1">PID <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => toggleSort('cpu_percent')}>
                <div className="flex items-center gap-1">CPU % <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => toggleSort('memory_mb')}>
                <div className="flex items-center gap-1">Memory (MB) <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60 bg-gray-900/30 font-mono">
            {sorted.slice(0, 50).map((proc) => {
              const isHighCpu = proc.cpu_percent > 15.0;
              const isHighRam = proc.memory_mb > 1000.0;

              return (
                <tr key={proc.pid} className="hover:bg-gray-800/40 transition-colors">
                  <td className="px-4 py-2.5 font-medium text-white font-sans flex items-center gap-2">
                    <span>{proc.name}</span>
                    {proc.exe && (
                      <span className="text-[10px] text-gray-500 font-mono truncate max-w-[200px]" title={proc.exe}>
                        ({proc.exe})
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-gray-400">{proc.pid}</td>
                  <td className="px-4 py-2.5">
                    <span className={`px-2 py-0.5 rounded ${isHighCpu ? 'bg-rose-500/20 text-rose-300 font-bold' : 'text-gray-300'}`}>
                      {proc.cpu_percent}%
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={`px-2 py-0.5 rounded ${isHighRam ? 'bg-amber-500/20 text-amber-300 font-bold' : 'text-gray-300'}`}>
                      {proc.memory_mb} MB
                    </span>
                  </td>
                  <td className="px-4 py-2.5 capitalize text-gray-400 font-sans">{proc.status}</td>
                  <td className="px-4 py-2.5 text-right font-sans">
                    <button
                      onClick={() => onRequestAction({
                        tool_name: 'terminate_process',
                        params: { pid: proc.pid },
                        process_name: proc.name,
                        cpu: proc.cpu_percent,
                        ram: proc.memory_mb,
                        reason: `Process is running with ${proc.cpu_percent}% CPU and ${proc.memory_mb} MB memory.`
                      })}
                      className="px-2.5 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-400 text-[11px] font-medium transition-colors"
                    >
                      Terminate
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
