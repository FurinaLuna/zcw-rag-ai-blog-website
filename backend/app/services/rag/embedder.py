from functools import lru_cache

from loguru import logger

from app.core.config import settings


class Embedder:
    def __init__(self) -> None:
        self._model = None
        self._model_name = settings.embedding_model

    def _load_model(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self._model_name}")
            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self._model = None

    def encode(self, texts: list[str]) -> list[list[float]] | None:
        self._load_model()
        if self._model is None:
            return None
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def encode_single(self, text: str) -> list[float] | None:
        result = self.encode([text])
        if result is None:
            return None
        return result[0]

    @property
    def dim(self) -> int:
        return settings.embedding_dim


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
