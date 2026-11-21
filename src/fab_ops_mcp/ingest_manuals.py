"""
Ingest script: reads the equipment manuals, turns every page into a vector
(an embedding), and stores the pages in the manual_pages table.

Run it with:  uv run python -m fab_ops_mcp.ingest_manuals
"""

import os
from pathlib import Path

import psycopg
from fastembed import TextEmbedding
from pgvector.psycopg import register_vector


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://fab:fab@localhost:55432/fab_ops",
)

PROJECT_FOLDER = Path(__file__).resolve().parents[2]
MANUALS_FOLDER = PROJECT_FOLDER / "manuals"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
PAGE_MARKER = "## Page "


def read_manual_pages(manual_file: Path) -> list[dict]:
    manual_text = manual_file.read_text(encoding="utf-8")

    first_line = manual_text.splitlines()[0]
    manual_title = first_line.removeprefix("# ").strip()

    pages = []
    page_blocks = manual_text.split(PAGE_MARKER)[1:]  # [0] is the title, skip it
    for page_block in page_blocks:
        page_number_text, page_content = page_block.split("\n", 1)
        page = {
            "manual_title": manual_title,
            "page_number": int(page_number_text),
            "content": page_content.strip(),
        }
        pages.append(page)
    return pages


def main() -> None:
    # 1. Read every page of every manual
    all_pages = []
    for manual_file in sorted(MANUALS_FOLDER.glob("*.md")):
        all_pages.extend(read_manual_pages(manual_file))

    # 2. Turn each page's text into a vector of 384 numbers
    embedding_model = TextEmbedding(EMBEDDING_MODEL_NAME)
    page_texts = [page["content"] for page in all_pages]
    page_embeddings = list(embedding_model.embed(page_texts))

    # 3. Store each page together with its vector
    with psycopg.connect(DATABASE_URL) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE manual_pages RESTART IDENTITY")
            for page, page_embedding in zip(all_pages, page_embeddings):
                cursor.execute(
                    "INSERT INTO manual_pages (manual_title, page_number, content, embedding) "
                    "VALUES (%s, %s, %s, %s)",
                    (page["manual_title"], page["page_number"], page["content"], page_embedding),
                )

    print(f"Stored {len(all_pages)} manual pages with embeddings.")


if __name__ == "__main__":
    main()