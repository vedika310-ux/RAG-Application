import React from "react";
import { Search, Settings, Activity, ShieldCheck, Sparkles, Layers } from "lucide-react";

export default function TopNav({
  searchQuery,
  setSearchQuery,
  onOpenSettings,
  serverStatus,
  embeddingModel,
}) {
  return (
    <header className="win11-header">
      <div className="header-brand">
        <div className="brand-icon">
          <Layers size={20} className="brand-svg" />
        </div>
        <div className="brand-text">
          <div className="brand-title">RAG DOCUMENT INTELLIGENCE</div>
          <div className="brand-subtitle">Windows 11 Edition • Vector Semantic Engine</div>
        </div>
      </div>

      <div className="header-search">
        <Search size={16} className="search-icon" />
        <input
          type="text"
          placeholder="Filter documents or chunks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        {searchQuery && (
          <button className="search-clear" onClick={() => setSearchQuery("")}>
            ×
          </button>
        )}
      </div>

      <div className="header-actions">
        <button
          className="win-btn win-btn-subtle"
          onClick={onOpenSettings}
          title="Configure API Keys and RAG Parameters"
        >
          <Settings size={16} />
          <span>Settings</span>
        </button>

        <div className={`status-badge ${serverStatus === "online" ? "status-online" : "status-offline"}`}>
          <span className="status-dot"></span>
          <span className="status-text">
            {serverStatus === "online" ? "Status: Online" : "Status: Offline"}
          </span>
        </div>
      </div>
    </header>
  );
}
