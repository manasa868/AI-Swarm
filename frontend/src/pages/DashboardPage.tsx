import React from 'react';
import {
  Activity,
  Layers,
  CheckCircle2,
  Clock,
  RotateCcw,
  Sparkles,
  Bot,
  AlertTriangle,
  Play
} from 'lucide-react';
import { Project, AgentRun } from '../types/project';
import { LogEntry } from '../types/agent';
import { AgentCard } from '../components/AgentCard';
import { ActivityLogTimeline } from '../components/ActivityLogTimeline';

interface DashboardPageProps {
  project: Project | null;
  agentRuns: AgentRun[];
  logs: LogEntry[];
  onSelectAgent: (agentId: string) => void;
  onViewWorkflow: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  project,
  agentRuns,
  logs,
  onSelectAgent,
  onViewWorkflow,
}) => {
  if (!project) {
    return (
      <div className="p-12 text-center text-slate-400">
        <Bot className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-300">No Active Swarm Selected</h3>
        <p className="text-xs text-slate-400 mt-1">
          Create a project on the Task Input tab to launch the autonomous AI swarm.
        </p>
      </div>
    );
  }

  // Pre-seed core agent list if runs are still initializing
  const coreAgentDefinitions = [
    { id: 'coordinator', name: 'Coordinator Agent', role: 'Master Workflow Orchestrator' },
    { id: 'planner', name: 'Planner Agent', role: 'Subtask Decomposition Specialist' },
    { id: 'researcher', name: 'Researcher Agent', role: 'Technical Research & Domain Reference' },
    { id: 'coder', name: 'Coding Agent', role: 'Lead Software Engineer' },
    { id: 'tester', name: 'Testing Agent', role: 'Closed-Loop QA Engineer' },
    { id: 'reviewer', name: 'Reviewer Agent', role: 'Quality & Security Auditor' },
    { id: 'documenter', name: 'Documentation Agent', role: 'Academic Documentation Author' },
  ];

  // Merge registered definitions with live run data
  const displayedAgents = coreAgentDefinitions.map((def) => {
    const liveRun = agentRuns.find((r) => r.agent_id === def.id);
    if (liveRun) return liveRun;
    return {
      agent_id: def.id,
      agent_name: def.name,
      role: def.role,
      status: 'WAITING',
      current_task: 'Pending execution schedule...',
      duration_seconds: 0,
      retry_count: 0,
    };
  });

  const completedCount = agentRuns.filter((r) => r.status === 'COMPLETED').length;
  const activeCount = agentRuns.filter((r) => r.status === 'RUNNING').length;
  const isRetrying = project.status === 'RETRYING';

  return (
    <div className="space-y-6 pb-12">
      {/* Top Project Status Card */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-2xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <h2 className="text-xl font-bold text-white tracking-tight">{project.name}</h2>
              <span className="text-[10px] font-mono uppercase px-2.5 py-0.5 rounded-full font-bold bg-sky-500/10 text-sky-400 border border-sky-500/30">
                {project.project_type}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl line-clamp-2">
              {project.description}
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <button
              onClick={onViewWorkflow}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors"
            >
              <Activity className="w-3.5 h-3.5 text-sky-400" />
              <span>Interactive Workflow DAG</span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1.5 pt-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium flex items-center gap-1.5">
              <span>Overall Swarm Progress:</span>
              <span className="text-white font-bold">{Math.round(project.progress)}%</span>
            </span>
            <span className="text-sky-400 font-semibold flex items-center gap-1.5">
              {project.current_agent ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
                  <span>Active: {project.current_agent}</span>
                </>
              ) : project.status === 'COMPLETED' ? (
                <span className="text-emerald-400">All Agents Completed</span>
              ) : (
                <span>Idle</span>
              )}
            </span>
          </div>

          <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                project.status === 'COMPLETED'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                  : isRetrying
                  ? 'bg-gradient-to-r from-amber-500 to-orange-400'
                  : 'bg-gradient-to-r from-sky-500 via-indigo-500 to-cyan-400'
              }`}
              style={{ width: `${Math.max(5, project.progress)}%` }}
            ></div>
          </div>
        </div>

        {/* Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">Status</span>
            <span className="text-xs font-bold text-sky-400 mt-0.5 block">{project.status}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">Active Agents</span>
            <span className="text-xs font-bold text-slate-200 mt-0.5 block">{activeCount} / 7</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">Completed Phases</span>
            <span className="text-xs font-bold text-emerald-400 mt-0.5 block">
              {completedCount} / 7
            </span>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block font-medium">Defect Retries</span>
            <span className="text-xs font-bold text-amber-400 mt-0.5 block">
              {project.retry_count} Cycles
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Agent Cards + Live Activity Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Cards Grid */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Autonomous Team Members
            </h3>
            <span className="text-[11px] text-slate-400">Click any agent to inspect telemetry</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {displayedAgents.map((ag) => (
              <AgentCard
                key={ag.agent_id}
                agent={ag}
                onClick={() => onSelectAgent(ag.agent_id)}
              />
            ))}
          </div>
        </div>

        {/* Live Activity Timeline */}
        <div className="lg:col-span-1">
          <ActivityLogTimeline logs={logs} />
        </div>
      </div>
    </div>
  );
};
