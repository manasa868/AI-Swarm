import React, { useState } from 'react';
import {
  Sparkles,
  Cpu,
  Globe,
  BarChart3,
  BookOpen,
  Scale,
  Terminal,
  Upload,
  FileCheck,
  ArrowRight,
  Lightbulb
} from 'lucide-react';
import { ProjectType } from '../types/project';
import { api } from '../services/api';

interface ProjectInputPageProps {
  onStartSwarm: (projectData: {
    name: string;
    description: string;
    project_type: ProjectType;
    technologies: string[];
  }) => void;
  isLoading: boolean;
}

export const ProjectInputPage: React.FC<ProjectInputPageProps> = ({
  onStartSwarm,
  isLoading,
}) => {
  const [name, setName] = useState<string>('Fake News Detection System');
  const [description, setDescription] = useState<string>(
    'Build a Python fake news detection system using machine learning with TF-IDF vectorization, a PassiveAggressive classifier, automated unit testing, and a FastAPI inference service.'
  );
  const [projectType, setProjectType] = useState<ProjectType>('ml');
  const [selectedTech, setSelectedTech] = useState<string[]>([
    'Python',
    'Scikit-Learn',
    'FastAPI',
    'PyTest',
  ]);
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; size: number }>>([]);
  const [uploading, setUploading] = useState<boolean>(false);

  const projectTypes: Array<{
    type: ProjectType;
    label: string;
    desc: string;
    icon: any;
    color: string;
  }> = [
    {
      type: 'ml',
      label: 'Machine Learning',
      desc: 'Dataset pipeline, training, model evaluation & inference API',
      icon: Cpu,
      color: 'from-sky-500/20 to-blue-500/10 border-sky-500/40 text-sky-400',
    },
    {
      type: 'web',
      label: 'Web Application',
      desc: 'Full-stack modular services (e.g. College Bus System)',
      icon: Globe,
      color: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/40 text-emerald-400',
    },
    {
      type: 'data_analysis',
      label: 'Data Analysis',
      desc: 'Clustering, statistical EDA, anomaly detection & variance',
      icon: BarChart3,
      color: 'from-amber-500/20 to-orange-500/10 border-amber-500/40 text-amber-400',
    },
    {
      type: 'research',
      label: 'Research / Report',
      desc: 'Technical investigations and domain synthesis',
      icon: BookOpen,
      color: 'from-indigo-500/20 to-purple-500/10 border-indigo-500/40 text-indigo-400',
    },
    {
      type: 'legal',
      label: 'Transparent Legal AI',
      desc: 'Strict non-hallucinatory legal analysis & fact decomposition',
      icon: Scale,
      color: 'from-purple-500/20 to-fuchsia-500/10 border-purple-500/40 text-purple-400',
    },
    {
      type: 'general',
      label: 'Custom Software Task',
      desc: 'Clean architecture microservices, CLI tools & logic engines',
      icon: Terminal,
      color: 'from-slate-500/20 to-slate-700/10 border-slate-500/40 text-slate-300',
    },
  ];

  const suggestedPrompts = [
    {
      type: 'ml' as ProjectType,
      name: 'Fake News Detection System',
      text: 'Build a Python fake-news detection system using machine learning with TF-IDF vectorization and a high-performance classifier.',
      tech: ['Python', 'Scikit-Learn', 'FastAPI', 'PyTest'],
    },
    {
      type: 'web' as ProjectType,
      name: 'College Bus Management System',
      text: 'Build a college bus management system with routes, driver scheduling, student assignments, and a fleet management dashboard.',
      tech: ['Python', 'FastAPI', 'SQLite', 'Pydantic'],
    },
    {
      type: 'data_analysis' as ProjectType,
      name: 'Customer Segmentation Analytics',
      text: 'Analyze customer segmentation data using RFM scoring, K-Means clustering, variance checks, and statistical cluster validation.',
      tech: ['Python', 'K-Means', 'Pandas', 'PyTest'],
    },
    {
      type: 'legal' as ProjectType,
      name: 'Transparent Legal AI Review',
      text: 'Is an employee non-compete clause enforceable if signed mid-tenure without additional monetary consideration or promotion?',
      tech: ['Legal Knowledge Base', 'FTC Rule 910', 'Restatement of Contracts'],
    },
  ];

  const availableTech = [
    'Python',
    'FastAPI',
    'Scikit-Learn',
    'PyTest',
    'React',
    'SQLite',
    'PostgreSQL',
    'Pydantic',
    'Docker',
    'Pandas',
  ];

  const toggleTech = (tech: string) => {
    if (selectedTech.includes(tech)) {
      setSelectedTech(selectedTech.filter((t) => t !== tech));
    } else {
      setSelectedTech([...selectedTech, tech]);
    }
  };

  const applyPrompt = (p: typeof suggestedPrompts[0]) => {
    setName(p.name);
    setDescription(p.text);
    setProjectType(p.type);
    setSelectedTech(p.tech);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploading(true);
    try {
      await api.uploadFile(file);
      setUploadedFiles((prev) => [...prev, { name: file.name, size: file.size }]);
    } catch (err) {
      alert('Upload failed or file type not allowed.');
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !description.trim()) {
      alert('Please provide both a project name and task description.');
      return;
    }
    onStartSwarm({
      name,
      description,
      project_type: projectType,
      technologies: selectedTech,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Hero Title */}
      <div className="text-center space-y-3 pt-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>College Major Project: Multi-Agent AI Orchestration</span>
        </div>
        <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          AI Swarm: From Individual to Intelligent Teams
        </h2>
        <p className="text-sm text-slate-400 max-w-2xl mx-auto">
          Deploy an autonomous swarm of specialized agents. The Coordinator Agent analyzes requirements,
          decomposes subtasks, assigns roles, and executes closed-loop testing and auto-correction.
        </p>
      </div>

      {/* Suggested Prompts Banner */}
      <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl space-y-3">
        <div className="flex items-center space-x-2 text-xs font-bold text-slate-300 uppercase tracking-wide">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <span>Quick Benchmark Prompts</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {suggestedPrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPrompt(p)}
              className="text-left p-3 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800/80 hover:border-sky-500/40 transition-all text-xs group"
            >
              <span className="font-bold text-white group-hover:text-sky-300 transition-colors block">
                {p.name}
              </span>
              <span className="text-[11px] text-slate-400 line-clamp-1 mt-0.5 font-sans">
                {p.text}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-2xl space-y-6">
        {/* Project Name */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-200 uppercase tracking-wide block">
            Project / Task Title
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Fake News Detection System"
            className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-all"
            required
          />
        </div>

        {/* Project Category Cards */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-200 uppercase tracking-wide block">
            Select Project Archetype
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {projectTypes.map((t) => {
              const Icon = t.icon;
              const isSelected = projectType === t.type;
              return (
                <div
                  key={t.type}
                  onClick={() => setProjectType(t.type)}
                  className={`p-3.5 rounded-xl border cursor-pointer select-none transition-all ${
                    isSelected
                      ? `bg-gradient-to-br ${t.color} ring-2 ring-sky-500 shadow-lg`
                      : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-850/60'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-slate-400'}`} />
                    <span className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                      {t.label}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{t.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Task Description */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-200 uppercase tracking-wide block">
            Detailed Task Requirements & Scope
          </label>
          <textarea
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe features, algorithms, schemas, or requirements..."
            className="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs font-sans focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-all leading-relaxed"
            required
          />
        </div>

        {/* Technology Selector */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-200 uppercase tracking-wide block">
            Target Technology Stack
          </label>
          <div className="flex flex-wrap gap-2">
            {availableTech.map((tech) => {
              const isSelected = selectedTech.includes(tech);
              return (
                <button
                  key={tech}
                  type="button"
                  onClick={() => toggleTech(tech)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isSelected
                      ? 'bg-sky-500 text-white shadow-sm shadow-sky-500/20'
                      : 'bg-slate-950 text-slate-400 border border-slate-800 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  {tech}
                </button>
              );
            })}
          </div>
        </div>

        {/* File Upload Zone */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-200 uppercase tracking-wide block">
            Optional Requirement Files (PDF, CSV, TXT, DOCX, Code)
          </label>
          <div className="p-4 rounded-xl border border-dashed border-slate-800 bg-slate-950/40 text-center hover:border-slate-700 transition-colors">
            <input
              type="file"
              id="file-upload"
              onChange={handleFileUpload}
              className="hidden"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center justify-center space-y-2"
            >
              <Upload className="w-6 h-6 text-slate-400" />
              <span className="text-xs text-slate-300 font-medium">
                {uploading ? 'Uploading file...' : 'Click to browse or drop reference files'}
              </span>
              <span className="text-[10px] text-slate-400">
                Supports TXT, CSV, JSON, PDF, DOCX, Python, JS, Java
              </span>
            </label>
          </div>

          {uploadedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {uploadedFiles.map((f, i) => (
                <div
                  key={i}
                  className="flex items-center space-x-1.5 px-3 py-1 rounded-md bg-slate-800 border border-slate-700 text-[11px] text-slate-300"
                >
                  <FileCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{f.name}</span>
                  <span className="text-slate-400">({(f.size / 1024).toFixed(1)} KB)</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Start Swarm Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl bg-gradient-to-r from-sky-500 via-indigo-600 to-cyan-500 hover:from-sky-400 hover:to-cyan-400 text-white font-bold text-sm tracking-wide shadow-xl shadow-sky-500/20 active:scale-[0.99] transition-all disabled:opacity-50"
        >
          {isLoading ? (
            <span className="flex items-center space-x-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>Initializing Autonomous AI Swarm...</span>
            </span>
          ) : (
            <span className="flex items-center space-x-2">
              <span>Start Autonomous Swarm</span>
              <ArrowRight className="w-4 h-4" />
            </span>
          )}
        </button>
      </form>
    </div>
  );
};
