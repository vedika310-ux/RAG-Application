import React from "react";
import {
  FileText,
  FileSpreadsheet,
  FileCode,
  File,
  Upload,
  Trash2,
  ExternalLink,
  CheckCircle2,
  Globe,
  Radio,
} from "lucide-react";

export default function DocumentsTable({
  documents = [],
  selectedDocId,
  onSelectDoc,
  onOpenUpload,
  onOpenPreview,
  onDeleteDocument,
  searchQuery = "",
}) {
  const filteredDocs = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getFileIcon = (fileType) => {
    switch (fileType?.toUpperCase()) {
      case "PDF":
        return <FileText className="file-icon-pdf" size={16} />;
      case "DOCX":
        return <FileText className="file-icon-docx" size={16} />;
      case "CSV":
        return <FileSpreadsheet className="file-icon-csv" size={16} />;
      case "MD":
      case "MARKDOWN":
        return <FileCode className="file-icon-md" size={16} />;
      default:
        return <File className="file-icon-txt" size={16} />;
    }
  };

  const getBadgeClass = (fileType) => {
    switch (fileType?.toUpperCase()) {
      case "PDF":
        return "badge-pdf";
      case "DOCX":
        return "badge-docx";
      case "CSV":
        return "badge-csv";
      case "MD":
      case "MARKDOWN":
        return "badge-md";
      default:
        return "badge-txt";
    }
  };

  const selectedDoc = documents.find((d) => d.id === selectedDocId);

  return (
    <section className="fluent-card documents-section">
      <div className="section-toolbar">
        <div className="section-title-wrap">
          <h2 className="section-title">Your Documents</h2>
          <span className="section-count">({documents.length} files)</span>
        </div>

        <div className="table-actions-group">
          <button className="win-btn win-btn-primary" onClick={onOpenUpload}>
            <Upload size={15} />
            <span>Upload Document</span>
          </button>

          <button
            className="win-btn win-btn-secondary"
            disabled={!selectedDocId || selectedDocId === "all"}
            onClick={() => selectedDoc && onOpenPreview(selectedDoc)}
            title="Inspect extracted text & chunks"
          >
            <ExternalLink size={15} />
            <span>Open</span>
          </button>

          <button
            className="win-btn win-btn-danger"
            disabled={!selectedDocId || selectedDocId === "all"}
            onClick={() => selectedDocId && onDeleteDocument(selectedDocId)}
            title="Delete selected document"
          >
            <Trash2 size={15} />
            <span>Delete</span>
          </button>
        </div>
      </div>

      <div className="table-container">
        <table className="fluent-table">
          <thead>
            <tr>
              <th style={{ width: "40px" }}>Scope</th>
              <th>File</th>
              <th style={{ width: "90px" }}>Type</th>
              <th style={{ width: "90px" }}>Pages</th>
              <th style={{ width: "90px" }}>Chunks</th>
              <th style={{ width: "110px" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {/* Global option: All Documents */}
            <tr
              className={`table-row-global ${selectedDocId === "all" ? "row-selected" : ""}`}
              onClick={() => onSelectDoc("all")}
            >
              <td>
                <input
                  type="radio"
                  name="docSelection"
                  checked={selectedDocId === "all"}
                  onChange={() => onSelectDoc("all")}
                  className="win-radio"
                />
              </td>
              <td className="file-cell">
                <Globe size={16} className="file-icon-global" />
                <span className="file-name-bold">Ask Across All Documents (Global Knowledge Base)</span>
              </td>
              <td>
                <span className="type-badge badge-global">ALL</span>
              </td>
              <td>-</td>
              <td>
                {documents.reduce((acc, d) => acc + (d.chunks_count || 0), 0)}
              </td>
              <td>
                <span className="status-cell-ready">
                  <CheckCircle2 size={13} className="text-success" />
                  <span>Ready</span>
                </span>
              </td>
            </tr>

            {filteredDocs.length === 0 && documents.length > 0 && (
              <tr>
                <td colSpan="6" className="table-empty-cell">
                  No documents match your search "{searchQuery}".
                </td>
              </tr>
            )}

            {documents.length === 0 && (
              <tr>
                <td colSpan="6" className="table-empty-cell empty-welcome">
                  <div className="empty-state-content">
                    <Upload size={32} className="empty-icon" />
                    <p className="empty-title">No documents uploaded yet</p>
                    <p className="empty-subtitle">
                      Upload a PDF, DOCX, TXT, CSV, or Markdown file to start asking questions.
                    </p>
                    <button className="win-btn win-btn-primary" onClick={onOpenUpload}>
                      <Upload size={14} /> Upload Document
                    </button>
                  </div>
                </td>
              </tr>
            )}

            {filteredDocs.map((doc) => {
              const isSelected = selectedDocId === doc.id;
              return (
                <tr
                  key={doc.id}
                  className={`table-row-item ${isSelected ? "row-selected" : ""}`}
                  onClick={() => onSelectDoc(doc.id)}
                >
                  <td>
                    <input
                      type="radio"
                      name="docSelection"
                      checked={isSelected}
                      onChange={() => onSelectDoc(doc.id)}
                      className="win-radio"
                    />
                  </td>
                  <td className="file-cell">
                    {getFileIcon(doc.file_type)}
                    <span className="file-title" title={doc.filename}>
                      {doc.filename}
                    </span>
                    <span className="file-size-hint">({doc.file_size})</span>
                  </td>
                  <td>
                    <span className={`type-badge ${getBadgeClass(doc.file_type)}`}>
                      {doc.file_type}
                    </span>
                  </td>
                  <td>{doc.pages !== null && doc.pages !== undefined ? doc.pages : "-"}</td>
                  <td>{doc.chunks_count}</td>
                  <td>
                    <span className="status-cell-ready">
                      <CheckCircle2 size={13} className="text-success" />
                      <span>{doc.status || "Ready"}</span>
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
