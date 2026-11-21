CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE manual_pages (
    id           INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    manual_title TEXT NOT NULL,
    page_number  INT NOT NULL,
    content      TEXT NOT NULL,
    embedding    vector(384) NOT NULL,
    UNIQUE (manual_title, page_number)
);