from rank_bm25 import BM25Okapi
import re

def tokenize_code(text: str) -> list[str]:
    """
    Tokenizes code text for BM25.
    Splits on spaces, underscores, camelCase, and punctuation.
    """
    # Split camelCase: "getUserById" -> "get User By Id"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Split on common code delimiters
    text = re.sub(r'[_\-\.\(\)\[\]\{\}:,]', ' ', text)
    tokens = text.lower().split()
    return [t for t in tokens if len(t) > 1]


def build_sparse_vectors(corpus: list[str]) -> tuple[BM25Okapi, list[list[str]]]:
    """
    Builds BM25 index over the entire corpus.
    Returns the BM25 object and tokenized corpus.
    """
    tokenized_corpus = [tokenize_code(doc) for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25, tokenized_corpus


def get_sparse_vector_for_qdrant(text: str, vocab: list[str]) -> dict:
    """
    Creates a sparse vector dict compatible with Qdrant's sparse format.
    { indices: [...], values: [...] }
    """
    tokens = tokenize_code(text)
    token_freq = {}
    for token in tokens:
        if token in vocab:
            idx = vocab.index(token)
            token_freq[idx] = token_freq.get(idx, 0) + 1
    
    return {
        "indices": list(token_freq.keys()),
        "values": [float(v) for v in token_freq.values()]
    }
