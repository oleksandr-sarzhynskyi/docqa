import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  getCollection,
  listDocuments,
  uploadDocument,
  queryCollection,
  deleteDocument,
  viewDocument,
} from "../api/client";

const STATUS_LABEL = { processing: "Processing", ready: "Ready", failed: "Failed" };

export default function CollectionDetail() {
  const { id } = useParams();
  const [collection, setCollection] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [thread, setThread] = useState([]);
  const [queryError, setQueryError] = useState("");

  const fileInputRef = useRef(null);
  const cancelledRef = useRef(false);

  async function pollDocuments() {
    while (!cancelledRef.current) {
      const data = await listDocuments(id);
      if (cancelledRef.current) return;
      setDocuments(data);

      if (!data.some((d) => d.status === "processing")) return;
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }
  }

  useEffect(() => {
    cancelledRef.current = false;
    getCollection(id).then(setCollection);
    pollDocuments();

    return () => {
      cancelledRef.current = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    setUploadError("");
    setUploading(true);
    try {
      await uploadDocument(id, file);
      cancelledRef.current = false;
      await pollDocuments();
    } catch (err) {
      setUploadError("Upload failed. Make sure it's a PDF.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDelete(documentId) {
    if (!window.confirm("Delete this document? This can't be undone.")) return;
    await deleteDocument(documentId);
    cancelledRef.current = false;
    await pollDocuments();
  }

  async function handleAsk(e) {
    e.preventDefault();
    if (!question.trim() || asking) return;

    const asked = question.trim();
    setQuestion("");
    setQueryError("");
    setAsking(true);

    try {
      const result = await queryCollection(id, asked);
      setThread((prev) => [...prev, { question: asked, ...result }]);
    } catch (err) {
      setQueryError("Something went wrong answering that question.");
    } finally {
      setAsking(false);
    }
  }

  const readyCount = documents.filter((d) => d.status === "ready").length;

  return (
    <div className="page">
      <Link to="/collections" className="back-link">← All collections</Link>

      <div className="page-header">
        <h1>{collection ? collection.name : "Loading..."}</h1>
        <p className="page-subtitle">
          {documents.length} document{documents.length === 1 ? "" : "s"} · {readyCount} ready
        </p>
      </div>

      <section className="panel">
        <div className="panel-header">
          <h2>Documents</h2>
          <label className="btn-primary upload-btn">
            {uploading ? "Uploading..." : "Upload PDF"}
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf"
              onChange={handleUpload}
              disabled={uploading}
              hidden
            />
          </label>
        </div>

        {uploadError && <p className="form-error">{uploadError}</p>}

        {documents.length === 0 ? (
          <p className="muted">No documents yet — upload a PDF to get started.</p>
        ) : (
          <ul className="document-list">
            {documents.map((doc) => (
              <li key={doc.id} className="document-row">
                <span className="document-name">{doc.original_filename}</span>
                <div className="document-actions">
                  <span className={`status-badge status-${doc.status}`}>
                    {STATUS_LABEL[doc.status] || doc.status}
                  </span>
                  {doc.status === "ready" && (
                    <button className="icon-btn" onClick={() => viewDocument(doc.id)}>
                      View
                    </button>
                  )}
                  <button className="icon-btn danger" onClick={() => handleDelete(doc.id)}>
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel">
        <h2>Ask a question</h2>

        <div className="thread">
          {thread.length === 0 && (
            <p className="muted">Ask anything about the documents in this collection once they're ready.</p>
          )}

          {thread.map((turn, i) => (
            <div className="turn" key={i}>
              <div className="bubble bubble-question">{turn.question}</div>
              <div className="bubble bubble-answer">
                <p>{turn.answer}</p>
                {turn.citations && turn.citations.length > 0 && (
                  <div className="citations">
                    {turn.citations.map((c, j) => (
                      <span className="citation-pill" key={j}>
                        {c.filename} · p.{c.page}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {queryError && <p className="form-error">{queryError}</p>}

        <form className="ask-form" onSubmit={handleAsk}>
          <input
            type="text"
            placeholder={
              readyCount === 0
                ? "Waiting for a document to finish processing..."
                : "Ask a question about these documents"
            }
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={readyCount === 0 || asking}
          />
          <button className="btn-primary" type="submit" disabled={readyCount === 0 || asking}>
            {asking ? "Thinking..." : "Ask"}
          </button>
        </form>
      </section>
    </div>
  );
}