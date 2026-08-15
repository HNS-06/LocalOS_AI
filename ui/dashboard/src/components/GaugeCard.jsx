import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

export default function GaugeCard({ title, icon: Icon, value, unit = '%', subtitle, data = [], color = 'cyan' }) {
  const colorMap = {
    cyan: { stroke: '#06B6D4', fill: 'url(#cyanGrad)', text: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
    blue: { stroke: '#3B82F6', fill: 'url(#blueGrad)', text: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
    emerald: { stroke: '#10B981', fill: 'url(#emeraldGrad)', text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
    amber: { stroke: '#F59E0B', fill: 'url(#amberGrad)', text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
    rose: { stroke: '#F43F5E', fill: 'url(#roseGrad)', text: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20' },
  };

  const currentTheme = colorMap[color] || colorMap.cyan;
  const numericVal = typeof value === 'number' ? value : 0;
  const isHigh = numericVal > 85;

  return (
    <div className="p-5 rounded-2xl bg-gray-900/60 border border-gray-800 flex flex-col justify-between space-y-4 hover:border-gray-700 transition-all shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl ${currentTheme.bg} ${currentTheme.border} border`}>
            <Icon className={`w-5 h-5 ${currentTheme.text}`} />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{title}</h3>
            <p className="text-xs text-gray-500 mt-0.5 truncate max-w-[160px]">{subtitle || 'Live system metric'}</p>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold font-mono ${isHigh ? 'text-rose-400' : 'text-white'}`}>
            {value}{unit}
          </div>
        </div>
      </div>

      {/* Recharts Area Chart */}
      <div className="h-16 w-full pt-1">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="cyanGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#06B6D4" stopOpacity={0.4}/>
                <stop offset="100%" stopColor="#06B6D4" stopOpacity={0.0}/>
              </linearGradient>
              <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.4}/>
                <stop offset="100%" stopColor="#3B82F6" stopOpacity={0.0}/>
              </linearGradient>
              <linearGradient id="emeraldGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10B981" stopOpacity={0.4}/>
                <stop offset="100%" stopColor="#10B981" stopOpacity={0.0}/>
              </linearGradient>
              <linearGradient id="amberGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#F59E0B" stopOpacity={0.4}/>
                <stop offset="100%" stopColor="#F59E0B" stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke={currentTheme.stroke} 
              fill={currentTheme.fill} 
              strokeWidth={2} 
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
