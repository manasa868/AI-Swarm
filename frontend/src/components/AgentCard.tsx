import React from 'react';
import {
  Clock,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  ChevronRight,
  Sparkles,
  Bot
} from 'lucide-react';
import { AgentRun } from '../types/project';

interface AgentCardProps {
  agent: AgentRun | {
    agent_id: string;
    agent_name: string;
    role?: string;
    status: string;
    current_task?: string;
    duration_seconds?: number;
    retry_count?: number;
    dependencies?: string[];
  };
  onClick: () => void;
  isActive?: boolean;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onClick, isActive }) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'RUNNING':
        return (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-sky-500/20 text-sky-400 border border-sky-500/40 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-ping"></span>
            <span>RUNNING</span>
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" />
            <span>COMPLETED</span>
          </span>
        );
      case 'RETRYING':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40 animate-pulse">
            <RotateCcw className="w-3 h-3 animate-spin" />
            <span>RETRYING</span>
          </span>
        );
      case 'FAILED':
        return (
          <span className="flex items-center space-x-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
            <AlertTriangle className="w-3 h-3" />
            <span>FAILED</span>
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700">
            WAITING
          </span>
        );
    }
  };

  return (
    <div
      onClick={onClick}
      className={`group relative p-4 rounded-xl border transition-all cursor-pointer select-none ${
        isActive
          ? 'bg-slate-800/90 border-sky-500 ring-2 ring-sky-500/30 shadow-lg shadow-sky-500/10'
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-850/80 shadow-md'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div
            className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
              agent.status === 'RUNNING'
                ? 'bg-sky-500/20 text-sky-400 border border-sky-500/40'
                : agent.status === 'COMPLETED'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                : 'bg-slate-800 text-slate-400 border border-slate-700'
            }`}
          >
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white group-hover:text-sky-300 transition-colors">
              {agent.agent_name}
            </h4>
            <p className="text-[11px] text-slate-400 font-mono">
              {'role' in agent ? agent.role : agent.agent_id}
            </p>
          </div>
        </div>

        {getStatusBadge(agent.status)}
      </div>

      <div className="mt-3 text-xs text-slate-300 line-clamp-2 bg-slate-950/40 p-2 rounded-lg border border-slate-800/80 font-sans">
        {'task_description' in agent ? agent.task_description : ('current_task' in agent ? agent.current_task : 'Awaiting assignment...')}
      </div>

      <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-slate-400" />
            <span>{(agent.duration_seconds || 0).toFixed(1)}s</span>
          </span>
          {(agent.retry_count || 0) > 0 && (
            <span className="flex items-center space-x-1 text-amber-400 font-semibold">
              <RotateCcw className="w-3 h-3" />
              <span>Retry #{agent.retry_count}</span>
            </span>
          )}
        </div>
        <span className="text-slate-400 group-hover:text-sky-400 flex items-center text-[10px] font-semibold transition-colors">
          Inspect <ChevronRight className="w-3 h-3 ml-0.5" />
        </span>
      </div>
    </div>
  );
};
