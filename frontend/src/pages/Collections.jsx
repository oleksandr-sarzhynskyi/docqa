import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCollections, createCollection, deleteCollection } from "../api/client";

export default function Collections() {
  const [collections, setCollections] = useState([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadCollections();
  }, []);

  async function loadCollections() {
    setLoading(true);
    const data = await getCollections();
    setCollections(data);
    setLoading(false);
  }

  async function handleCreate(e) {
    e.preventDefault();
    if (!name.trim()) return;

    setCreating(true);
    try {
      await createCollection(name.trim());
      setName("");
      await loadCollections();
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(e, collectionId) {
    e.preventDefault();
    e.stopPropagation();

    if (!window.confirm("Delete this collection and all its documents? This can't be undone.")) return;

    await deleteCollection(collectionId);
    await loadCollections();
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Your collections</h1>
        <p className="page-subtitle">Group related documents and ask questions about them.</p>
      </div>

      <form className="inline-form" onSubmit={handleCreate}>
        <input
          type="text"
          placeholder="New collection name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={creating}>
          {creating ? "Creating..." : "Create"}
        </button>
      </form>

      {loading ? (
        <p className="muted">Loading...</p>
      ) : collections.length === 0 ? (
        <p className="muted">No collections yet — create one to get started.</p>
      ) : (
        <div className="card-grid">
          {collections.map((c) => (
            <Link key={c.id} to={`/collections/${c.id}`} className="collection-card">
              <div className="collection-card-header">
                <h3>{c.name}</h3>
                <button className="icon-btn danger" onClick={(e) => handleDelete(e, c.id)}>
                  Delete
                </button>
              </div>
              <span className="muted">Created {new Date(c.created_at).toLocaleDateString()}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}