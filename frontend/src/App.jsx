import React, { useState, useEffect } from "react";
import TopNav from "./components/TopNav";
import DashboardCards from "./components/DashboardCards";
import DocumentsTable from "./components/DocumentsTable";
import QuestionWorkspace from "./components/QuestionWorkspace";
import AnswerPanel from "./components/AnswerPanel";
import RetrievalInspector from "./components/RetrievalInspector";
import UploadModal from "./components/UploadModal";
import DocumentPreviewModal from "./components/DocumentPreviewModal";
import SettingsModal from "./components/SettingsModal";
import {
  fetchHealth,
  fetchDocuments,
  deleteDocument,
  askQuestion,
} from "./api";
import "./App.css";

export default function App() {
  const [serverStatus, setServerStatus] = useState("checking");
  const [healthData, setHealthData] = useState({
    documents_count: 0,
    chunks_count: 0,
    questions_count: 0,
    embedding_model: "all-MiniLM-L6-v2",
  });
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Modals state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [previewDoc, setPreviewDoc] = useState(null);

  // Question & RAG state
  const [isAsking, setIsAsking] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [retrievedSources, setRetrievedSources] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");

  const loadData = async () => {
    try {
      const health = await fetchHealth();
      setServerStatus("online");
      setHealthData(health);
    } catch (err) {
      setServerStatus("offline");
      console.warn("Backend not yet reachable at http://127.0.0.1:8000");
    }

    try {
      const docs = await fetchDocuments();
      setDocuments(docs);
      // If currently selected doc was deleted or invalid, default to 'all'
      if (selectedDocId !== "all" && !docs.some((d) => d.id === selectedDocId)) {
        setSelectedDocId(docs.length > 0 ? docs[0].id : "all");
      }
    } catch (err) {
      console.error("Failed to load documents list:", err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 6000);
    return () => clearInterval(interval);
  }, [selectedDocId]);

  const handleSelectDoc = (docId) => {
    setSelectedDocId(docId);
  };

  const handleOpenPreview = (doc) => {
    setPreviewDoc(doc);
    setIsPreviewOpen(true);
  };

  const handleDelete = async (docId) => {
    const docToDelete = documents.find((d) => d.id === docId);
    if (!docToDelete) return;

    if (!window.confirm(`Are you sure you want to delete '${docToDelete.filename}' and all its vector embeddings?`)) {
      return;
    }

    try {
      await deleteDocument(docId);
      loadData();
      if (selectedDocId === docId) {
        setSelectedDocId("all");
      }
    } catch (err) {
      alert("Delete failed: " + err.message);
    }
  };

  const handleAskQuestion = async (question) => {
    setIsAsking(true);
    setErrorMessage("");
    setCurrentQuestion(question);
    setCurrentAnswer("");
    setRetrievedSources([]);

    try {
      const res = await askQuestion(question, selectedDocId);
      setCurrentAnswer(res.answer);
      setRetrievedSources(res.sources || []);
      // Refresh metrics
      fetchHealth().then((h) => setHealthData(h)).catch(() => {});
    } catch (err) {
      setErrorMessage(err.message || "Failed to retrieve and answer question.");
      setCurrentAnswer(
        `⚠️ Error processing question: ${err.message}. Please check backend logs or settings.`
      );
    } finally {
      setIsAsking(false);
    }
  };

  const selectedDoc = documents.find((d) => d.id === selectedDocId);

  return (
    <div className="win11-app-container">
      {/* Top Navigation Bar */}
      <TopNav
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onOpenSettings={() => setIsSettingsOpen(true)}
        serverStatus={serverStatus}
        embeddingModel={healthData.embedding_model}
      />

      <main className="dashboard-main-content">
        {/* Dashboard Metric Cards */}
        <DashboardCards
          documentsCount={healthData.documents_count}
          chunksCount={healthData.chunks_count}
          questionsCount={healthData.questions_count}
        />

        {/* Main Grid: Left / Top Documents Table */}
        <DocumentsTable
          documents={documents}
          selectedDocId={selectedDocId}
          onSelectDoc={handleSelectDoc}
          onOpenUpload={() => setIsUploadOpen(true)}
          onOpenPreview={handleOpenPreview}
          onDeleteDocument={handleDelete}
          searchQuery={searchQuery}
        />

        {/* Question Workspace */}
        <QuestionWorkspace
          selectedDoc={selectedDoc}
          selectedDocId={selectedDocId}
          onAskQuestion={handleAskQuestion}
          isLoading={isAsking}
        />

        {/* Answer Panel */}
        <AnswerPanel
          answer={currentAnswer}
          sourcesCount={retrievedSources.length}
          isLoading={isAsking}
          lastQuestion={currentQuestion}
        />

        {/* Dedicated Retrieval Inspector (Making RAG process visible) */}
        <RetrievalInspector
          question={currentQuestion}
          sources={retrievedSources}
          answer={currentAnswer}
          isLoading={isAsking}
        />
      </main>

      {/* Upload Modal with Progress Flow */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={(res) => {
          loadData();
          if (res?.document_id) {
            setSelectedDocId(res.document_id);
          }
        }}
      />

      {/* Document Inspection & Text Preview Modal */}
      <DocumentPreviewModal
        isOpen={isPreviewOpen}
        document={previewDoc}
        onClose={() => {
          setIsPreviewOpen(false);
          setPreviewDoc(null);
        }}
      />

      {/* Settings Dialog */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSettingsUpdated={loadData}
      />
    </div>
  );
}
