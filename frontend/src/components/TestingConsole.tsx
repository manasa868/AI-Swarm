import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  ShieldAlert,
  ArrowRight,
  Terminal,
  Activity,
  Layers,
  Code
} from 'lucide-react';
import { TestResultData } from '../types/project';

interface TestingConsoleProps {
  testResults: TestResultData | null;
  retryCount: number;
  projectStatus: string;
}

export const TestingConsole: React.FC<TestingConsoleProps> = ({
  testResults,
  retryCount,
  projectStatus,
}) => {
  const isRetrying = projectStatus === 'RETRYING';

  return (
    <div className="space-y-6">
      {/* Header & Flow Banner */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl">
        <h3 className="text-base font-bold text-white mb-2 flex items-center space-x-2">
          <Activity className="w-5 h-5 text-sky-400" />
          <span>Automated Closed-Loop Testing & Defect Remediation</span>
        </h3>
        <p className="text-xs text-slate-400 max-w-2xl mb-6">
          When the Testing Agent detects test failures or assertion mismatches, it generates structured
          tracebacks and routes them directly back to the Coding Agent for automated remediation.
        </p>

        {/* Visual Flow diagram: CODING -> TEST -> ERROR? (YES -> FIX -> RETEST; NO -> REVIEW) */}
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[650px] text-xs">
            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 font-semibold flex items-center gap-2">
              <Code className="w-4 h-4 text-sky-400" />
              <span>CODING AGENT</span>
            </div>

            <ArrowRight className="w-4 h-4 text-slate-600" />

            <div className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 font-semibold flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-400" />
              <span>TESTING AGENT</span>
            </div>

            <ArrowRight className="w-4 h-4 text-slate-600" />

            {/* Error Decision Diamond */}
            <div className={`px-4 py-2 rounded-lg border font-bold text-center ${
              retryCount > 0
                ? 'bg-amber-500/20 border-amber-500 text-amber-300 ring-2 ring-amber-500/30'
                : 'bg-slate-900 border-slate-700 text-slate-300'
            }`}>
              DEFECTS FOUND?
            </div>

            <ArrowRight className="w-4 h-4 text-slate-600" />

            <div className="flex flex-col space-y-2">
              <div className="flex items-center space-x-2 text-[11px] font-semibold text-amber-400">
                <span className="px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/30">YES</span>
                <span>Auto-Fix & Retest Loop (Retry #{retryCount})</span>
              </div>
              <div className="flex items-center space-x-2 text-[11px] font-semibold text-emerald-400">
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/30">NO</span>
                <span>Proceed to Reviewer Agent</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Test Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-xs text-slate-400 block font-medium">Total Test Cases</span>
          <span className="text-2xl font-extrabold text-white mt-1 block">
            {testResults ? testResults.total_tests : 0}
          </span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-emerald-500/30 bg-emerald-950/10">
          <span className="text-xs text-emerald-400 block font-medium flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Passed Assertions</span>
          </span>
          <span className="text-2xl font-extrabold text-emerald-400 mt-1 block">
            {testResults ? testResults.passed : 0}
          </span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-rose-500/30 bg-rose-950/10">
          <span className="text-xs text-rose-400 block font-medium flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Failed Assertions</span>
          </span>
          <span className="text-2xl font-extrabold text-rose-400 mt-1 block">
            {testResults ? testResults.failed : 0}
          </span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-amber-500/30 bg-amber-950/10">
          <span className="text-xs text-amber-400 block font-medium flex items-center gap-1.5">
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Correction Cycles</span>
          </span>
          <span className="text-2xl font-extrabold text-amber-400 mt-1 block">
            {retryCount}
          </span>
        </div>
      </div>

      {/* Raw Output & Traceback Console */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Python Sandbox Runner Output
            </h4>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
            {testResults?.passed_all ? 'ALL PASSED' : isRetrying ? 'RETRY IN PROGRESS' : 'AWAITING TEST'}
          </span>
        </div>

        <pre className="mt-3 p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto max-h-72 whitespace-pre-wrap leading-relaxed">
          {testResults?.raw_output || 'No test execution output yet. Start swarm to execute unit tests.'}
        </pre>
      </div>
    </div>
  );
};
