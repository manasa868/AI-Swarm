import React from 'react';
import {
  Compass,
  Cpu,
  Search,
  Code,
  CheckCircle2,
  FileCheck,
  BookOpen,
  ArrowDown,
  RotateCcw,
  Sparkles,
  AlertTriangle,
  Play
} from 'lucide-react';
import { AgentRun } from '../types/project';

interface WorkflowGraphProps {
  agentRuns: AgentRun[];
  activeAgentId?: string;
  onSelectAgent: (agentId: string) => void;
  isLegalWorkflow?: boolean;
}

export const WorkflowGraph: React.FC<WorkflowGraphProps> = ({
  agentRuns,
  activeAgentId,
  onSelectAgent,
  isLegalWorkflow = false,
}) => {
  // Helper to extract status for an agent
  const getAgentStatus = (agentId: string) => {
    const run = agentRuns.find((r) => r.agent_id === agentId);
    return run ? run.status : 'WAITING';
  };

  // Node component
  const NodeCard = ({
    id,
    name,
    role,
    icon: Icon,
    subtitle,
    isLoopback = false,
  }: {
    id: string;
    name: string;
    role: string;
    icon: any;
    subtitle?: string;
    isLoopback?: boolean;
  }) => {
    const status = getAgentStatus(id);
    const isRunning = status === 'RUNNING';
    const isCompleted = status === 'COMPLETED';
    const isRetrying = status === 'RETRYING';
    const isFailed = status === 'FAILED';
    const isSelected = activeAgentId === id;

    return (
      <div
        onClick={() => onSelectAgent(id)}
        className={`relative z-10 w-56 p-3.5 rounded-xl border transition-all cursor-pointer select-none ${
          isRunning
            ? 'bg-slate-900 border-sky-400 ring-4 ring-sky-500/20 shadow-xl shadow-sky-500/30 -translate-y-1'
            : isCompleted
            ? 'bg-slate-900/90 border-emerald-500/50 hover:border-emerald-400'
            : isRetrying
            ? 'bg-slate-900 border-amber-500 ring-2 ring-amber-500/30'
            : isFailed
            ? 'bg-slate-900 border-rose-500'
            : 'bg-slate-900/50 border-slate-800 opacity-70 hover:opacity-100 hover:border-slate-700'
        } ${isSelected ? 'ring-2 ring-sky-400' : ''}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                isRunning
                  ? 'bg-sky-500 text-white shadow-md shadow-sky-500/40 animate-pulse'
                  : isCompleted
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : isRetrying
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'bg-slate-800 text-slate-400'
              }`}
            >
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <h5 className="text-xs font-bold text-white tracking-tight">{name}</h5>
              <p className="text-[10px] text-slate-400 font-mono truncate max-w-[120px]">{role}</p>
            </div>
          </div>

          <div>
            {isRunning && (
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
              </span>
            )}
            {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
            {isRetrying && <RotateCcw className="w-3.5 h-3.5 text-amber-400 animate-spin" />}
            {isFailed && <AlertTriangle className="w-4 h-4 text-rose-400" />}
          </div>
        </div>

        {subtitle && (
          <div className="mt-2 text-[10px] text-slate-400 bg-slate-950/60 px-2 py-1 rounded border border-slate-800/60 truncate font-mono">
            {subtitle}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="relative p-8 rounded-2xl bg-slate-900/40 border border-slate-800 overflow-hidden shadow-2xl">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b08_1px,transparent_1px),linear-gradient(to_bottom,#1e293b08_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      <div className="relative z-10 flex flex-col items-center space-y-8 max-w-4xl mx-auto">
        {/* Step 1: User Task */}
        <div className="flex flex-col items-center">
          <div className="px-5 py-2 rounded-full bg-slate-850 border border-slate-700 text-xs font-semibold text-slate-300 flex items-center space-x-2 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-sky-400" />
            <span>USER TASK SPECIFICATION</span>
          </div>
          <ArrowDown className="w-5 h-5 text-slate-600 mt-2 animate-bounce" />
        </div>

        {/* Step 2: Coordinator */}
        <div className="flex flex-col items-center">
          <NodeCard
            id="coordinator"
            name="Coordinator Agent"
            role="Master Orchestrator"
            icon={Compass}
            subtitle="Analyzes & Decomposes Graph"
          />
          <ArrowDown className="w-5 h-5 text-slate-600 mt-2" />
        </div>

        {/* Step 3: Parallel / Pipeline Layer */}
        {!isLegalWorkflow ? (
          <>
            <div className="w-full flex items-center justify-center">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
                {/* Visual Connector bar */}
                <div className="hidden md:block absolute -top-4 left-16 right-16 h-0.5 bg-gradient-to-r from-sky-500/40 via-indigo-500/40 to-cyan-500/40"></div>
                <NodeCard
                  id="planner"
                  name="Planner Agent"
                  role="Subtask Architect"
                  icon={Cpu}
                  subtitle="Decomposes Subtasks"
                />
                <NodeCard
                  id="researcher"
                  name="Researcher Agent"
                  role="Domain Knowledge"
                  icon={Search}
                  subtitle="Investigates Tech Stack"
                />
                <NodeCard
                  id="coder"
                  name="Coding Agent"
                  role="Software Engineer"
                  icon={Code}
                  subtitle="Synthesizes Codebase"
                />
              </div>
            </div>

            <ArrowDown className="w-5 h-5 text-slate-600" />

            {/* Step 4: Testing & Closed Loop */}
            <div className="relative flex flex-col items-center">
              <NodeCard
                id="tester"
                name="Testing Agent"
                role="QA Sandbox Runner"
                icon={CheckCircle2}
                subtitle="Unit Tests & Bug Detection"
              />

              {/* Loopback indicator */}
              <div className="mt-2 flex items-center space-x-2 text-[10px] text-amber-400 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20 font-mono">
                <RotateCcw className="w-3 h-3 animate-spin" />
                <span>Error Feedback Loop: Tester ⮂ Coder (Auto-Fix)</span>
              </div>

              <ArrowDown className="w-5 h-5 text-slate-600 mt-2" />
            </div>

            {/* Step 5: Reviewer */}
            <div className="flex flex-col items-center">
              <NodeCard
                id="reviewer"
                name="Reviewer Agent"
                role="Quality & Security Audit"
                icon={FileCheck}
                subtitle="Code Quality & Security Sign-off"
              />
              <ArrowDown className="w-5 h-5 text-slate-600 mt-2" />
            </div>

            {/* Step 6: Documentation */}
            <div className="flex flex-col items-center">
              <NodeCard
                id="documenter"
                name="Documentation Agent"
                role="Academic Author"
                icon={BookOpen}
                subtitle="22-Section Academic Report"
              />
              <ArrowDown className="w-5 h-5 text-slate-600 mt-2" />
            </div>
          </>
        ) : (
          /* Transparent Legal AI Pipeline */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl">
            <NodeCard
              id="legal_researcher"
              name="Legal Research Agent"
              role="Statute & Citation Retrieval"
              icon={Search}
              subtitle="Verified Authorities"
            />
            <NodeCard
              id="facts_analyzer"
              name="Facts Analysis Agent"
              role="Facts vs Assumptions"
              icon={Cpu}
              subtitle="Issue Framing"
            />
            <NodeCard
              id="risk_analyzer"
              name="Risk Analysis Agent"
              role="Exposure & Uncertainty"
              icon={AlertTriangle}
              subtitle="Regulatory Flux Matrix"
            />
            <NodeCard
              id="legal_explainer"
              name="Legal Explainer Agent"
              role="Plain Language Communicator"
              icon={BookOpen}
              subtitle="Source-to-Conclusion"
            />
            <div className="md:col-span-2 flex justify-center">
              <NodeCard
                id="legal_reviewer"
                name="Legal Reviewer Agent"
                role="Citation & Disclaimer Audit"
                icon={FileCheck}
                subtitle="Enforces Disclaimers"
              />
            </div>
          </div>
        )}

        {/* Step 7: Final Result */}
        <div className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600/20 to-sky-600/20 border border-emerald-500/40 text-xs font-bold text-emerald-300 flex items-center space-x-2 shadow-lg shadow-emerald-500/10">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>FINAL VALIDATED RESULT & DOWNLOADABLE CODEBASE</span>
        </div>
      </div>
    </div>
  );
};
