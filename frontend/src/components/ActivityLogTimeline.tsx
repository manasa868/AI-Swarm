import React, { useState } from 'react';
import { Terminal, Clock, Filter, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { LogEntry } from '../types/agent';

interface ActivityLogTimelineProps {
  logs: LogEntry[];
}

export const ActivityLogTimeline: React.FC<ActivityLogTimelineProps> = ({ logs }) => {
  const [filter, setFilter] = useState<'all' | 'error' | 'agent'>('all');

  const filteredLogs = logs.filter((log) => {
    if (filter === 'error') return log.type.includes('fail') || log.type.includes('error');
    if (filter === 'agent') return log.type.includes('agent');
    return true;
  });

  return (
    <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5 flex flex-col h-full shadow-lg">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-sky-400" />
          <h3 className="text-xs font-bold text-white tracking-wide uppercase">
            Live Activity Log & Telemetry
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
            {logs.length} events
          </span>
        </div>

        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => setFilter('all')}
            className={`px-2 py-1 rounded text-[10px] font-medium transition-colors ${
              filter === 'all'
                ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('agent')}
            className={`px-2 py-1 rounded text-[10px] font-medium transition-colors ${
              filter === 'agent'
                ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Agents
          </button>
          <button
            onClick={() => setFilter('error')}
            className={`px-2 py-1 rounded text-[10px] font-medium transition-colors ${
              filter === 'error'
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Errors
          </button>
        </div>
      </div>

      <div className="mt-3 overflow-y-auto flex-1 space-y-2 pr-1 font-mono text-[11px] max-h-96">
        {filteredLogs.length === 0 ? (
          <div className="p-8 text-center text-slate-400 font-sans text-xs">
            No events logged yet. Launch swarm to observe live activity.
          </div>
        ) : (
          filteredLogs.map((log) => {
            const isError = log.type.includes('fail') || log.type.includes('error');
            const isCompleted = log.type.includes('complete');
            const isStarted = log.type.includes('start');

            return (
              <div
                key={log.id}
                className={`p-2.5 rounded-lg border transition-all flex items-start space-x-2.5 ${
                  isError
                    ? 'bg-rose-950/20 border-rose-500/30 text-rose-300'
                    : isCompleted
                    ? 'bg-emerald-950/20 border-emerald-500/20 text-emerald-300'
                    : isStarted
                    ? 'bg-sky-950/20 border-sky-500/20 text-sky-300'
                    : 'bg-slate-950/40 border-slate-800 text-slate-300'
                }`}
              >
                <div className="shrink-0 mt-0.5">
                  {isError ? (
                    <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                  ) : isCompleted ? (
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                    <span className="font-semibold text-slate-300">
                      {log.agent_name || 'System Orchestrator'}
                    </span>
                    <span>{log.timestamp}</span>
                  </div>
                  <p className="text-slate-200 break-words">{log.message}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
