import React, { useState } from 'react';
import {
  Scale,
  ShieldCheck,
  AlertTriangle,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Sparkles,
  ExternalLink,
  Info,
  CheckCircle2,
  HelpCircle,
  ArrowRight
} from 'lucide-react';
import { LegalAnalysisResult } from '../types/legal';
import { api } from '../services/api';

export const TransparentLegalAIPage: React.FC = () => {
  const [question, setQuestion] = useState<string>(
    'Is an employee non-compete clause enforceable if signed mid-tenure without additional monetary consideration or promotion?'
  );
  const [jurisdiction, setJurisdiction] = useState<string>('United States / General Common Law');
  const [analysisResult, setAnalysisResult] = useState<LegalAnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<string>('');

  // Expandable card collapse state
  const [openCards, setOpenCards] = useState<Record<string, boolean>>({
    facts: true,
    sources: true,
    risks: true,
    explanation: true,
    limitations: true,
    disclaimer: true,
  });

  const toggleCard = (id: string) => {
    setOpenCards((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleRunLegalAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setCurrentStep('Initializing Legal Research Agent...');

    try {
      // 1. Create query record
      const created = await api.createLegalAnalysis(question, jurisdiction);
      
      // 2. Open SSE stream
      const eventSource = new EventSource(`/api/legal/${created.id}/stream`);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'agent_started') {
            setCurrentStep(`${data.agent}: ${data.message || 'Executing...'}`);
          } else if (data.type === 'workflow_completed') {
            setCurrentStep('Analysis Completed.');
            eventSource.close();
            // Fetch updated query
            api.getLegalAnalysis(created.id).then((res) => {
              setAnalysisResult(res);
              setLoading(false);
            });
          } else if (data.type === 'error') {
            setCurrentStep(`Error: ${data.message}`);
            setLoading(false);
            eventSource.close();
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setLoading(false);
      };
    } catch (err: any) {
      alert(`Legal analysis initialization failed: ${err.message}`);
      setLoading(false);
    }
  };

  const sampleQuestions = [
    {
      title: 'Mid-Tenure Non-Compete Consideration',
      q: 'Is an employee non-compete clause enforceable if signed mid-tenure without additional monetary consideration or promotion?',
      jur: 'United States / General Common Law',
    },
    {
      title: 'AI Code Copyright Ownership',
      q: 'Does an engineer or corporation hold copyright over software code generated autonomously by an AI foundation model?',
      jur: 'U.S. Copyright Law (Compendium § 313.2)',
    },
    {
      title: 'E-Commerce Delayed Shipment Refund',
      q: 'Can an online retail merchant refuse a cash refund when shipping is delayed beyond 30 days under federal trade regulations?',
      jur: 'FTC 16 CFR Part 435 (Mail & Internet Order Rule)',
    },
  ];

  return (
    <div className="space-y-8 max-w-4xl mx-auto pb-16">
      {/* Hero Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-950/40 via-slate-900 to-slate-900 border border-purple-500/30 shadow-2xl">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
            <Scale className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              Transparent Legal AI Assistant
            </h2>
            <p className="text-xs text-purple-300/80">
              Verifiable, auditable legal information retrieval with strict zero-hallucination citations.
            </p>
          </div>
        </div>

        {/* Prominent Legal Disclaimer Badge */}
        <div className="mt-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start space-x-2.5">
          <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="font-semibold">Notice:</strong> Transparent Legal AI is an academic AI research assistant.
            It does <strong className="underline">NOT</strong> provide formal legal advice or create an attorney-client relationship.
            For binding legal counsel, consult a qualified attorney licensed in your jurisdiction.
          </p>
        </div>
      </div>

      {/* Benchmark Presets */}
      <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 space-y-2">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
          Select Verified Legal Inquiries
        </span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          {sampleQuestions.map((sq, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuestion(sq.q);
                setJurisdiction(sq.jur);
              }}
              className="text-left p-2.5 rounded-lg bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 hover:border-purple-500/40 transition-all text-xs"
            >
              <span className="font-bold text-slate-200 block truncate">{sq.title}</span>
              <span className="text-[10px] text-slate-400 block truncate mt-0.5">{sq.jur}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Query Submission Box */}
      <form onSubmit={handleRunLegalAnalysis} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 shadow-xl">
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
            Legal Question & Scenario
          </label>
          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-white text-xs font-sans focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 leading-relaxed"
            placeholder="Type your legal research question..."
            required
          />
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Jurisdiction:</span>
            <input
              type="text"
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs tracking-wide shadow-lg shadow-purple-500/20 active:scale-95 transition-all disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center space-x-2">
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>{currentStep || 'Analyzing Authorities...'}</span>
              </span>
            ) : (
              <span className="flex items-center space-x-2">
                <span>Run Transparent Analysis</span>
                <ArrowRight className="w-4 h-4" />
              </span>
            )}
          </button>
        </div>
      </form>

      {/* Expandable Transparency Cards Section */}
      {analysisResult && (
        <div className="space-y-4 animate-in fade-in duration-300">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Transparent Audit Trail & Reasoning Cards</span>
            </h3>
            <span className="text-xs text-slate-400">Click headers to expand or collapse</span>
          </div>

          {/* CARD 1: FACTS IDENTIFIED */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            <div
              onClick={() => toggleCard('facts')}
              className="p-4 bg-slate-850/80 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between select-none transition-colors"
            >
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-sky-400"></span>
                <h4 className="text-xs font-bold text-white uppercase">
                  1. Facts Identified & Assumptions Isolated
                </h4>
              </div>
              {openCards.facts ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </div>
            {openCards.facts && (
              <div className="p-4 space-y-3 bg-slate-950/40 text-xs">
                <div>
                  <span className="font-semibold text-sky-400 block mb-1">Explicit Facts Extracted:</span>
                  <ul className="list-disc pl-5 space-y-1 text-slate-300">
                    {analysisResult.facts_identified.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
                {analysisResult.assumptions.length > 0 && (
                  <div>
                    <span className="font-semibold text-amber-400 block mb-1">Unverified Assumptions:</span>
                    <ul className="list-disc pl-5 space-y-1 text-slate-400 italic">
                      {analysisResult.assumptions.map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {analysisResult.missing_info.length > 0 && (
                  <div>
                    <span className="font-semibold text-rose-400 block mb-1">Missing Material Information:</span>
                    <ul className="list-disc pl-5 space-y-1 text-slate-400">
                      {analysisResult.missing_info.map((m, i) => (
                        <li key={i}>{m}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* CARD 2: LEGAL INFORMATION & SOURCES */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            <div
              onClick={() => toggleCard('sources')}
              className="p-4 bg-slate-850/80 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between select-none transition-colors"
            >
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <h4 className="text-xs font-bold text-white uppercase">
                  2. Verified Legal Authorities & Statutory Citations
                </h4>
              </div>
              {openCards.sources ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </div>
            {openCards.sources && (
              <div className="p-4 space-y-3 bg-slate-950/40 text-xs">
                {analysisResult.sources.map((src, i) => (
                  <div key={i} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-emerald-400 text-xs">{src.title}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                        VERIFIED CITATION
                      </span>
                    </div>
                    <p className="font-mono text-[11px] text-slate-300 font-semibold">{src.citation}</p>
                    <p className="text-slate-400 text-[11px] italic bg-slate-950 p-2 rounded border border-slate-800/60">
                      "{src.excerpt}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* CARD 3: RISKS & UNCERTAINTIES */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            <div
              onClick={() => toggleCard('risks')}
              className="p-4 bg-slate-850/80 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between select-none transition-colors"
            >
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-rose-400"></span>
                <h4 className="text-xs font-bold text-white uppercase">
                  3. Legal Risks & Regulatory Uncertainties Matrix
                </h4>
              </div>
              {openCards.risks ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </div>
            {openCards.risks && (
              <div className="p-4 space-y-2.5 bg-slate-950/40 text-xs">
                {analysisResult.risks_uncertainties.map((r, i) => (
                  <div key={i} className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-start space-x-3">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white">{r.risk_area}</span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                          {r.severity} EXPOSURE
                        </span>
                      </div>
                      <p className="text-slate-300 text-[11px]">{r.description}</p>
                      <p className="text-sky-400 text-[10px] font-mono">Mitigation: {r.mitigation}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* CARD 4: PLAIN-LANGUAGE EXPLANATION */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            <div
              onClick={() => toggleCard('explanation')}
              className="p-4 bg-slate-850/80 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between select-none transition-colors"
            >
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                <h4 className="text-xs font-bold text-white uppercase">
                  4. Transparent Plain-Language Explanation & Source Tracing
                </h4>
              </div>
              {openCards.explanation ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </div>
            {openCards.explanation && (
              <div className="p-5 bg-slate-950/40 text-xs text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
                {analysisResult.explanation || analysisResult.analysis}
              </div>
            )}
          </div>

          {/* CARD 5: LIMITATIONS */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
            <div
              onClick={() => toggleCard('limitations')}
              className="p-4 bg-slate-850/80 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between select-none transition-colors"
            >
              <div className="flex items-center space-x-2.5">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                <h4 className="text-xs font-bold text-white uppercase">
                  5. Explicit Jurisdictional Limitations
                </h4>
              </div>
              {openCards.limitations ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </div>
            {openCards.limitations && (
              <div className="p-4 bg-slate-950/40 text-xs">
                <ul className="list-disc pl-5 space-y-1.5 text-slate-400">
                  {analysisResult.limitations.map((l, i) => (
                    <li key={i}>{l}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* CARD 6: MANDATORY DISCLAIMER */}
          <div className="p-5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs space-y-1.5">
            <span className="font-bold flex items-center gap-1.5 text-amber-300">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              <span>Mandatory Professional Disclaimer</span>
            </span>
            <p className="leading-relaxed text-[11px] text-amber-200/90 font-sans">
              {analysisResult.disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
