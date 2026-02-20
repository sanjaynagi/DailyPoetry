ALTER TABLE poems
ADD COLUMN IF NOT EXISTS editorial_status TEXT NOT NULL DEFAULT 'pending';

CREATE INDEX IF NOT EXISTS idx_poems_editorial_status ON poems(editorial_status);
