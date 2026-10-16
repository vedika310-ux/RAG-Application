import React from "react";
import { Files, Database, MessageSquare, ArrowUpRight } from "lucide-react";

export default function DashboardCards({ documentsCount = 0, chunksCount = 0, questionsCount = 0 }) {
  return (
    <div className="dashboard-cards-grid">
      <div className="fluent-card metric-card">
        <div className="card-header-row">
          <span className="card-label">DOCUMENTS</span>
          <div className="card-icon-pill icon-blue">
            <Files size={18} />
          </div>
        </div>
        <div className="card-main-metric">{documentsCount}</div>
        <div className="card-footer-caption">
          <span>Active Ingested Files</span>
        </div>
      </div>

      <div className="fluent-card metric-card">
        <div className="card-header-row">
          <span className="card-label">CHUNKS</span>
          <div className="card-icon-pill icon-purple">
            <Database size={18} />
          </div>
        </div>
        <div className="card-main-metric">{chunksCount}</div>
        <div className="card-footer-caption">
          <span>Vectors in ChromaDB</span>
        </div>
      </div>

      <div className="fluent-card metric-card">
        <div className="card-header-row">
          <span className="card-label">QUESTIONS</span>
          <div className="card-icon-pill icon-green">
            <MessageSquare size={18} />
          </div>
        </div>
        <div className="card-main-metric">{questionsCount}</div>
        <div className="card-footer-caption">
          <span>Queries Executed</span>
        </div>
      </div>
    </div>
  );
}
