import React, { useState } from 'react';
import {
  Folder,
  FolderOpen,
  FileCode,
  FileText,
  Download,
  Copy,
  Check,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import { FileTreeNode } from '../types/project';
import { api } from '../services/api';

interface FileExplorerProps {
  projectId: string;
  fileTree: FileTreeNode[];
}

export const FileExplorer: React.FC<FileExplorerProps> = ({ projectId, fileTree }) => {
  const [selectedFilePath, setSelectedFilePath] = useState<string>('');
  const [fileContent, setFileContent] = useState<string>('');
  const [loadingFile, setLoadingFile] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({ '': true });

  const toggleFolder = (path: string) => {
    setExpandedFolders((prev) => ({ ...prev, [path]: !prev[path] }));
  };

  const handleSelectFile = async (path: string) => {
    setSelectedFilePath(path);
    setLoadingFile(true);
    try {
      const data = await api.getFileContent(projectId, path);
      setFileContent(data.content);
    } catch (err) {
      setFileContent('// Failed to load file content.');
    } finally {
      setLoadingFile(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(fileContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Recursive Tree Node Renderer
  const renderTree = (nodes: FileTreeNode[], depth = 0) => {
    return nodes.map((node) => {
      const isExpanded = expandedFolders[node.path] !== false; // default open
      if (node.is_dir) {
        return (
          <div key={node.path} className="select-none">
            <div
              onClick={() => toggleFolder(node.path)}
              className="flex items-center space-x-2 px-2 py-1.5 rounded-lg hover:bg-slate-800/60 cursor-pointer text-xs font-semibold text-slate-300 transition-colors"
              style={{ paddingLeft: `${depth * 14 + 8}px` }}
            >
              {isExpanded ? (
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
              )}
              {isExpanded ? (
                <FolderOpen className="w-4 h-4 text-sky-400" />
              ) : (
                <Folder className="w-4 h-4 text-sky-400" />
              )}
              <span>{node.name}</span>
            </div>
            {isExpanded && node.children && (
              <div>{renderTree(node.children, depth + 1)}</div>
            )}
          </div>
        );
      }

      const isSelected = selectedFilePath === node.path;
      return (
        <div
          key={node.path}
          onClick={() => handleSelectFile(node.path)}
          className={`flex items-center space-x-2 px-2 py-1.5 rounded-lg cursor-pointer text-xs transition-colors select-none ${
            isSelected
              ? 'bg-sky-500/20 text-sky-300 font-semibold border border-sky-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
          }`}
          style={{ paddingLeft: `${depth * 14 + 20}px` }}
        >
          {node.extension === 'py' || node.extension === 'js' || node.extension === 'ts' ? (
            <FileCode className="w-3.5 h-3.5 text-indigo-400" />
          ) : (
            <FileText className="w-3.5 h-3.5 text-slate-400" />
          )}
          <span className="truncate">{node.name}</span>
        </div>
      );
    });
  };

  return (
    <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-2xl flex flex-col md:flex-row h-[550px]">
      {/* File Tree Left Sidebar */}
      <div className="w-full md:w-64 border-r border-slate-800 bg-slate-950/40 p-4 flex flex-col justify-between shrink-0">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              Project Codebase
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">generated_projects/</span>
          </div>
          <div className="overflow-y-auto max-h-[420px] space-y-0.5 pr-1">
            {fileTree.length > 0 ? (
              renderTree(fileTree)
            ) : (
              <p className="text-xs text-slate-400 p-2 text-center">No files generated yet.</p>
            )}
          </div>
        </div>

        {/* ZIP Download button */}
        <a
          href={`/api/projects/${projectId}/download`}
          className="w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all shadow-md active:scale-95"
        >
          <Download className="w-4 h-4 text-sky-400" />
          <span>Download Codebase (.ZIP)</span>
        </a>
      </div>

      {/* Code Viewer Panel */}
      <div className="flex-1 flex flex-col bg-slate-950/80 min-w-0">
        {selectedFilePath ? (
          <>
            <div className="p-3 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
              <span className="text-xs font-mono text-slate-300 font-medium">
                {selectedFilePath}
              </span>
              <button
                onClick={copyToClipboard}
                className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[11px] font-medium text-slate-300 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
                <span>{copied ? 'Copied!' : 'Copy Code'}</span>
              </button>
            </div>

            <div className="p-4 overflow-auto flex-1 font-mono text-xs text-slate-200 leading-relaxed">
              {loadingFile ? (
                <div className="p-8 text-center text-slate-400">Loading file content...</div>
              ) : (
                <pre className="whitespace-pre">{fileContent}</pre>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-slate-400">
            <FileCode className="w-12 h-12 text-slate-600 mb-3" />
            <p className="text-sm font-semibold text-slate-300">Select a file to inspect source code</p>
            <p className="text-xs text-slate-400 mt-1">Generated directly to disk by the Coding Agent.</p>
          </div>
        )}
      </div>
    </div>
  );
};
