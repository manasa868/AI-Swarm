import React from 'react';
import { GitMerge, Sparkles, Activity } from 'lucide-react';
import { AgentRun } from '../types/project';
import { WorkflowGraph } from '../components/WorkflowGraph';

interface WorkflowPageProps {
  agentRuns: AgentRun[];
  activeAgentId?: string;
  onSelectAgent: (agentId: string) => void;
  projectName?: string;
  projectType?: string;
}

export const WorkflowPage: React.FC<WorkflowPageProps> = ({
  agentRuns,
  activeAgentId,
  onSelectAgent,
  projectName = 'AI Swarm Execution Graph',
  projectType = 'ml',
}) => {
  return (
    <div className="space-y-6 pb-12">
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <GitMerge className="w-5 h-5 text-sky-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">{projectName}</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Live directed acyclic graph (DAG) representing the dynamic agent orchestration pipeline.
            Glowing nodes indicate active execution. Notice the automated error feedback loop between the Testing and Coding agents.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Completed</span>
          </span>
          <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
            <span>Running</span>
          </span>
          <span className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span>Retrying</span>
          </span>
        </div>
      </div>

      <WorkflowGraph
        agentRuns={agentRuns}
        activeAgentId={activeAgentId}
        onSelectAgent={onSelectAgent}
        isLegalWorkflow={projectType === 'legal'}
      />
    </div>
  );
};
