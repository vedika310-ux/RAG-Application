import React, { useState, useEffect } from "react";
import {
  X,
  FileText,
  FileSpreadsheet,
  FileCode,
  File,
  Layers,
  Database,
  BookOpen,
  Calendar,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { fetchDocumentDetails, fetchDocumentChunks } from "../api";

export default function DocumentPreviewModal({ isOpen, document, onClose }) {
  const [activeTab, setActiveTab] = useState("pages"); // 'pages' | 'chunks'
  const [selectedPageIndex, setSelectedPageIndex] = useState(0);
  const [docDetails, setDocDetails] = useState(null);
  const [chunksList, setChunksList] = useState([]);
  const [isLoadingChunks, setIsLoadingChunks] = useState(false);

  useEffect(() => {
    if (document?.id && isOpen) {
      // Load details
      fetchDocumentDetails(document.id)
        .then((data) => setDocDetails(data))
        .catch((err) => console.error("Error loading doc details:", err));

      // Load chunks
      setIsLoadingChunks(true);
      fetchDocumentChunks(document.id)
        .then((data) => setChunksList(data.chunks || []))
        .catch((err) => console.error("Error loading chunks:", err))
        .finally(() => setIsLoadingChunks(false));
    }
  }, [document?.id, isOpen]);

  if (!isOpen || !document) return null;

  const pages = docDetails?.preview_pages || [];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="fluent-modal preview-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-title-wrap">
            <BookOpen size={18} className="text-accent" />
            <h3 className="modal-title">Document Inspection & Preview</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Metadata Banner */}
        <div className="preview-meta-banner">
          <div className="meta-card-item">
            <span className="meta-label">FILENAME</span>
            <span className="meta-value text-bold" title={document.filename}>
              {document.filename}
            </span>
          </div>

          <div className="meta-card-item">
            <span className="meta-label">FILE TYPE</span>
            <span className="meta-value badge-pill">{document.file_type}</span>
          </div>

          <div className="meta-card-item">
            <span className="meta-label">FILE SIZE</span>
            <span className="meta-value">{document.file_size}</span>
          </div>

          <div className="meta-card-item">
            <span className="meta-label">PAGES</span>
            <span className="meta-value">
              {document.pages !== null && document.pages !== undefined ? document.pages : "N/A"}
            </span>
          </div>

          <div className="meta-card-item">
            <span className="meta-label">CHUNKS</span>
            <span className="meta-value text-accent">{document.chunks_count}</span>
          </div>

          <div className="meta-card-item">
            <span className="meta-label">STATUS</span>
            <span className="meta-value status-badge-sm">
              <CheckCircle2 size={12} className="text-success" />
              {document.status || "Ready"}
            </span>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="preview-tabs-row">
          <button
            className={`tab-btn ${activeTab === "pages" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("pages")}
          >
            <BookOpen size={14} />
            <span>Extracted Text & Pages</span>
          </button>

          <button
            className={`tab-btn ${activeTab === "chunks" ? "tab-active" : ""}`}
            onClick={() => setActiveTab("chunks")}
          >
            <Database size={14} />
            <span>Vector Chunks ({chunksList.length})</span>
          </button>
        </div>

        {/* Tab 1: Pages Inspection */}
        {activeTab === "pages" && (
          <div className="preview-body-layout">
            {pages.length > 0 ? (
              <>
                {/* Page Selector Sidebar */}
                <div className="pages-sidebar">
                  <div className="sidebar-header">PAGES</div>
                  <div className="pages-list">
                    {pages.map((p, idx) => (
                      <button
                        key={idx}
                        className={`page-pill-btn ${selectedPageIndex === idx ? "page-active" : ""}`}
                        onClick={() => setSelectedPageIndex(idx)}
                      >
                        Page {p.page}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Page Content Viewer */}
                <div className="page-content-viewer">
                  <div className="viewer-header">
                    <span>Page {pages[selectedPageIndex]?.page} Preview</span>
                  </div>
                  <pre className="extracted-text-pre">
                    {pages[selectedPageIndex]?.text || "No text on this page."}
                  </pre>
                </div>
              </>
            ) : (
              <div className="single-text-viewer">
                <div className="viewer-header">Extracted Text Content</div>
                <pre className="extracted-text-pre">
                  {docDetails?.full_preview_snippet || "Text loaded."}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Chunks Inspection */}
        {activeTab === "chunks" && (
          <div className="chunks-tab-viewer">
            {isLoadingChunks ? (
              <div className="loading-chunks-wrap">
                <Loader2 size={24} className="animate-spin text-accent" />
                <span>Loading indexed chunks from ChromaDB...</span>
              </div>
            ) : (
              <div className="chunks-grid-scroll">
                {chunksList.map((chunk, idx) => (
                  <div key={chunk.chunk_id || idx} className="chunk-inspector-card">
                    <div className="chunk-card-top">
                      <span className="chunk-tag">#{chunk.chunk_index || idx + 1}</span>
                      <span className="chunk-id-text">{chunk.chunk_id}</span>
                      {chunk.page && (
                        <span className="chunk-page-tag">Page {chunk.page}</span>
                      )}
                      {chunk.section && (
                        <span className="chunk-page-tag">{chunk.section}</span>
                      )}
                      {chunk.row_range && (
                        <span className="chunk-page-tag">{chunk.row_range}</span>
                      )}
                    </div>
                    <pre className="chunk-card-text">{chunk.text}</pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="modal-footer">
          <button className="win-btn win-btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
