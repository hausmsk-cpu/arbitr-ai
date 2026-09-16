"""Загрузка и сегментация документов кейса для RAG.

Собирает извлечённый текст из docs/knowledge в чанки для векторного поиска.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

# Каталог с извлечёнными текстами кейсов
KNOWLEDGE_ROOT = Path(__file__).resolve().parents[3] / "docs" / "knowledge"


@dataclass
class KnowledgeChunk:
    """Чанк текста с метаданными для векторного поиска."""

    text: str
    source: str          # имя файла
    case_id: str         # идентификатор кейса
    doc_type: str        # тип документа (request_fns, court_decision и т.д.)
    category: str        # категория (request, court_decision, registry...)
    chunk_index: int     # номер чанка в документе


class KnowledgeBaseLoader:
    """Загрузчик базы знаний из извлечённых текстов кейсов."""

    def __init__(self, chunk_size: int = 1500, overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _split_text(self, text: str) -> list[str]:
        """Разбиение текста на чанки с перекрытием (по абзацам)."""
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if not text:
            return []

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= self.chunk_size:
                current = f"{current}\n\n{para}".strip()
            else:
                if current:
                    chunks.append(current)
                # Если абзац больше чанка — режем по предложениям
                if len(para) > self.chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    buf = ""
                    for sent in sentences:
                        if len(buf) + len(sent) + 1 <= self.chunk_size:
                            buf = f"{buf} {sent}".strip()
                        else:
                            if buf:
                                chunks.append(buf)
                            buf = sent
                    if buf:
                        chunks.append(buf)
                else:
                    current = para

        if current:
            chunks.append(current)
        return chunks

    def load_all(self) -> list[KnowledgeChunk]:
        """Загружает все кейсы из docs/knowledge в чанки."""
        chunks: list[KnowledgeChunk] = []
        if not KNOWLEDGE_ROOT.exists():
            print(f"Каталог знаний не найден: {KNOWLEDGE_ROOT}")
            return chunks

        for case_dir in sorted(KNOWLEDGE_ROOT.iterdir()):
            if not case_dir.is_dir():
                continue
            meta_file = case_dir / "case_metadata.json"
            if not meta_file.exists():
                continue

            metadata = json.loads(meta_file.read_text(encoding="utf-8"))
            case_id = case_dir.name

            for doc in metadata:
                text = doc.get("text", "").strip()
                if not text:
                    continue
                doc_chunks = self._split_text(text)
                for idx, chunk_text in enumerate(doc_chunks):
                    chunks.append(
                        KnowledgeChunk(
                            text=chunk_text,
                            source=doc.get("filename", ""),
                            case_id=case_id,
                            doc_type=doc.get("doc_type", "unknown"),
                            category=doc.get("category", "other"),
                            chunk_index=idx,
                        )
                    )
        return chunks

    def stats(self) -> dict:
        """Статистика базы знаний."""
        chunks = self.load_all()
        docs = {(c.case_id, c.source) for c in chunks}
        by_type: dict[str, int] = {}
        for c in chunks:
            by_type[c.doc_type] = by_type.get(c.doc_type, 0) + 1
        return {
            "total_chunks": len(chunks),
            "total_documents": len(docs),
            "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
        }


if __name__ == "__main__":
    loader = KnowledgeBaseLoader()
    st = loader.stats()
    print(f"Чанков всего: {st['total_chunks']}")
    print(f"Документов всего: {st['total_documents']}")
    print("По типам:")
    for t, n in st["by_type"].items():
        print(f"  {t}: {n}")