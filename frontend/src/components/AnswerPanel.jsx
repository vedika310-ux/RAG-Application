import React, { useState } from "react";
import { Check, Copy, Bot, Sparkles, BookOpen } from "lucide-react";

export default function AnswerPanel({
  answer,
  sourcesCount = 0,
  isLoading,
  lastQuestion,
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!answer) return;
    navigator.clipboard.writeText(answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!answer && !isLoading) {
    return null;
  }

  return (
    <section className="fluent-card answer-panel-section">
      <div className="answer-header-row">
        <div className="answer-title-group">
          <Bot size={18} className="text-accent" />
          <h2 className="answer-title">Answer</h2>
        </div>

        <div className="answer-actions-group">
          {sourcesCount > 0 && (
            <span className="sources-count-badge">
              <BookOpen size={13} />
              <span>{sourcesCount} Sources Used</span>
            </span>
          )}

          {answer && (
            <button className="win-btn win-btn-subtle btn-copy" onClick={handleCopy}>
              {copied ? (
                <>
                  <Check size={14} className="text-success" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy size={14} />
                  <span>Copy</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      <div className="answer-content-body">
        {isLoading ? (
          <div className="answer-loading-state">
            <div className="skeleton-line shimmer"></div>
            <div className="skeleton-line shimmer w-80"></div>
            <div className="skeleton-line shimmer w-90"></div>
            <div className="skeleton-line shimmer w-60"></div>
          </div>
        ) : (
          <div className="answer-text-formatted">
            {answer.split("\n\n").map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
