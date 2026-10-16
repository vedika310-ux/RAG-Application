import React, { useState } from "react";
import {
  Search,
  CheckCircle,
  FileText,
  ChevronDown,
  ChevronUp,
  Cpu,
  Layers,
  Sparkles,
  ArrowRight,
  Database,
  Quote,
} from "lucide-react";

export default function RetrievalInspector({
  question,
  sources = [],
  answer,
  isLoading,
}) {
  const [expandedChunkId, setExpandedChunkId] = useState(null);

  if (!question && sources.length === 0 && !isLoading) {
    return null;
  }

  const toggleChunk = (id) => {
    setExpandedChunkId(expandedChunkId === id ? null : id);
  };

  const getScoreColor = (score) => {
    if (score >= 0.85) return "score-high";
    if (score >= 0.70) return "score-med";
    return "score-low";
  };

  return (
    <section className="fluent-card retrieval-inspector-section">
      <div className="inspector-header">
        <div className="inspector-title-group">
          <Database size={18} className="text-purple" />
          <h2 className="inspector-title">RAG Retrieval Inspector</h2>
          <span className="live-tag">LIVE VECTOR AUDIT</span>
        </div>
        <div className="inspector-stats-tag">
          {sources.length} chunks retrieved from ChromaDB
        </div>
      </div>

      {/* Visual Pipeline Bar */}
      <div className="rag-pipeline-visual">
        <div className="pipeline-step step-done">
          <div className="step-num">1</div>
          <div className="step-desc">
            <span className="step-title">Question</span>
            <span className="step-sub">User Input</span>
          </div>
        </div>
        <ArrowRight size={14} className="pipeline-arrow" />

        <div className="pipeline-step step-done">
          <div className="step-num">2</div>
          <div className="step-desc">
            <span className="step-title">Vector Search</span>
            <span className="step-sub">MiniLM-L6-v2</span>
          </div>
        </div>
        <ArrowRight size={14} className="pipeline-arrow" />

        <div className="pipeline-step step-done">
          <div className="step-num">3</div>
          <div className="step-desc">
            <span className="step-title">Top-{sources.length || 5} Chunks</span>
            <span className="step-sub">ChromaDB Store</span>
          </div>
        </div>
        <ArrowRight size={14} className="pipeline-arrow" />

        <div className="pipeline-step step-done">
          <div className="step-num">4</div>
          <div className="step-desc">
            <span className="step-title">LLM Prompt</span>
            <span className="step-sub">Strict Context</span>
          </div>
        </div>
        <ArrowRight size={14} className="pipeline-arrow" />

        <div className="pipeline-step step-active">
          <div className="step-num">5</div>
          <div className="step-desc">
            <span className="step-title">Final Answer</span>
            <span className="step-sub">Gemini Live</span>
          </div>
        </div>
      </div>

      {/* Question Inspection */}
      <div className="inspector-block">
        <div className="inspector-block-label">QUESTION</div>
        <div className="inspector-question-box">
          <Quote size={16} className="quote-icon" />
          <span>"{question}"</span>
        </div>
      </div>

      {/* Retrieved Chunks */}
      <div className="inspector-block">
        <div className="inspector-block-label-row">
          <span className="inspector-block-label">
            RETRIEVED CHUNKS ({sources.length})
          </span>
          <span className="inspector-meta-note">
            Ranked by vector cosine similarity
          </span>
        </div>

        {sources.length === 0 && !isLoading && (
          <div className="empty-chunks-box">
            No relevant chunks met the similarity threshold.
          </div>
        )}

        <div className="chunks-list">
          {sources.map((chunk, index) => {
            const isExpanded = expandedChunkId === chunk.chunk_id || index === 0;
            const scorePercent = Math.round(chunk.score * 100);

            return (
              <div key={chunk.chunk_id || index} className="chunk-card">
                <div
                  className="chunk-header-row"
                  onClick={() => toggleChunk(chunk.chunk_id)}
                >
                  <div className="chunk-meta-left">
                    <span className="chunk-rank">Source #{index + 1}</span>
                    <span className="chunk-id-tag">{chunk.chunk_id}</span>
                    <span className="chunk-doc-badge">
                      <FileText size={12} />
                      {chunk.document}
                    </span>
                    {chunk.page && (
                      <span className="chunk-page-badge">
                        Page {chunk.page}
                      </span>
                    )}
                    {chunk.section && (
                      <span className="chunk-section-badge">
                        {chunk.section}
                      </span>
                    )}
                    {chunk.row_range && (
                      <span className="chunk-section-badge">
                        {chunk.row_range}
                      </span>
                    )}
                  </div>

                  <div className="chunk-meta-right">
                    <div className="similarity-meter-wrap">
                      <span className="sim-label">Similarity:</span>
                      <div className="sim-bar-bg">
                        <div
                          className={`sim-bar-fill ${getScoreColor(chunk.score)}`}
                          style={{ width: `${Math.max(10, scorePercent)}%` }}
                        ></div>
                      </div>
                      <span className={`sim-value ${getScoreColor(chunk.score)}`}>
                        {chunk.score.toFixed(3)}
                      </span>
                    </div>

                    <button className="expand-toggle-btn" title="Toggle full text">
                      {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="chunk-body-text">
                    <pre className="chunk-pre">{chunk.text}</pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Final Answer Inspection */}
      {answer && (
        <div className="inspector-block">
          <div className="inspector-block-label">FINAL ANSWER PRODUCED</div>
          <div className="inspector-answer-box">
            <p>{answer}</p>
          </div>
        </div>
      )}
    </section>
  );
}
