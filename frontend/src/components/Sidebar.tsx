import React from 'react';
import {
  Sparkles,
  LayoutDashboard,
  GitMerge,
  FlaskConical,
  Code2,
  Scale,
  BookOpen,
  Network,
  CheckCircle2,
  RefreshCw,
  FolderGit2
} from 'lucide-react';

export type NavTab =
  | 'input'
  | 'dashboard'
  | 'workflow'
  | 'testing'
  | 'results'
  | 'legal'
  | 'documentation'
  | 'uml';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  projectStatus?: string;
  hasLegalAnalysis?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  projectStatus,
  hasLegalAnalysis,
}) => {
  const navItems = [
    {
      id: 'input' as NavTab,
      label: 'Task Input & Setup',
      icon: Sparkles,
      badge: null,
    },
    {
      id: 'dashboard' as NavTab,
      label: 'Swarm Dashboard',
      icon: LayoutDashboard,
      badge: projectStatus === 'RUNNING' ? 'LIVE' : null,
      badgeColor: 'bg-sky-500/20 text-sky-400 border-sky-500/30',
    },
    {
      id: 'workflow' as NavTab,
      label: 'Agent Workflow DAG',
      icon: GitMerge,
      badge: null,
    },
    {
      id: 'testing' as NavTab,
      label: 'Testing & Auto-Fix',
      icon: FlaskConical,
      badge: projectStatus === 'RETRYING' ? 'RETRY' : null,
      badgeColor: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    },
    {
      id: 'results' as NavTab,
      label: 'Code & File Tree',
      icon: Code2,
      badge: projectStatus === 'COMPLETED' ? 'READY' : null,
      badgeColor: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    },
    {
      id: 'legal' as NavTab,
      label: 'Transparent Legal AI',
      icon: Scale,
      badge: 'SPECIAL',
      badgeColor: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    },
    {
      id: 'documentation' as NavTab,
      label: 'Academic Project Docs',
      icon: BookOpen,
      badge: '22 SEC',
      badgeColor: 'bg-slate-700/60 text-slate-300 border-slate-600',
    },
    {
      id: 'uml' as NavTab,
      label: 'Star UML System Design',
      icon: Network,
      badge: 'DIAGRAMS',
      badgeColor: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/40 p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-6">
        <div>
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">
            Navigation
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm shadow-sky-500/10 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold border ${
                        item.badgeColor || 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* College Major Project Footer Info */}
      <div className="p-3 rounded-xl bg-slate-850/80 border border-slate-800 text-xs">
        <p className="font-semibold text-slate-200">College Major Project</p>
        <p className="text-[11px] text-slate-400 mt-0.5">AI Swarm Architecture</p>
        <div className="mt-2.5 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
          <span>Engine v1.0.0</span>
          <span className="text-emerald-400 font-medium">● Local Active</span>
        </div>
      </div>
    </aside>
  );
};
