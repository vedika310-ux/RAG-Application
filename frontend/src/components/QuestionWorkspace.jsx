import React, { useState } from "react";
import { MessageSquare, Sparkles, Send, Loader2, FileCheck, Globe } from "lucide-react";

export default function QuestionWorkspace({
  selectedDoc,
  selectedDocId,
  onAskQuestion,
  isLoading,
}) {
  const [question, setQuestion] = useState("");

  const sampleQuestions = [
    "What is the main objective of this project?",
    "What is the architecture and technology stack?",
    "What are the main advantages and limitations?",
    "Summarize the key findings.",
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;
    onAskQuestion(question.trim());
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const scopeLabel =
    selectedDocId === "all"
      ? "All Documents (Global Search)"
      : selectedDoc
      ? selectedDoc.filename
      : "No document selected (Select a document or 'All Documents' above)";

  return (
    <section className="fluent-card question-workspace-section">
      <div className="workspace-header">
        <div className="workspace-title-row">
          <MessageSquare size={18} className="text-accent" />
          <h2 className="workspace-title">Question Workspace</h2>
        </div>
        <div className="scope-indicator-pill">
          {selectedDocId === "all" ? (
            <Globe size={14} className="text-blue" />
          ) : (
            <FileCheck size={14} className="text-green" />
          )}
          <span className="scope-label">Document:</span>
          <span className="scope-name" title={scopeLabel}>
            {scopeLabel}
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="question-form">
        <div className="input-container">
          <label htmlFor="question-input" className="input-label">
            Ask a question:
          </label>
          <div className="textarea-wrapper">
            <textarea
              id="question-input"
              rows={3}
              placeholder={
                selectedDocId
                  ? "What is the main objective of this project?"
                  : "Please select a document or 'All Documents' from the table above..."
              }
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading || !selectedDocId}
              className="win-textarea"
            />
          </div>
        </div>

        {/* Quick sample question chips */}
        <div className="sample-chips-row">
          <span className="chips-hint">Suggested:</span>
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              type="button"
              className="chip-btn"
              disabled={isLoading || !selectedDocId}
              onClick={() => setQuestion(q)}
            >
              {q}
            </button>
          ))}
        </div>

        <div className="form-actions-row">
          <button
            type="submit"
            className="win-btn win-btn-primary win-btn-lg ask-btn"
            disabled={!question.trim() || isLoading || !selectedDocId}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                <span>RETRIEVING & GENERATING...</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>ASK QUESTION</span>
              </>
            )}
          </button>
        </div>
      </form>
    </section>
  );
}
