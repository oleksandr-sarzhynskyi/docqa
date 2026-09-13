const BASE_URL = "http://localhost:8000";

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token");
  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

export async function login(email, password) {
  const formData = new FormData();
  formData.append("username", email);
  formData.append("password", password);

  return apiFetch("/auth/login", {
    method: "POST",
    body: formData,
  });
}

export async function signup(email, password) {
  return apiFetch("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getCollections() {
  return apiFetch("/collections/", { method: "GET" });
}

export async function createCollection(name) {
  return apiFetch("/collections/", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function listDocuments(collectionId) {
  return apiFetch(`/collections/${collectionId}/documents`, {
    method: "GET",
  });
}

export async function uploadDocument(collectionId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch(`/documents/upload?collection_id=${collectionId}`, {
    method: "POST",
    body: formData,
  });
}

export async function queryCollection(collectionId, question) {
  return apiFetch(`/collections/${collectionId}/query`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export async function getCollection(collectionId) {
  return apiFetch(`/collections/${collectionId}`, { method: "GET" });
}

export async function deleteDocument(documentId) {
  return apiFetch(`/documents/${documentId}`, { method: "DELETE" });
}

export async function viewDocument(documentId) {
  const token = localStorage.getItem("token");
  const response = await fetch(`${BASE_URL}/documents/${documentId}/file`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) throw new Error(`Request failed: ${response.status}`);

  const blob = await response.blob();
  window.open(URL.createObjectURL(blob), "_blank");
}

export async function deleteCollection(collectionId) {
  return apiFetch(`/collections/${collectionId}`, { method: "DELETE" });
}