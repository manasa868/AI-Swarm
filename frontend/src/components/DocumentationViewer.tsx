import React, { useState } from 'react';
import {
  BookOpen,
  Copy,
  Check,
  Download,
  List,
  Layers,
  FileText
} from 'lucide-react';

interface DocumentationViewerProps {
  title: string;
  markdownContent: string;
  sections: Record<string, string>;
}

export const DocumentationViewer: React.FC<DocumentationViewerProps> = ({
  title,
  markdownContent,
  sections,
}) => {
  const [selectedSection, setSelectedSection] = useState<string>(
    Object.keys(sections)[0] || ''
  );
  const [copied, setCopied] = useState<boolean>(false);

  const sectionKeys = Object.keys(sections);

  const copyMarkdown = () => {
    navigator.clipboard.writeText(markdownContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadMarkdown = () => {
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_')}_Major_Project.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-sky-400" />
            <h3 className="text-base font-bold text-white tracking-tight">{title}</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Dynamic 22-section academic documentation compiled automatically by the Documentation Agent.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={copyMarkdown}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-slate-400" />}
            <span>{copied ? 'Copied Full Report' : 'Copy Markdown'}</span>
          </button>
          <button
            onClick={downloadMarkdown}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-xs font-semibold text-white transition-all shadow-md shadow-sky-500/20"
          >
            <Download className="w-4 h-4" />
            <span>Download .MD</span>
          </button>
        </div>
      </div>

      {/* Main Two-Column Reader */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Table of Contents Column */}
        <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 max-h-[600px] overflow-y-auto">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <List className="w-3.5 h-3.5" />
            <span>Table of Contents</span>
          </h4>
          <nav className="space-y-1">
            {sectionKeys.map((key) => {
              const isSelected = selectedSection === key;
              return (
                <button
                  key={key}
                  onClick={() => setSelectedSection(key)}
                  className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs transition-colors truncate ${
                    isSelected
                      ? 'bg-sky-500/20 text-sky-300 font-semibold border border-sky-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  {key}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Section Content Column */}
        <div className="md:col-span-3 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 min-h-[500px] max-h-[600px] overflow-y-auto font-sans leading-relaxed text-slate-200 text-xs">
          {sections[selectedSection] ? (
            <div className="prose prose-invert max-w-none space-y-4">
              <pre className="whitespace-pre-wrap font-sans text-xs text-slate-300 leading-relaxed">
                {sections[selectedSection]}
              </pre>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400">
              Select a section from the Table of Contents to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
