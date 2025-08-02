from pathlib import Path
from typing import List

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter


def markdown_file_load_and_document_spilt(
        markdown_path: str) -> list[Document]:
    """
    加载文档，并进行文档分割
    :param markdown_path: 文件路径
    :return:
    """
    # 1. 加载 Markdown 文档
    documents = __load_document_from_markdown_path(markdown_path)
    # 2. 分割配置（修正：补充参数说明）
    all_splits = __splitter_markdown(documents)

    return __documents_splitter(all_splits)


def __load_document_from_markdown_path(markdown_path: str) -> List[Document]:
    """加载 Markdown 文档"""
    file = Path(markdown_path)
    if not file.exists():
        raise FileNotFoundError(f"文档不存在: {markdown_path}")

    loader = UnstructuredMarkdownLoader(str(markdown_path))
    documents = loader.load()
    return documents


def __splitter_markdown(documents):
    headers_to_split_on = [
        ("#", "Header 1"),  # 一级标题 → 存入 metadata["Header 1"]
        ("##", "Header 2"),
        ("###", "Header 3")
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=True  # False=保留标题文本在内容中，True=仅存到metadata
    )
    # 3. 分割处理（修正：优化元数据合并逻辑）
    all_splits: List[Document] = []
    for doc in documents:
        # 提取原始文本并分割
        header_splits: List[Document] = markdown_splitter.split_text(doc.page_content)

        # 仅合并必要的源元数据（如文件路径）
        for split in header_splits:
            split.metadata.update({
                "source": doc.metadata.get("source", "unknown"),  # 保留原始来源
                "original_format": "markdown"  # 添加自定义标记
            })
        all_splits.extend(header_splits)
    return all_splits


def __documents_splitter(documents: List[Document])->list[Document]:
    # 4. 二次分割（保持不变）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "。", "！", "？"]
    )
    final_splits = text_splitter.split_documents(documents)
    return final_splits
