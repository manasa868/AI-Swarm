import React from 'react';
import { Layers, Plus, Cpu, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onNewProject: () => void;
  activeProjectName?: string;
  isDemoMode?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onNewProject,
  activeProjectName,
  isDemoMode = true,
}) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 via-indigo-600 to-cyan-400 p-[1px] shadow-lg shadow-sky-500/20">
            <div className="w-full h-full bg-slate-950 rounded-xl flex items-center justify-center">
              <Layers className="w-5 h-5 text-sky-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
                AI Swarm
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  Major Project
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400">From Individual to Intelligent Teams</p>
          </div>
        </div>

        {activeProjectName && (
          <div className="hidden md:flex items-center space-x-2 pl-6 border-l border-slate-800">
            <span className="text-xs text-slate-400 font-medium">Active:</span>
            <span className="text-xs font-semibold text-slate-200 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700">
              {activeProjectName}
            </span>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {/* Transparent Demo/Live Mode Status Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-850 border border-slate-700/60 text-xs">
          <span className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isDemoMode ? 'bg-amber-400' : 'bg-emerald-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${isDemoMode ? 'bg-amber-500' : 'bg-emerald-500'}`}></span>
          </span>
          <span className="text-slate-300 font-medium">
            {isDemoMode ? 'Demo Mode — simulated model response' : 'Live OpenAI GPT-4o'}
          </span>
        </div>

        <button
          onClick={onNewProject}
          className="flex items-center space-x-2 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-md shadow-sky-500/20 active:scale-95"
        >
          <Plus className="w-4 h-4" />
          <span>New Project</span>
        </button>
      </div>
    </header>
  );
};
