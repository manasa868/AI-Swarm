import { Project, FileTreeNode } from '../types/project';
import { LegalAnalysisResult, LegalSource } from '../types/legal';

const API_BASE = '/api';

export interface ProjectDiagram {
  id: string;
  title: string;
  description: string;
  svg_url: string;
  export_url: string;
  classes: string[];
  source_files: string[];
}

interface ProjectDiagramsResponse {
  project_id: string;
  diagrams: ProjectDiagram[];
}

async function errorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const body = await response.json();
    return typeof body.detail === 'string' ? body.detail : fallback;
  } catch {
    return fallback;
  }
}

export const api = {
  // Project endpoints
  async createProject(data: { name: string; description: string; project_type: string; technologies: string[] }): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create project');
    return res.json();
  },

  async listProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects`);
    if (!res.ok) throw new Error('Failed to list projects');
    return res.json();
  },

  async getProject(id: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`);
    if (!res.ok) throw new Error('Failed to get project');
    return res.json();
  },

  async getProjectFiles(id: string): Promise<{ project_id: string; file_tree: FileTreeNode[] }> {
    const res = await fetch(`${API_BASE}/projects/${id}/files`);
    if (!res.ok) throw new Error('Failed to get project files');
    return res.json();
  },

  async getFileContent(id: string, path: string): Promise<{ path: string; content: string }> {
    const res = await fetch(`${API_BASE}/projects/${id}/files/content?path=${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error('Failed to read file');
    return res.json();
  },

  async getDocumentation(id: string): Promise<{ title: string; content_markdown: string; sections: Record<string, string> }> {
    const res = await fetch(`${API_BASE}/projects/${id}/documentation`);
    if (!res.ok) throw new Error('Failed to get documentation');
    return res.json();
  },

  async getProjectDiagrams(id: string): Promise<ProjectDiagramsResponse> {
    const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(id)}/diagrams`);
    if (!res.ok) throw new Error(await errorMessage(res, 'Failed to load project diagrams.'));
    return res.json();
  },

  async generateProjectDiagrams(id: string): Promise<ProjectDiagramsResponse> {
    const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(id)}/diagrams/generate`, { method: 'POST' });
    if (!res.ok) throw new Error(await errorMessage(res, 'Failed to generate project diagrams.'));
    return res.json();
  },

  async uploadFile(file: File): Promise<{ filename: string; saved_as: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/projects/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(await errorMessage(res, 'Failed to upload file.'));
    return res.json();
  },

  // Transparent Legal AI endpoints
  async createLegalAnalysis(question: string, jurisdiction?: string): Promise<LegalAnalysisResult> {
    const res = await fetch(`${API_BASE}/legal/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, jurisdiction }),
    });
    if (!res.ok) throw new Error('Failed to create legal query');
    return res.json();
  },

  async getLegalAnalysis(id: string): Promise<LegalAnalysisResult> {
    const res = await fetch(`${API_BASE}/legal/${id}`);
    if (!res.ok) throw new Error('Failed to get legal analysis');
    return res.json();
  },

  async getCuratedLegalSources(): Promise<LegalSource[]> {
    const res = await fetch(`${API_BASE}/legal/sources/curated`);
    if (!res.ok) throw new Error('Failed to get curated legal sources');
    return res.json();
  },

  // Agents
  async listAgents(): Promise<{ total: number; agents: any[] }> {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error('Failed to list agents');
    return res.json();
  },

  // Health
  async getHealth(): Promise<{ status: string; mode: string; demo_mode: boolean }> {
    const res = await fetch('/health');
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  }
};
