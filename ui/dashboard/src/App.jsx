import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import GaugeCard from './components/GaugeCard';
import ProcessTable from './components/ProcessTable';
import AIChatPanel from './components/AIChatPanel';
import WhatChangedPanel from './components/WhatChangedPanel';
import SecurityPanel from './components/SecurityPanel';
import ReportsPanel from './components/ReportsPanel';
import ActionApprovalModal from './components/ActionApprovalModal';
import { useWebSocket } from './hooks/useWebSocket';

import { Cpu, HardDrive, Network, Zap, Battery, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { data: telemetry, isConnected } = useWebSocket();
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const [actionModalData, setActionModalData] = useState(null);

  // History buffers for live charts
  const [cpuHistory, setCpuHistory] = useState([]);
  const [ramHistory, setRamHistory] = useState([]);
  const [diskHistory, setDiskHistory] = useState([]);
  const [netHistory, setNetHistory] = useState([]);

  useEffect(() => {
    fetch('/api/ai/models')
      .then(res => res.json())
      .then(data => setOllamaStatus(data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (telemetry) {
      const nowStr = new Date().toLocaleTimeString();
      const cpuVal = telemetry.cpu?.total_percent || 0;
      const ramVal = telemetry.memory?.percent || 0;
      const diskVal = telemetry.disk?.percent || 0;
      const netVal = (telemetry.network?.sent_kbps || 0) + (telemetry.network?.recv_kbps || 0);

      setCpuHistory(prev => [...prev.slice(-20), { time: nowStr, value: cpuVal }]);
      setRamHistory(prev => [...prev.slice(-20), { time: nowStr, value: ramVal }]);
      setDiskHistory(prev => [...prev.slice(-20), { time: nowStr, value: diskVal }]);
      setNetHistory(prev => [...prev.slice(-20), { time: nowStr, value: netVal }]);
    }
  }, [telemetry]);

  const cpu = telemetry?.cpu?.total_percent || 0;
  const ram = telemetry?.memory?.percent || 0;
  const ramUsed = telemetry?.memory?.used_gb || 0;
  const disk = telemetry?.disk?.percent || 0;
  const netSent = telemetry?.network?.sent_kbps || 0;
  const netRecv = telemetry?.network?.recv_kbps || 0;
  const gpu = telemetry?.gpu?.utilization || 0;
  const battery = telemetry?.battery?.percent || 100;

  const topCpuProc = telemetry?.processes?.top_cpu_process || 'None';
  const topRamProc = telemetry?.processes?.top_ram_process || 'None';
  const processes = telemetry?.processes?.processes_sample || [];

  return (
    <div className="min-h-screen bg-[#0B0F19] text-gray-100 flex flex-col font-sans">
      <Navbar isConnected={isConnected} ollamaStatus={ollamaStatus} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* TAB 1: DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Gauges Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <GaugeCard
                  title="CPU Utilization"
                  icon={Cpu}
                  value={cpu}
                  unit="%"
                  subtitle={`Top: ${topCpuProc}`}
                  data={cpuHistory}
                  color={cpu > 85 ? 'rose' : 'cyan'}
                />
                <GaugeCard
                  title="Memory (RAM)"
                  icon={Zap}
                  value={ram}
                  unit="%"
                  subtitle={`${ramUsed} GB used (Top: ${topRamProc})`}
                  data={ramHistory}
                  color={ram > 85 ? 'amber' : 'blue'}
                />
                <GaugeCard
                  title="Primary Disk"
                  icon={HardDrive}
                  value={disk}
                  unit="%"
                  subtitle="Primary Volume Usage"
                  data={diskHistory}
                  color="emerald"
                />
                <GaugeCard
                  title="Network I/O"
                  icon={Network}
                  value={Math.round(netSent + netRecv)}
                  unit=" Kbps"
                  subtitle={`Sent: ${netSent} | Recv: ${netRecv}`}
                  data={netHistory}
                  color="amber"
                />
              </div>

              {/* Active Process List Overview */}
              <ProcessTable processes={processes} onRequestAction={(data) => setActionModalData(data)} />
            </div>
          )}

          {/* TAB 2: PROCESS INTELLIGENCE */}
          {activeTab === 'processes' && (
            <ProcessTable processes={processes} onRequestAction={(data) => setActionModalData(data)} />
          )}

          {/* TAB 3: AI OS COPILOT */}
          {activeTab === 'chat' && (
            <AIChatPanel onRequestAction={(data) => setActionModalData(data)} />
          )}

          {/* TAB 4: WHAT CHANGED? */}
          {activeTab === 'changed' && (
            <WhatChangedPanel />
          )}

          {/* TAB 5: SECURITY & ANOMALIES */}
          {activeTab === 'security' && (
            <SecurityPanel />
          )}

          {/* TAB 6: SYSTEM REPORTS */}
          {activeTab === 'reports' && (
            <ReportsPanel />
          )}
        </main>
      </div>

      {/* Action Confirmation Modal */}
      <ActionApprovalModal
        actionData={actionModalData}
        onClose={() => setActionModalData(null)}
        onActionComplete={() => setActionModalData(null)}
      />
    </div>
  );
}
