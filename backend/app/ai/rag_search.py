"""RAG-поиск по базе знаний Arbitr AI.

Лёгкая реализация без внешних векторных БД:
- индексация чанков в памяти (загрузка из docs/knowledge)
- TF-IDF-подобный поиск с нормализацией русских словоформ
- ранжирование по релевантности + буст по типу документа
"""

import re
import string
from collections import Counter
from functools import lru_cache
from math import log

from app.ai.knowledge_base import KnowledgeBaseLoader, KnowledgeChunk

# Стоп-слова русского языка (служебные)
STOP_WORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
    "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
    "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще",
    "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли",
    "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь",
    "опять", "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может",
    "они", "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя", "их",
    "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз", "тоже", "себе",
    "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого",
    "какой", "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем",
    "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех", "никогда", "можно",
    "при", "об", "другой", "хоть", "после", "над", "больше", "тот", "через",
    "эти", "нас", "про", "всего", "них", "какая", "много", "разве", "три",
    "эту", "моя", "впрочем", "хорошо", "свою", "этой", "перед", "иногда",
    "лучше", "чуть", "том", "нельзя", "такой", "им", "более", "всегда",
    "конечно", "всю", "между", "стать", "должен", "представлен", "настоящим",
}

# Простая стемминг-нормализация: убираем окончания
STEM_SUFFIXES = (
    "иями", "ями", "ямии", "ам", "ами", "ах", "ов", "ев", "ей", "ий",
    "ая", "яя", "ое", "ее", "ие", "ые", "ого", "его", "ому", "ему",
    "ым", "им", "ом", "ем", "ую", "юю", "ою", "ею", "ах", "ях",
    "ы", "и", "а", "я", "о", "е", "у", "ю", "ь", "й",
)


def normalize_word(word: str) -> str:
    """Нормализация слова: нижний регистр, убираем пунктуацию."""
    word = word.strip(string.punctuation + "«»—–«»")
    return word.lower()


def stem_word(word: str) -> str:
    """Простой стеммер: отрезаем одно окончание."""
    if len(word) <= 3:
        return word
    for suffix in STEM_SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> list[str]:
    """Токенизация текста: слова → стеммы."""
    words = re.findall(r"[а-яёa-z0-9]+", text.lower(), flags=re.IGNORECASE)
    return [stem_word(w) for w in words if w not in STOP_WORDS and len(w) > 2]


class RagSearch:
    """Поиск по базе знаний (TF-IDF)."""

    def __init__(self) -> None:
        self.chunks: list[KnowledgeChunk] = []
        self._index: list[dict[str, float]] = []   # tf per chunk
        self._df: Counter = Counter()              # document frequency
        self._idf: dict[str, float] = {}
        self._doc_norms: list[float] = []

    # === Индексация ===

    def build_index(self, chunks: list[KnowledgeChunk] | None = None) -> None:
        """Построение индекса из чанков базы знаний."""
        if chunks is None:
            loader = KnowledgeBaseLoader()
            chunks = loader.load_all()
        self.chunks = chunks

        # TF для каждого чанка
        tokenized: list[list[str]] = []
        for ch in chunks:
            toks = tokenize(ch.text)
            tokenized.append(toks)
            for t in set(toks):
                self._df[t] += 1

        n_docs = len(chunks)
        self._idf = {
            t: log(1 + n_docs / (1 + freq)) for t, freq in self._df.items()
        }

        self._index = []
        self._doc_norms = []
        for toks in tokenized:
            tf = Counter(toks)
            weights = {t: (1 + log(tf[t])) * self._idf.get(t, 0.0) for t in tf}
            norm = sum(w * w for w in weights.values()) ** 0.5 or 1.0
            self._index.append(weights)
            self._doc_norms.append(norm)

    # === Поиск ===

    def query(self, query_text: str, top_k: int = 5) -> list[KnowledgeChunk]:
        """Поиск релевантных чанков по текстовому запросу."""
        if not self._index:
            self.build_index()

        q_tokens = tokenize(query_text)
        if not q_tokens:
            return []

        q_tf = Counter(q_tokens)
        q_weights = {t: (1 + log(q_tf[t])) * self._idf.get(t, 0.0) for t in q_tf}
        q_norm = sum(w * w for w in q_weights.values()) ** 0.5 or 1.0

        scores: list[float] = []
        for doc_weights, doc_norm in zip(self._index, self._doc_norms, strict=False):
            score = 0.0
            matched = 0
            for term, qw in q_weights.items():
                if term in doc_weights:
                    score += qw * doc_weights[term]
                    matched += 1
            score = score / (q_norm * doc_norm) if doc_norm else 0.0
            if matched:
                score *= 1.0 + 0.15 * matched  # маленький буст за количество совпадений
            scores.append(score)

        ranked = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:top_k]

        return [self.chunks[i] for i in ranked if scores[i] > 0.0]

    def search_by_type(self, doc_type: str, top_k: int = 10) -> list[KnowledgeChunk]:
        """Поиск чанков по типу документа."""
        return [ch for ch in self.chunks if ch.doc_type == doc_type][:top_k]

    def stats(self) -> dict:
        return {
            "chunks": len(self.chunks),
            "terms": len(self._idf),
            "documents": len({(c.case_id, c.source) for c in self.chunks}),
        }


@lru_cache
def get_rag_search() -> RagSearch:
    """Синглтон RAG-поиска (индексация при первом обращении)."""
    search = RagSearch()
    search.build_index()
    return search