"""
PDF 文档向量化导入工具

将 PDF 文档切分、向量化后存入 knowledge_docs 表，用于 RAG 检索

使用方法:
    cd backend
    python scripts/ingest_pdf.py <pdf_file_path>

    或批量导入整个目录:
    python scripts/ingest_pdf.py --dir data/raw/documents/
"""
import sys
import os
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

# PDF 加载
try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings
from app.db.models import KnowledgeDoc, Base


class PDFIngestor:
    """PDF 文档向量化处理器"""

    def __init__(self):
        """初始化处理器"""
        self.engine = create_engine(settings.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )

        # 文本切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 每个文本块大小
            chunk_overlap=200,  # 重叠字符数
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        从 PDF 文件中提取文本

        Args:
            pdf_path: PDF 文件路径

        Returns:
            提取的文本内容
        """
        print(f"📖 正在读取 PDF: {pdf_path}")

        try:
            reader = PdfReader(pdf_path)
            text = ""

            # 逐页提取文本
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

                # 显示进度
                if (i + 1) % 10 == 0:
                    print(f"   已处理 {i + 1}/{len(reader.pages)} 页")

            print(f"✅ PDF 读取完成，共 {len(reader.pages)} 页")
            print(f"   提取文本长度: {len(text)} 字符")

            return text

        except Exception as e:
            print(f"❌ 错误: PDF 读取失败 - {str(e)}")
            return ""

    def split_text(self, text: str) -> List[str]:
        """
        切分文本为多个块

        Args:
            text: 原始文本

        Returns:
            文本块列表
        """
        print(f"✂️  正在切分文本...")

        chunks = self.text_splitter.split_text(text)
        print(f"✅ 切分完成，共 {len(chunks)} 个文本块")

        return chunks

    def create_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """
        为文本块创建向量嵌入

        Args:
            chunks: 文本块列表

        Returns:
            向量列表
        """
        print(f"🧠 正在生成向量嵌入...")

        try:
            # 使用 OpenAI Embedding API
            vectors = self.embeddings.embed_documents(chunks)

            print(f"✅ 向量生成完成")
            print(f"   向量维度: {len(vectors[0]) if vectors else 0}")

            return vectors

        except Exception as e:
            print(f"❌ 错误: 向量生成失败 - {str(e)}")
            return []

    def save_to_database(
        self,
        title: str,
        chunks: List[str],
        vectors: List[List[float]],
        file_path: str,
        file_type: str = "pdf",
        uploaded_by: int = 1
    ) -> int:
        """
        将切分的文本块和向量保存到数据库

        Args:
            title: 文档标题
            chunks: 文本块列表
            vectors: 向量列表
            file_path: 文件路径
            file_type: 文件类型
            uploaded_by: 上传者 ID

        Returns:
            成功保存的文档数量
        """
        print(f"💾 正在保存到数据库...")

        session = self.Session()
        saved_count = 0

        try:
            for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                # pgvector 原生格式：直接传入 Python list
                doc = KnowledgeDoc(
                    title=f"{title} - Part {i + 1}",
                    content=chunk,
                    file_path=file_path,
                    file_type=file_type,
                    embedding=vector,
                    meta_data={
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "source_file": title
                    },
                    uploaded_by=uploaded_by
                )

                session.add(doc)
                saved_count += 1

                # 显示进度
                if (i + 1) % 10 == 0:
                    print(f"   已保存 {i + 1}/{len(chunks)} 个文档块")

            session.commit()
            print(f"✅ 保存完成，共 {saved_count} 个文档块")

        except Exception as e:
            session.rollback()
            print(f"❌ 错误: 数据库保存失败 - {str(e)}")
        finally:
            session.close()

        return saved_count

    def process_pdf(
        self,
        pdf_path: str,
        title: Optional[str] = None,
        uploaded_by: int = 1
    ) -> bool:
        """
        处理单个 PDF 文件

        Args:
            pdf_path: PDF 文件路径
            title: 文档标题（可选，默认使用文件名）
            uploaded_by: 上传者 ID

        Returns:
            是否成功处理
        """
        try:
            # 提取文件名作为标题
            if title is None:
                title = Path(pdf_path).stem

            # 1. 提取文本
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                return False

            # 2. 切分文本
            chunks = self.split_text(text)
            if not chunks:
                return False

            # 3. 生成向量
            vectors = self.create_embeddings(chunks)
            if not vectors:
                return False

            # 4. 保存到数据库
            saved_count = self.save_to_database(
                title=title,
                chunks=chunks,
                vectors=vectors,
                file_path=pdf_path,
                file_type="pdf",
                uploaded_by=uploaded_by
            )

            return saved_count > 0

        except Exception as e:
            print(f"❌ 错误: PDF 处理失败 - {str(e)}")
            return False

    def process_directory(self, dir_path: str, uploaded_by: int = 1):
        """
        批量处理目录中的所有 PDF 文件

        Args:
            dir_path: PDF 文件目录
            uploaded_by: 上传者 ID
        """
        dir_path = Path(dir_path)

        if not dir_path.exists():
            print(f"❌ 错误: 目录不存在 - {dir_path}")
            return

        # 查找所有 PDF 文件
        pdf_files = list(dir_path.glob("*.pdf"))

        if not pdf_files:
            print(f"⚠️  未找到 PDF 文件: {dir_path}")
            return

        print(f"📁 找到 {len(pdf_files)} 个 PDF 文件\n")

        success_count = 0
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] 处理: {pdf_file.name}")
            print("-" * 60)

            if self.process_pdf(str(pdf_file), uploaded_by=uploaded_by):
                success_count += 1
                print(f"✅ {pdf_file.name} 处理成功")
            else:
                print(f"❌ {pdf_file.name} 处理失败")

        print("\n" + "=" * 60)
        print(f"✅ 批量处理完成: {success_count}/{len(pdf_files)} 成功")
        print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("📚 PDF 文档向量化导入工具")
    print("=" * 60)

    ingestor = PDFIngestor()

    # 解析命令行参数
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  单个文件: python ingest_pdf.py <pdf_file_path>")
        print("  批量导入: python ingest_pdf.py --dir <directory>")
        return

    if sys.argv[1] == "--dir":
        # 批量导入目录
        if len(sys.argv) < 3:
            print("❌ 错误: 请指定目录路径")
            return

        dir_path = sys.argv[2]
        ingestor.process_directory(dir_path)
    else:
        # 单个文件导入
        pdf_path = sys.argv[1]

        if not Path(pdf_path).exists():
            print(f"❌ 错误: 文件不存在 - {pdf_path}")
            return

        ingestor.process_pdf(pdf_path)


if __name__ == "__main__":
    main()
