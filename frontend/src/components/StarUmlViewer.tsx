import React, { useEffect, useRef, useState } from 'react';
import {
  Download,
  FileImage,
  FileText,
  Maximize,
  Network,
  RefreshCw,
  ZoomIn,
  ZoomOut,
} from 'lucide-react';
import { api, ProjectDiagram } from '../services/api';

interface StarUmlViewerProps {
  projectId?: string;
}

const diagramTabs = [
  { id: 'use_case', title: 'Use Case Diagram' },
  { id: 'class', title: 'Class Diagram' },
  { id: 'sequence', title: 'Sequence Diagram' },
  { id: 'activity', title: 'Activity Diagram' },
  { id: 'component', title: 'Component Diagram' },
] as const;

const exportFormats = [
  { id: 'png', label: 'PNG', icon: FileImage },
  { id: 'svg', label: 'SVG', icon: Network },
  { id: 'pdf', label: 'PDF', icon: FileText },
] as const;

export const StarUmlViewer: React.FC<StarUmlViewerProps> = ({ projectId }) => {
  const [activeDiagram, setActiveDiagram] = useState<string>('use_case');
  const [diagrams, setDiagrams] = useState<Record<string, ProjectDiagram>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const drag = useRef<{ pointerId: number; x: number; y: number; panX: number; panY: number } | null>(null);

  const loadDiagrams = async (regenerate = false) => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const result = regenerate
        ? await api.generateProjectDiagrams(projectId)
        : await api.getProjectDiagrams(projectId);
      setDiagrams(Object.fromEntries(result.diagrams.map((diagram) => [diagram.id, diagram])));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Could not load UML diagrams.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setDiagrams({});
    setZoom(1);
    setPan({ x: 0, y: 0 });
    void loadDiagrams();
  }, [projectId]);

  const current = diagrams[activeDiagram];
  const changeZoom = (change: number) => setZoom((value) => Math.min(3, Math.max(0.5, value + change)));

  const handlePointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0 || zoom <= 1) return;
    drag.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!drag.current || drag.current.pointerId !== event.pointerId) return;
    setPan({
      x: drag.current.panX + event.clientX - drag.current.x,
      y: drag.current.panY + event.clientY - drag.current.y,
    });
  };

  const handlePointerUp = (event: React.PointerEvent<HTMLDivElement>) => {
    if (drag.current?.pointerId === event.pointerId) drag.current = null;
  };

  const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
    if (!event.ctrlKey && !event.metaKey) return;
    event.preventDefault();
    changeZoom(event.deltaY < 0 ? 0.1 : -0.1);
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Network className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-bold text-white tracking-tight">Star UML & System Design Architecture</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Rendered UML diagrams are generated from each project&apos;s generated source code.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void loadDiagrams(true)}
            disabled={!projectId || loading}
            className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-xs font-semibold text-slate-200 border border-slate-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Regenerate
          </button>
          {projectId && (
            <a
              href={`/api/projects/${encodeURIComponent(projectId)}/diagrams/export/all`}
              className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 text-xs font-semibold text-cyan-300 border border-cyan-500/30"
            >
              <Download className="w-4 h-4" />
              Download All
            </a>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="UML diagram types">
        {diagramTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeDiagram === tab.id}
            onClick={() => setActiveDiagram(tab.id)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeDiagram === tab.id
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-md shadow-cyan-500/10'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            {tab.title}
          </button>
        ))}
      </div>

      <section className="p-5 md:p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 shadow-xl">
        <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-white">{current?.title || diagramTabs.find((tab) => tab.id === activeDiagram)?.title}</h4>
            <p className="text-xs text-slate-400 mt-1">
              {current?.description || 'Generated diagrams will be available after a project has completed source-code generation.'}
            </p>
            {current?.source_files && (
              <p className="text-[11px] text-slate-500 mt-2">
                Analyzed {current.source_files.length} source files
                {current.classes.length ? ` · ${current.classes.length} classes: ${current.classes.join(', ')}` : ''}
              </p>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button type="button" onClick={() => changeZoom(-0.2)} disabled={!current} aria-label="Zoom out" className="diagram-tool">
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono text-slate-400 min-w-12 text-center">{Math.round(zoom * 100)}%</span>
            <button type="button" onClick={() => changeZoom(0.2)} disabled={!current} aria-label="Zoom in" className="diagram-tool">
              <ZoomIn className="w-4 h-4" />
            </button>
            <button type="button" onClick={resetView} disabled={!current} className="diagram-tool inline-flex items-center gap-1.5">
              <Maximize className="w-4 h-4" />
              Fit
            </button>
            {exportFormats.map(({ id, label, icon: Icon }) => (
              <a
                key={id}
                href={current ? `${current.export_url}?format=${id}` : undefined}
                aria-disabled={!current}
                className={`diagram-tool inline-flex items-center gap-1.5 ${!current ? 'pointer-events-none opacity-40' : ''}`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </a>
            ))}
          </div>
        </div>

        <div
          className={`h-[62vh] min-h-[360px] max-h-[760px] rounded-xl bg-slate-950 border border-slate-800/80 overflow-hidden flex items-center justify-center touch-none ${
            zoom > 1 ? 'cursor-grab active:cursor-grabbing' : ''
          }`}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerCancel={handlePointerUp}
          onWheel={handleWheel}
          aria-label="Rendered UML diagram. Hold Control or Command while scrolling to zoom."
        >
          {loading ? (
            <div className="text-sm text-slate-400 animate-pulse">Loading rendered diagram…</div>
          ) : error ? (
            <div className="max-w-lg px-6 text-center">
              <p className="text-sm font-semibold text-rose-300">Diagram unavailable</p>
              <p className="text-xs text-slate-400 mt-2">{error}</p>
              <button type="button" onClick={() => void loadDiagrams(true)} className="mt-4 px-3 py-2 rounded-lg bg-slate-800 text-xs text-white">
                Generate diagrams
              </button>
            </div>
          ) : current ? (
            <img
              src={current.svg_url}
              alt={`${current.title} for the current project`}
              draggable={false}
              className="max-w-full max-h-full object-contain select-none"
              style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }}
            />
          ) : (
            <div className="max-w-lg px-6 text-center">
              <Network className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-sm font-semibold text-slate-300">
                {projectId ? 'Project diagrams are not available yet' : 'Select or generate a project first'}
              </p>
              <p className="text-xs text-slate-500 mt-2">
                Each diagram is built from the current project&apos;s source files and workflow.
              </p>
            </div>
          )}
        </div>
        <p className="text-[11px] text-slate-500">
          Tip: use the zoom controls, or hold Ctrl/Command and scroll. Drag the diagram to pan while zoomed in.
        </p>
      </section>
    </div>
  );
};
