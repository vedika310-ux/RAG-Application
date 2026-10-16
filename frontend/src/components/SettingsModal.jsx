import React, { useState, useEffect } from "react";
import { Settings, X, Key, Check, Loader2, Sparkles, Layers, Sliders } from "lucide-react";
import { fetchSettings, saveSettings } from "../api";

export default function SettingsModal({ isOpen, onClose, onSettingsUpdated }) {
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [topK, setTopK] = useState(5);
  const [chunkSize, setChunkSize] = useState(800);
  const [chunkOverlap, setChunkOverlap] = useState(100);
  const [embeddingModel, setEmbeddingModel] = useState("all-MiniLM-L6-v2");
  const [isConfigured, setIsConfigured] = useState(false);
  const [keyPreview, setKeyPreview] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchSettings()
        .then((data) => {
          setIsConfigured(data.gemini_api_key_configured);
          setKeyPreview(data.gemini_api_key_preview || "");
          if (data.gemini_model) setModel(data.gemini_model);
          if (data.top_k) setTopK(data.top_k);
          if (data.chunk_size) setChunkSize(data.chunk_size);
          if (data.chunk_overlap) setChunkOverlap(data.chunk_overlap);
          if (data.embedding_model) setEmbeddingModel(data.embedding_model);
        })
        .catch((err) => console.error("Error fetching settings:", err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      const payload = {
        gemini_model: model,
        top_k: Number(topK),
        chunk_size: Number(chunkSize),
        chunk_overlap: Number(chunkOverlap),
      };
      if (apiKey.trim()) {
        payload.gemini_api_key = apiKey.trim();
      }

      await saveSettings(payload);
      setSaveSuccess(true);
      if (apiKey.trim()) {
        setIsConfigured(true);
        setKeyPreview(apiKey.trim().slice(0, 4) + "..." + apiKey.trim().slice(-4));
        setApiKey("");
      }
      setTimeout(() => {
        setSaveSuccess(false);
        if (onSettingsUpdated) onSettingsUpdated();
        onClose();
      }, 1000);
    } catch (err) {
      alert("Failed to save settings: " + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="fluent-modal settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-wrap">
            <Settings size={18} className="text-accent" />
            <h3 className="modal-title">RAG Engine & LLM Settings</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSave} className="modal-body settings-form-body">
          {/* Gemini API Key */}
          <div className="form-group">
            <label className="form-label">
              <Key size={14} />
              <span>Google Gemini API Key</span>
              {isConfigured && (
                <span className="badge-key-active">
                  Active {keyPreview ? `(${keyPreview})` : ""}
                </span>
              )}
            </label>
            <input
              type="password"
              placeholder={isConfigured ? "Enter new key to replace existing..." : "Paste Gemini API Key from Google AI Studio"}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="win-input"
            />
            <span className="input-helper">
              Get an API key free at{" "}
              <a href="https://aistudio.google.com/" target="_blank" rel="noreferrer" className="win-link">
                Google AI Studio
              </a>
              . Stored safely in runtime memory / environment.
            </span>
          </div>

          {/* Model Selection */}
          <div className="form-group">
            <label className="form-label">
              <Sparkles size={14} />
              <span>LLM Model</span>
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="win-select"
            >
              <option value="gemini-2.5-flash">gemini-2.5-flash (Fastest & Recommended)</option>
              <option value="gemini-1.5-flash">gemini-1.5-flash (Standard)</option>
              <option value="gemini-1.5-pro">gemini-1.5-pro (High reasoning)</option>
            </select>
          </div>

          <div className="form-row-2col">
            {/* Top-K */}
            <div className="form-group">
              <label className="form-label">
                <Sliders size={14} />
                <span>Retrieval TOP_K</span>
              </label>
              <input
                type="number"
                min="1"
                max="20"
                value={topK}
                onChange={(e) => setTopK(e.target.value)}
                className="win-input"
              />
              <span className="input-helper">Number of top chunks sent to LLM context (Default: 5).</span>
            </div>

            {/* Chunk Size */}
            <div className="form-group">
              <label className="form-label">
                <Layers size={14} />
                <span>Chunk Size (chars)</span>
              </label>
              <input
                type="number"
                min="100"
                max="3000"
                step="50"
                value={chunkSize}
                onChange={(e) => setChunkSize(e.target.value)}
                className="win-input"
              />
              <span className="input-helper">Characters per chunk block (Default: 800).</span>
            </div>
          </div>

          {/* Chunk Overlap & Embedding Model */}
          <div className="form-row-2col">
            <div className="form-group">
              <label className="form-label">Chunk Overlap (chars)</label>
              <input
                type="number"
                min="0"
                max="500"
                step="25"
                value={chunkOverlap}
                onChange={(e) => setChunkOverlap(e.target.value)}
                className="win-input"
              />
              <span className="input-helper">Overlap between consecutive chunks (Default: 100).</span>
            </div>

            <div className="form-group">
              <label className="form-label">Vector Embeddings</label>
              <input
                type="text"
                value={embeddingModel}
                disabled
                className="win-input input-disabled"
              />
              <span className="input-helper">Local SentenceTransformer (MiniLM-L6-v2).</span>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="win-btn win-btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="win-btn win-btn-primary" disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  <span>Saving...</span>
                </>
              ) : saveSuccess ? (
                <>
                  <Check size={14} className="text-success" />
                  <span>Saved!</span>
                </>
              ) : (
                <span>Save Settings</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
