export interface AgentDefinition {
  id: string;
  name: string;
  role: string;
  capabilities: string[];
  workflow: string;
}

export interface AgentMessage {
  id: string;
  from_agent: string;
  to_agent: string;
  message_type: 'TASK_ASSIGNMENT' | 'TASK_RESULT' | 'ERROR' | 'REVIEW' | 'TEST_RESULT' | 'RETRY' | 'FINAL_RESULT';
  task_id?: string;
  content: string;
  data?: Record<string, any>;
  timestamp: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  agent_id?: string;
  agent_name?: string;
  type: string;
  message: string;
  details?: any;
}
