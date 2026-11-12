import React from 'react';
import {
  X,
  Bot,
  Clock,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Database,
  Cpu,
  Layers,
  Terminal
} from 'lucide-react';
import { AgentRun } from '../types/project';

interface AgentDetailModalProps {
  agent: AgentRun | null;
  onClose: () => void;
}

export const AgentDetailModal: React.FC<AgentDetailModalProps> = ({ agent, onClose }) => {
  if (!agent) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-850/60">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">{agent.agent_name}</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {agent.agent_id}
                </span>
              </div>
              <p className="text-xs text-slate-400">{agent.task_description || 'Active Autonomous Agent'}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-medium">Status</span>
              <span className="text-xs font-bold text-sky-400 flex items-center gap-1.5 mt-0.5">
                {agent.status}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-medium">Execution Duration</span>
              <span className="text-xs font-bold text-slate-200 flex items-center gap-1 mt-0.5">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                {(agent.duration_seconds || 0).toFixed(2)}s
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-medium">Retry Attempts</span>
              <span className="text-xs font-bold text-amber-400 flex items-center gap-1 mt-0.5">
                <RotateCcw className="w-3.5 h-3.5" />
                {agent.retry_count || 0}
              </span>
            </div>
          </div>

          {/* Error Banner if any */}
          {agent.error_message && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start space-x-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold block">Failure Diagnostics:</span>
                <span className="font-mono text-[11px]">{agent.error_message}</span>
              </div>
            </div>
          )}

          {/* Dependencies */}
          {agent.dependencies && agent.dependencies.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-2">
                <Layers className="w-3.5 h-3.5 text-sky-400" />
                <span>Task Dependencies</span>
              </h4>
              <div className="flex flex-wrap gap-2">
                {agent.dependencies.map((dep, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700"
                  >
                    {dep}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Input Payload */}
          <div>
            <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-2">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>Input Context & Prompt Payload</span>
            </h4>
            <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-36">
              {JSON.stringify(agent.input_payload || {}, null, 2)}
            </pre>
          </div>

          {/* Output Payload */}
          <div>
            <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-2">
              <Terminal className="w-3.5 h-3.5 text-emerald-400" />
              <span>Generated Output Artifact</span>
            </h4>
            <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-emerald-300/90 overflow-x-auto max-h-48">
              {JSON.stringify(agent.output_payload || {}, null, 2)}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
