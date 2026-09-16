"""Извлечение текста из PDF-кейса для базы знаний Arbitr AI."""

import json
import os
from pathlib import Path

from pypdf import PdfReader


CASE_DIR = Path(r"C:\Users\МЕГАЛИТ\Desktop\AI Dip\банкротство ФЛ\16-09-2026_14-44-25")
OUTPUT_DIR = Path(r"C:\Users\МЕГАЛИТ\Desktop\AI Dip\arbitr-ai\docs\knowledge\case_16-09-2026")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def classify_document(filename: str) -> dict[str, str]:
    """Классификация документа по имени файла."""
    name_lower = filename.lower()
    category = "other"
    doc_type = "unknown"

    if "реестр требований" in name_lower:
        category = "registry"
        doc_type = "creditor_registry"
    elif "анализ финансового" in name_lower:
        category = "analysis"
        doc_type = "financial_analysis"
    elif "признаки банкротства" in name_lower or "отсутствии" in name_lower:
        category = "analysis"
        doc_type = "bankruptcy_signs"
    elif "уведомление кредиторам" in name_lower:
        category = "notification"
        doc_type = "creditor_notification"
    elif "собрание кредиторов" in name_lower:
        category = "meeting"
        doc_type = "creditor_meeting"
    elif "свидетельство о смерти" in name_lower:
        category = "death_certificate"
        doc_type = "death_certificate"
    elif "отчет финансового" in name_lower:
        category = "report"
        doc_type = "manager_report"
    elif "определение" in name_lower and "завершении" in name_lower:
        category = "court_decision"
        doc_type = "completion_decision"
    elif "определение" in name_lower and "переходе" in name_lower:
        category = "court_decision"
        doc_type = "death_transition_decision"
    elif "решение о введении" in name_lower or "рид" in name_lower.replace(" ", ""):
        category = "court_decision"
        doc_type = "rig_intro_decision"
    elif "ходатайство" in name_lower:
        category = "petition"
        doc_type = "completion_petition"
    elif "закрытие счетов" in name_lower:
        category = "bank"
        doc_type = "account_closure"
    elif "запрос" in name_lower or "уведомление" in name_lower:
        category = "request"
        if "фнс" in name_lower:
            doc_type = "request_fns"
        elif "росреестр" in name_lower and "супруг" not in name_lower:
            doc_type = "request_rosreestr"
        elif "росреестр" in name_lower and "супруг" in name_lower:
            doc_type = "request_rosreestr_spouse"
        elif "егрн" in name_lower and "супруг" not in name_lower:
            doc_type = "request_egrn"
        elif "егрн" in name_lower and "супруг" in name_lower:
            doc_type = "request_egrn_spouse"
        elif "гибдд" in name_lower:
            doc_type = "request_gibdd"
        elif "гимс" in name_lower:
            doc_type = "request_gims"
        elif "гостехнадзор" in name_lower:
            doc_type = "request_gostekhnadzor"
        elif "депозитарий" in name_lower:
            doc_type = "request_depository"
        elif "загс" in name_lower:
            doc_type = "request_zags"
        elif "осфр" in name_lower:
            doc_type = "request_osfr"
        elif "земельн" in name_lower or "аренде зу" in name_lower:
            doc_type = "request_land"
        elif "росавиация" in name_lower:
            doc_type = "request_rosaviation"
        elif "росгварди" in name_lower:
            doc_type = "request_rosgvardiya"
        elif "роспатент" in name_lower:
            doc_type = "request_rospatent"
        elif "миграц" in name_lower:
            doc_type = "request_migration_mvd"
        elif "rsa" in name_lower or "обший" in name_lower:
            doc_type = "request_rsa"
        elif "пристав" in name_lower or "fsp" in name_lower.lower() or "осп риг" in name_lower:
            doc_type = "request_bailiff"
        elif "миров" in name_lower:
            doc_type = "request_magistrate"
        elif "сою" in name_lower or "суд общей" in name_lower:
            doc_type = "request_general_court"
        elif "бти" in name_lower:
            doc_type = "request_bti"
        elif "супруг" in name_lower and "красн" not in name_lower:
            doc_type = "request_spouse"
        elif "должни" in name_lower:
            doc_type = "request_debtor"
    else:
        doc_type = "other"

    return {"category": category, "doc_type": doc_type}


def extract_all():
    """Извлекает текст из всех PDF и сохраняет JSON + Markdown."""
    documents = []
    all_text_parts = []

    pdf_files = sorted(CASE_DIR.glob("*.pdf"))
    print(f"Найдено PDF: {len(pdf_files)}")

    for i, pdf_path in enumerate(pdf_files, 1):
        reader = PdfReader(str(pdf_path))
        n_pages = len(reader.pages)

        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n\n"

        classification = classify_document(pdf_path.name)

        doc_record = {
            "id": i,
            "filename": pdf_path.name,
            "category": classification["category"],
            "doc_type": classification["doc_type"],
            "pages": n_pages,
            "text": full_text.strip(),
            "text_length": len(full_text),
        }
        documents.append(doc_record)

        # Сохраняем текст каждого документа
        txt_name = pdf_path.stem + ".txt"
        (OUTPUT_DIR / txt_name).write_text(full_text.strip(), encoding="utf-8")

        all_text_parts.append(
            f"## Документ {i}: {pdf_path.name}\n"
            f"**Тип:** {classification['doc_type']} | **Страниц:** {n_pages}\n\n"
            f"{full_text.strip()}\n"
        )

        print(f"  [{i}/{len(pdf_files)}] {classification['doc_type']:30s} ({n_pages} стр.) {pdf_path.name}")

    # Сохраняем метаданные всех документов
    meta_path = OUTPUT_DIR / "case_metadata.json"
    meta_path.write_text(
        json.dumps(documents, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Сводный markdown
    summary_path = OUTPUT_DIR / "case_full_text.md"
    summary_path.write_text(
        "# Полный текст кейса: 16-09-2026\n\n"
        f"**Документов:** {len(documents)}\n\n"
        "---\n\n" + "\n---\n\n".join(all_text_parts),
        encoding="utf-8",
    )

    print(f"\nГотово! Сохранено в {OUTPUT_DIR}")
    print(f"  - {len(documents)} документов")
    print(f"  - metadata: {meta_path.name}")
    print(f"  - полный текст: {summary_path.name}")

    return documents


if __name__ == "__main__":
    extract_all()
