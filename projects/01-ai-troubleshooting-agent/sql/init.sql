CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunks (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  service TEXT NOT NULL,
  source TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536)
);

CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
ON knowledge_chunks
USING ivfflat (embedding vector_cosine_ops);
