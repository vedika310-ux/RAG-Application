import React, { useState, useRef } from "react";
import {
  Upload,
  X,
  FileCheck,
  AlertCircle,
  CheckCircle2,
  Loader2,
  FileText,
  FileSpreadsheet,
  FileCode,
  Layers,
} from "lucide-react";
import { uploadDocumentFile } from "../api";

const STEPS = [
  { id: 1, label: "Uploading..." },
  { id: 2, label: "Extracting..." },
  { id: 3, label: "Creating chunks..." },
  { id: 4, label: "Generating embeddings..." },
  { id: 5, label: "Indexing..." },
  { id: 6, label: "Ready" },
];

export default function UploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState("");
  const [successInfo, setSuccessInfo] = useState(null);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file) => {
    setErrorMsg("");
    setSuccessInfo(null);
    setCurrentStep(0);
    const validExts = [".pdf", ".docx", ".txt", ".csv", ".md", ".markdown"];
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!validExts.includes(ext)) {
      setErrorMsg(`Unsupported format '${ext}'. Please choose a PDF, DOCX, TXT, CSV, or Markdown file.`);
      return;
    }
    setSelectedFile(file);
  };

  const handleStartUpload = async () => {
    if (!selectedFile || isProcessing) return;

    setIsProcessing(true);
    setErrorMsg("");
    setSuccessInfo(null);

    // Step 1: Uploading
    setCurrentStep(1);

    // Simulated progress transitions to reflect RAG pipeline while backend executes
    const timer1 = setTimeout(() => setCurrentStep(2), 600); // Extracting
    const timer2 = setTimeout(() => setCurrentStep(3), 1200); // Chunking
    const timer3 = setTimeout(() => setCurrentStep(4), 1800); // Embeddings
    const timer4 = setTimeout(() => setCurrentStep(5), 2500); // Indexing

    try {
      const response = await uploadDocumentFile(selectedFile);
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);

      setCurrentStep(6); // Ready
      setSuccessInfo(response);
      setTimeout(() => {
        onUploadSuccess(response);
        handleClose();
      }, 1500);
    } catch (err) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      setCurrentStep(0);
      setErrorMsg(err.message || "Failed to process document");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    if (isProcessing) return;
    setSelectedFile(null);
    setErrorMsg("");
    setSuccessInfo(null);
    setCurrentStep(0);
    onClose();
  };

  return (
    <div className="modal-backdrop" onClick={handleClose}>
      <div className="fluent-modal upload-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-wrap">
            <Upload size={18} className="text-accent" />
            <h3 className="modal-title">Upload Document</h3>
          </div>
          <button className="modal-close-btn" onClick={handleClose} disabled={isProcessing}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {errorMsg && (
            <div className="error-callout">
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          {successInfo && (
            <div className="success-callout">
              <CheckCircle2 size={16} />
              <span>
                Document ready! {successInfo.chunks_count} chunks indexed in vector store.
              </span>
            </div>
          )}

          {!selectedFile ? (
            <div
              className={`dropzone-area ${dragActive ? "dropzone-active" : ""}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={36} className="dropzone-icon" />
              <p className="dropzone-text-main">
                Drag and drop your document here, or <span className="browse-link">Browse files</span>
              </p>
              <p className="dropzone-text-sub">
                Supports PDF, DOCX, TXT, CSV, and Markdown files
              </p>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden-file-input"
                accept=".pdf,.docx,.txt,.csv,.md,.markdown"
                onChange={handleFileChange}
              />
            </div>
          ) : (
            <div className="selected-file-card">
              <div className="file-info-col">
                <FileCheck size={24} className="text-accent" />
                <div className="file-details">
                  <div className="file-name">{selectedFile.name}</div>
                  <div className="file-meta">
                    {(selectedFile.size / 1024).toFixed(1)} KB •{" "}
                    {selectedFile.name.split(".").pop().toUpperCase()}
                  </div>
                </div>
              </div>
              {!isProcessing && currentStep !== 6 && (
                <button
                  className="win-btn win-btn-subtle btn-remove-file"
                  onClick={() => setSelectedFile(null)}
                >
                  Change
                </button>
              )}
            </div>
          )}

          {/* Progress Flow Indicator */}
          {currentStep > 0 && (
            <div className="rag-progress-container">
              <div className="progress-steps-list">
                {STEPS.map((step) => {
                  const isDone = currentStep > step.id || (currentStep === 6 && step.id === 6);
                  const isCurrent = currentStep === step.id;

                  return (
                    <div
                      key={step.id}
                      className={`step-item ${isDone ? "step-finished" : isCurrent ? "step-running" : "step-pending"}`}
                    >
                      <div className="step-indicator">
                        {isDone ? (
                          <CheckCircle2 size={14} className="text-success" />
                        ) : isCurrent ? (
                          <Loader2 size={14} className="animate-spin text-accent" />
                        ) : (
                          <span className="step-dot"></span>
                        )}
                      </div>
                      <span className="step-text">{step.label}</span>
                    </div>
                  );
                })}
              </div>

              {/* Progress bar line */}
              <div className="progress-bar-rail">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${(currentStep / 6) * 100}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button
            className="win-btn win-btn-secondary"
            onClick={handleClose}
            disabled={isProcessing}
          >
            Cancel
          </button>
          <button
            className="win-btn win-btn-primary"
            onClick={handleStartUpload}
            disabled={!selectedFile || isProcessing || currentStep === 6}
          >
            {isProcessing ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                <span>Processing RAG...</span>
              </>
            ) : (
              <>
                <Upload size={14} />
                <span>Start Ingestion</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
