import React from 'react';
import { FlaskConical, AlertCircle, CheckCircle, RotateCcw, ShieldCheck } from 'lucide-react';
import { TestResultData } from '../types/project';
import { TestingConsole } from '../components/TestingConsole';

interface TestingPageProps {
  testResults: TestResultData | null;
  retryCount: number;
  projectStatus: string;
  projectName?: string;
}

export const TestingPage: React.FC<TestingPageProps> = ({
  testResults,
  retryCount,
  projectStatus,
  projectName = 'Current Project',
}) => {
  return (
    <div className="space-y-6 pb-12">
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <FlaskConical className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">
              Test Execution & Self-Correction Engine
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Testing Agent executes isolated unit tests in the sandbox. Any failed assertion triggers an automated repair cycle.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-850 border border-slate-700 text-slate-300">
            Target: {projectName}
          </span>
        </div>
      </div>

      <TestingConsole
        testResults={testResults}
        retryCount={retryCount}
        projectStatus={projectStatus}
      />
    </div>
  );
};
