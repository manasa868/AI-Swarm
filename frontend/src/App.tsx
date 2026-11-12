import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar, NavTab } from './components/Sidebar';
import { AgentDetailModal } from './components/AgentDetailModal';
import { StarUmlViewer } from './components/StarUmlViewer';
import { ProjectInputPage } from './pages/ProjectInputPage';
import { DashboardPage } from './pages/DashboardPage';
import { WorkflowPage } from './pages/WorkflowPage';
import { TestingPage } from './pages/TestingPage';
import { ResultsPage } from './pages/ResultsPage';
import { TransparentLegalAIPage } from './pages/TransparentLegalAIPage';
import { DocumentationViewer } from './components/DocumentationViewer';

import { Project, AgentRun, FileTreeNode, TestResultData, ReviewData, ProjectType } from './types/project';
import { LogEntry } from './types/agent';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('input');
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [agentRuns, setAgentRuns] = useState<AgentRun[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AgentRun | null>(null);
  const [fileTree, setFileTree] = useState<FileTreeNode[]>([]);
  const [testResults, setTestResults] = useState<TestResultData | null>(null);
  const [reviewData, setReviewData] = useState<ReviewData | null>(null);
  const [documentation, setDocumentation] = useState<{
    title: string;
    content_markdown: string;
    sections: Record<string, string>;
  } | null>(null);

  const [isDemoMode, setIsDemoMode] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Check backend health on mount
  useEffect(() => {
    api.getHealth()
      .then((h) => setIsDemoMode(h.demo_mode))
      .catch(() => setIsDemoMode(true));
  }, []);

  const addLog = (type: string, message: string, agentName?: string, agentId?: string) => {
    const timeStr = new Date().toLocaleTimeString('en-US', { hour12: false });
    const newEntry: LogEntry = {
      id: `log_${Date.now()}_${Math.random()}`,
      timestamp: timeStr,
      type,
      message,
      agent_name: agentName,
      agent_id: agentId,
    };
    setLogs((prev) => [newEntry, ...prev]);
  };

  const handleStartSwarm = async (projectData: {
    name: string;
    description: string;
    project_type: ProjectType;
    technologies: string[];
  }) => {
    setIsLoading(true);
    setLogs([]);
    setAgentRuns([]);
    setFileTree([]);
    setTestResults(null);
    setReviewData(null);
    setDocumentation(null);

    try {
      // 1. Create project on backend
      const proj = await api.createProject(projectData);
      setActiveProject(proj);
      setCurrentTab('dashboard');
      setIsLoading(false);

      addLog('system_start', `Coordinator initialized project '${proj.name}'`, 'Coordinator Agent', 'coordinator');

      // 2. Open Server-Sent Events stream for live telemetry
      const eventSource = new EventSource(`/api/projects/${proj.id}/stream`);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'project_status') {
            setActiveProject((prev) => prev ? {
              ...prev,
              status: data.status,
              progress: data.progress,
              current_agent: data.current_agent,
            } : null);
            addLog('status_update', data.message || `Swarm state: ${data.status}`);
          } else if (data.type === 'agent_started') {
            setActiveProject((prev) => prev ? {
              ...prev,
              current_agent: data.agent_name,
              progress: typeof data.progress === 'number' ? data.progress : prev.progress,
            } : null);

            setAgentRuns((prev) => {
              const existing = prev.filter((r) => r.agent_id !== data.agent_id);
              const newRun: AgentRun = {
                id: `run_${Date.now()}`,
                project_id: proj.id,
                agent_id: data.agent_id,
                agent_name: data.agent_name,
                task_description: data.task,
                status: 'RUNNING',
                input_payload: {},
                output_payload: {},
                dependencies: [],
                retry_count: 0,
                duration_seconds: 0,
                started_at: data.timestamp,
              };
              return [...existing, newRun];
            });

            addLog('agent_start', data.task, data.agent_name, data.agent_id);
          } else if (data.type === 'agent_completed') {
            setAgentRuns((prev) =>
              prev.map((r) =>
                r.agent_id === data.agent_id
                  ? {
                      ...r,
                      status: 'COMPLETED',
                      output_payload: data.output || {},
                      duration_seconds: r.started_at
                        ? Math.max(0, (new Date(data.timestamp).getTime() - new Date(r.started_at).getTime()) / 1000)
                        : r.duration_seconds,
                      completed_at: data.timestamp,
                    }
                  : r
              )
            );

            // If tester completed, capture test results
            if (data.agent_id === 'tester' && data.output) {
              setTestResults({
                iteration: data.output.iteration || 1,
                total_tests: data.output.total_tests || 0,
                passed: data.output.passed || 0,
                failed: data.output.failed || 0,
                skipped: data.output.skipped || 0,
                details: data.output.details || [],
                raw_output: data.output.raw_output || '',
                passed_all: data.output.passed_all ?? false,
              });
            }

            // If reviewer completed, capture review data
            if (data.agent_id === 'reviewer' && data.output) {
              setReviewData({
                reviewer_agent: 'Reviewer Agent',
                code_quality_score: data.output.code_quality_score,
                security_score: data.output.security_score,
                architecture_score: data.output.architecture_score,
                approved: data.output.approved,
                summary: data.output.summary,
                findings: data.output.findings || [],
                recommendations: data.output.recommendations || [],
              });
            }

            addLog('agent_complete', data.summary || `${data.agent_name} finished task.`, data.agent_name, data.agent_id);
          } else if (data.type === 'test_failure_detected') {
            setActiveProject((prev) => prev ? { ...prev, status: 'RETRYING', retry_count: (prev.retry_count || 0) + 1 } : null);
            setAgentRuns((prev) =>
              prev.map((r) =>
                r.agent_id === 'coder' || r.agent_id === 'tester'
                  ? { ...r, status: 'RETRYING', retry_count: (r.retry_count || 0) + 1 }
                  : r
              )
            );
            addLog('test_fail', data.message || 'Defects identified. Automated remediation triggered.', 'Testing Agent', 'tester');
          } else if (data.type === 'diagrams_generating') {
            addLog('agent_start', data.message || 'Analyzing source code for UML diagrams.', 'UML Diagram Generator', 'uml');
          } else if (data.type === 'diagrams_generated') {
            addLog('agent_complete', data.message || 'Project UML diagrams are ready.', 'UML Diagram Generator', 'uml');
          } else if (data.type === 'workflow_completed') {
            eventSource.close();
            setActiveProject((prev) => prev ? {
              ...prev,
              status: 'COMPLETED',
              progress: 100.0,
              current_agent: undefined,
              execution_summary: data.execution_summary,
            } : null);

            if (data.file_tree) setFileTree(data.file_tree);
            if (data.documentation) {
              setDocumentation({
                title: data.documentation.document_title,
                content_markdown: data.documentation.markdown_content,
                sections: data.documentation.sections,
              });
            }

            addLog('system_complete', 'AI Swarm execution completed successfully. Deliverable generated.', 'Coordinator Agent', 'coordinator');
          } else if (data.type === 'workflow_failed') {
            eventSource.close();
            setActiveProject((prev) => prev ? {
              ...prev,
              status: 'FAILED',
              progress: data.progress ?? prev.progress,
              retry_count: data.retry_count ?? prev.retry_count,
              current_agent: undefined,
              error_message: data.message,
            } : null);
            if (data.test_results) {
              setTestResults({
                iteration: data.test_results.iteration || 1,
                total_tests: data.test_results.total_tests || 0,
                passed: data.test_results.passed || 0,
                failed: data.test_results.failed || 0,
                skipped: data.test_results.skipped || 0,
                details: data.test_results.details || [],
                raw_output: data.test_results.raw_output || '',
                passed_all: data.test_results.passed_all ?? false,
              });
            }
            addLog('system_error', data.message || 'The swarm could not complete its test suite.');
          } else if (data.type === 'error') {
            eventSource.close();
            setActiveProject((prev) => prev ? {
              ...prev,
              status: 'FAILED',
              current_agent: undefined,
              error_message: data.message || 'Workflow error occurred.',
            } : null);
            addLog('system_error', data.message || 'Workflow error occurred.');
          }
        } catch (err) {
          console.error('Error handling SSE event:', err);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        addLog('system_error', 'The live workflow connection was interrupted.');
        setActiveProject((prev) => {
          if (!prev || !['RUNNING', 'RETRYING'].includes(prev.status)) return prev;
          return {
            ...prev,
            status: 'FAILED',
            current_agent: undefined,
            error_message: 'The live workflow connection was interrupted.',
          };
        });
      };
    } catch (err: any) {
      setIsLoading(false);
      alert(`Failed to launch swarm: ${err.message}`);
    }
  };

  const handleSelectAgentById = (agentId: string) => {
    const found = agentRuns.find((r) => r.agent_id === agentId);
    if (found) {
      setSelectedAgent(found);
    } else {
      // Create mockup run for un-started agent
      setSelectedAgent({
        id: `mock_${agentId}`,
        project_id: activeProject?.id || '',
        agent_id: agentId,
        agent_name: `${agentId.charAt(0).toUpperCase() + agentId.slice(1)} Agent`,
        task_description: 'Awaiting pipeline dispatch...',
        status: 'WAITING',
        input_payload: {},
        output_payload: {},
        dependencies: [],
        retry_count: 0,
        duration_seconds: 0,
      });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
      {/* Top Header */}
      <Header
        onNewProject={() => setCurrentTab('input')}
        activeProjectName={activeProject?.name}
        isDemoMode={isDemoMode}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          projectStatus={activeProject?.status}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-8 bg-slate-950/60">
          {currentTab === 'input' && (
            <ProjectInputPage onStartSwarm={handleStartSwarm} isLoading={isLoading} />
          )}

          {currentTab === 'dashboard' && (
            <DashboardPage
              project={activeProject}
              agentRuns={agentRuns}
              logs={logs}
              onSelectAgent={handleSelectAgentById}
              onViewWorkflow={() => setCurrentTab('workflow')}
            />
          )}

          {currentTab === 'workflow' && (
            <WorkflowPage
              agentRuns={agentRuns}
              activeAgentId={activeProject?.current_agent}
              onSelectAgent={handleSelectAgentById}
              projectName={activeProject?.name}
              projectType={activeProject?.project_type}
            />
          )}

          {currentTab === 'testing' && (
            <TestingPage
              testResults={testResults}
              retryCount={activeProject?.retry_count || 0}
              projectStatus={activeProject?.status || 'PENDING'}
              projectName={activeProject?.name}
            />
          )}

          {currentTab === 'results' && (
            <ResultsPage
              project={activeProject}
              fileTree={fileTree}
              reviewData={reviewData}
              testResults={testResults}
              documentation={documentation}
              onRunAgain={() => setCurrentTab('input')}
              onGoToDocumentation={() => setCurrentTab('documentation')}
              onGoToTesting={() => setCurrentTab('testing')}
            />
          )}

          {currentTab === 'legal' && <TransparentLegalAIPage />}

          {currentTab === 'documentation' && (
            <div className="max-w-5xl mx-auto">
              {documentation ? (
                <DocumentationViewer
                  title={documentation.title}
                  markdownContent={documentation.content_markdown}
                  sections={documentation.sections}
                />
              ) : (
                <div className="p-16 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
                  <p className="text-sm font-semibold text-slate-300">Documentation Not Yet Generated</p>
                  <p className="text-xs text-slate-400 mt-1">
                    Execute a project swarm to observe the Documentation Agent compile 22 academic sections dynamically.
                  </p>
                </div>
              )}
            </div>
          )}

          {currentTab === 'uml' && (
            <div className="max-w-5xl mx-auto">
              <StarUmlViewer projectId={activeProject?.id} />
            </div>
          )}
        </main>
      </div>

      {/* Agent Deep Inspection Modal */}
      {selectedAgent && (
        <AgentDetailModal
          agent={selectedAgent}
          onClose={() => setSelectedAgent(null)}
        />
      )}
    </div>
  );
};

export default App;
