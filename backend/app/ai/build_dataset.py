"""Создание обучающего датасета на основе реального кейса."""

import json
from pathlib import Path

from app.ai.knowledge_base import KnowledgeBaseLoader

OUTPUT_DIR = Path(r"C:\Users\МЕГАЛИТ\Desktop\AI Dip\arbitr-ai\docs\knowledge")
DATASET_PATH = OUTPUT_DIR / "training_dataset.jsonl"


def build_training_dataset() -> None:
    """Формирует датасет для тонкой настройки / few-shot обучения LLM."""
    loader = KnowledgeBaseLoader()
    chunks = loader.load_all()

    # Группируем чанки по документам
    by_doc: dict[tuple[str, str], list] = {}
    for ch in chunks:
        key = (ch.case_id, ch.source)
        by_doc.setdefault(key, []).append(ch)

    records = []
    for (case_id, source), doc_chunks in sorted(by_doc.items()):
        doc_type = doc_chunks[0].doc_type
        full_text = "\n".join(c.text for c in doc_chunks)

        typ = "Обучающий пример для генерации юридических документов"
        record = {
            "instruction": (
                f"Документ типа «{doc_type}» из дела о банкротстве. "
                f"Используй как образец при генерации аналогичных документов."
            ),
            "input": f"Источник: {source}, дело: {case_id}",
            "output": full_text,
            "metadata": {
                "source": source,
                "case_id": case_id,
                "doc_type": doc_type,
                "chunks": len(doc_chunks),
                "category": doc_chunks[0].category,
            },
        }
        records.append(record)

    with DATASET_PATH.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Статистика
    types: dict[str, int] = {}
    for rec in records:
        t = rec["metadata"]["doc_type"]
        types[t] = types.get(t, 0) + 1

    print(f"Датасет сохранён: {DATASET_PATH}")
    print(f"Всего записей: {len(records)}")
    print("\nПо типам документов:")
    for t, n in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")


if __name__ == "__main__":
    build_training_dataset()