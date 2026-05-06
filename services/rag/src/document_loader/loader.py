import io
import httpx
from abc import ABC, abstractmethod
from typing import AsyncIterator
from bs4 import BeautifulSoup
import html2text
from markdown import markdown
from pypdf import PdfReader
from loguru import logger
from ..schemas import DocumentMetadata, DocumentSource


class BaseDocumentLoader(ABC):
    """Abstract base class for document loaders."""

    @abstractmethod
    async def load(self, content: bytes, metadata: DocumentMetadata) -> AsyncIterator[dict]:
        """Load and yield document chunks."""
        pass


class MarkdownLoader(BaseDocumentLoader):
    """Loader for Markdown documents."""

    async def load(self, content: bytes, metadata: DocumentMetadata) -> AsyncIterator[dict]:
        text = content.decode("utf-8")
        html_body = markdown(text, extensions=["fenced_code", "tables"])
        plain_text = html2text.html2text(html_body)
        yield {
            "text": plain_text.strip(),
            "metadata": metadata.model_dump(exclude_none=True),
        }


class PDFLoader(BaseDocumentLoader):
    """Loader for PDF documents."""

    async def load(self, content: bytes, metadata: DocumentMetadata) -> AsyncIterator[dict]:
        try:
            pdf_reader = PdfReader(io.BytesIO(content))
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    page_metadata = DocumentMetadata(
                        **{
                            **metadata.model_dump(exclude_none=True),
                            "page": page_num,
                        }
                    )
                    yield {
                        "text": text.strip(),
                        "metadata": page_metadata.model_dump(exclude_none=True),
                    }
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise


class WebLoader(BaseDocumentLoader):
    """Loader for web pages."""

    async def load(self, content: bytes, metadata: DocumentMetadata) -> AsyncIterator[dict]:
        try:
            html = content.decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")

            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            text = soup.get_text(separator="\n", strip=True)
            lines = [line for line in text.split("\n") if line.strip()]
            cleaned_text = "\n".join(lines)

            yield {
                "text": cleaned_text,
                "metadata": metadata.model_dump(exclude_none=True),
            }
        except Exception as e:
            logger.error(f"Error loading web page: {e}")
            raise


class TextLoader(BaseDocumentLoader):
    """Loader for plain text documents."""

    async def load(self, content: bytes, metadata: DocumentMetadata) -> AsyncIterator[dict]:
        try:
            text = content.decode("utf-8")
            yield {
                "text": text.strip(),
                "metadata": metadata.model_dump(exclude_none=True),
            }
        except UnicodeDecodeError:
            text = content.decode("latin-1")
            yield {
                "text": text.strip(),
                "metadata": metadata.model_dump(exclude_none=True),
            }


class DocumentLoaderFactory:
    """Factory for creating document loaders based on source type."""

    _loaders = {
        DocumentSource.MARKDOWN: MarkdownLoader,
        DocumentSource.PDF: PDFLoader,
        DocumentSource.WEB: WebLoader,
        DocumentSource.TEXT: TextLoader,
    }

    @classmethod
    def get_loader(cls, source: DocumentSource) -> BaseDocumentLoader:
        """Get the appropriate loader for the given source type."""
        loader_class = cls._loaders.get(source)
        if not loader_class:
            raise ValueError(f"No loader available for source type: {source}")
        return loader_class()

    @classmethod
    async def load(
        cls,
        content: bytes,
        metadata: DocumentMetadata,
    ) -> list[dict]:
        """Load document and return all chunks."""
        loader = cls.get_loader(metadata.source)
        chunks = []
        async for chunk in loader.load(content, metadata):
            chunks.append(chunk)
        return chunks


async def load_from_url(url: str, metadata: DocumentMetadata) -> list[dict]:
    """Load document from a URL."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return await DocumentLoaderFactory.load(
                content=response.content,
                metadata=metadata,
            )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        raise
