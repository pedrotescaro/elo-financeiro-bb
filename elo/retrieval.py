"""Recuperação local por conceitos curados e similaridade de termos, sem LLM.

O vocabulário aproxima paráfrases simples. Não é um modelo de embeddings e sua
cobertura não foi avaliada em perguntas reais de usuários.
"""
from collections import Counter
from copy import deepcopy
from math import log, sqrt
import re
import unicodedata


_CONCEPTS = {
    "saldo": "saldo dinheiro caixa recursos",
    "calendário": "calendario vencimento vencimentos data datas conta contas compromisso compromissos",
    "recebimento": "recebimento recebimentos renda salario salarios entrada entradas",
    "margem": "margem reserva folga aperto curto falta negativo negativa",
    "consentimento": "consentimento autorizar autorizado autorizacao leitura acesso compartilhamento permissao revogacao revogar desativar cancelar",
    "compra": "compra comprar celular produto adiar preco",
    "parcelamento": "parcela parcelas parcelado parcelamento juros",
    "verificação": "verificar verificacao conferir confirme identidade destinatario urgencia pressa suspeito golpe golpes fraude pix transferencia",
}
_STOPWORDS = frozenset(
    "a ao aos as ate com como da das de do dos e em entre esse esta este ha na nas nao no nos "
    "o os ou para pela pelas pelo pelos por que se sem seu seus sua suas um uma uns umas "
    "antes depois neste nesta nesse nessa sobre pode podem sera sao ser tem ter quero preciso".split()
)
LIMITATION = (
    "Recuperação local por conceitos e similaridade de termos em uma base pequena. "
    "Não usa embeddings, não gera respostas e não garante cobertura de perguntas inéditas. "
    "As fontes não são atualizadas pela internet durante a consulta."
)


def _words(text: str) -> list[str]:
    """Normaliza acentos e extrai palavras relevantes do português."""
    plain = "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))
    return [word for word in re.findall(r"[a-z0-9]+", plain) if word not in _STOPWORDS]


def _concepts(words: set[str]) -> set[str]:
    """Reconhece apenas os conceitos explicitamente revisados no vocabulário."""
    return {name for name, aliases in _CONCEPTS.items() if words.intersection(aliases.split())}


def _features(text: str) -> Counter:
    """Expande termos com conceitos para aproximar paráfrases simples."""
    words = _words(text)
    features = Counter(words)
    features.update({"concept:" + concept: 2 for concept in _concepts(set(words))})
    return features


class LocalRetriever:
    """Indexa a base uma vez e recupera cópias dos trechos, sem leitura por pedido."""

    def __init__(self, documents: list[dict]) -> None:
        self.documents = deepcopy(documents)
        self.features = [_features(doc["title"] + " " + doc["text"]) for doc in self.documents]
        counts = Counter(term for features in self.features for term in features)
        self.idf = {term: 1 + log((1 + len(documents)) / (1 + count)) for term, count in counts.items()}
        self.vectors = [self._vector(features) for features in self.features]

    def _vector(self, features: Counter) -> dict[str, float]:
        """Calcula pesos TF-IDF; esses pesos não representam valores financeiros."""
        weights = {term: count * self.idf.get(term, 1) for term, count in features.items()}
        norm = sqrt(sum(weight * weight for weight in weights.values()))
        return {term: weight / norm for term, weight in weights.items()} if norm else {}

    def retrieve(self, query: str, topic: str, limit: int = 3) -> dict:
        """Ordena trechos relacionados ou usa o tópico quando não há correspondência."""
        if not isinstance(query, str) or not isinstance(topic, str) or type(limit) is not int or not 1 <= limit <= 5:
            raise ValueError("Consulta de orientação inválida.")
        query = query[:2000]
        terms = _features(query)
        vector = self._vector(terms)
        candidates = [i for i, doc in enumerate(self.documents) if topic in doc["topics"]]
        ranked = []
        for index in candidates:
            score = sum(weight * self.vectors[index].get(term, 0) for term, weight in vector.items())
            if score >= 0.08:
                ranked.append((score, index))
        ranked.sort(key=lambda pair: (-pair[0], self.documents[pair[1]]["id"]))
        selected = [index for _, index in ranked[:limit]] if ranked else candidates[:limit]
        found = []
        for index in selected:
            document = deepcopy(self.documents[index])
            document["matched_concepts"] = sorted(
                term.removeprefix("concept:") for term in terms.keys() & self.features[index].keys()
                if term.startswith("concept:")
            ) if ranked else []
            found.append(document)
        return {"topic": topic, "query": query, "documents": found,
                "retrieval_mode": "local_concepts" if ranked else "topic_fallback", "limitation": LIMITATION}
