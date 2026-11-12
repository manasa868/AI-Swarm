export type ProjectType = 'ml' | 'web' | 'data_analysis' | 'research' | 'legal' | 'general';

export type ProjectStatus = 'PENDING' | 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'RETRYING' | 'CANCELLED';

export interface Subtask {
  id: string;
  project_id?: string;
  title: string;
  description: string;
  assigned_agent: string;
  dependencies: string[];
  order_index: number;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'RETRYING';
  started_at?: string;
  completed_at?: string;
}

export interface AgentRun {
  id: string;
  project_id: string;
  agent_id: string;
  agent_name: string;
  task_description?: string;
  status: 'WAITING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'RETRYING';
  input_payload: Record<string, any>;
  output_payload: Record<string, any>;
  dependencies: string[];
  error_message?: string;
  retry_count: number;
  started_at?: string;
  completed_at?: string;
  duration_seconds: number;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  project_type: ProjectType;
  technologies: string[];
  status: ProjectStatus;
  progress: number;
  current_agent?: string;
  retry_count: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  execution_summary?: Record<string, any>;
  generated_path?: string;
  tasks?: Subtask[];
  agent_runs?: AgentRun[];
}

export interface FileTreeNode {
  name: string;
  path: string;
  is_dir: boolean;
  size?: number;
  extension?: string;
  children?: FileTreeNode[];
}

export interface TestResultData {
  iteration: number;
  total_tests: number;
  passed: number;
  failed: number;
  skipped: number;
  details: Array<{
    name: string;
    status: string;
    error?: string;
  }>;
  raw_output?: string;
  passed_all: boolean;
}

export interface ReviewData {
  reviewer_agent: string;
  code_quality_score: number;
  security_score: number;
  architecture_score: number;
  approved: boolean;
  summary: string;
  findings: Array<{
    severity: string;
    category: string;
    message: string;
  }>;
  recommendations: string[];
}
