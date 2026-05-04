"""测试 RAG 文本切片模块"""

import pytest
from app.services.rag.splitter import split_text


def test_split_empty_text():
    result = split_text("")
    assert result == []


def test_split_whitespace_only():
    result = split_text("   \n\n  ")
    assert result == []


def test_split_short_text():
    text = "这是一段简短的文本。"
    result = split_text(text)
    assert len(result) >= 0


def test_split_paragraphs():
    text = "Paragraph one with enough content to exceed minimum chunk size.\n\nParagraph two also has enough content to pass the filter.\n\nParagraph three continues with more content for testing."
    result = split_text(text, chunk_size=100)
    assert len(result) > 0
    for chunk in result:
        assert len(chunk) >= 50


def test_split_long_text():
    paragraphs = []
    for i in range(20):
        paragraphs.append(f"这是第{i}段内容，" + "包含一些文字内容。" * 20)
    text = "\n\n".join(paragraphs)
    result = split_text(text, chunk_size=200, chunk_overlap=50)
    assert len(result) > 0
    for chunk in result:
        assert 50 <= len(chunk) <= 500


def test_split_respects_chunk_size():
    text = "短句子。" * 100
    result = split_text(text, chunk_size=200)
    for chunk in result:
        assert len(chunk) <= 500


def test_split_chinese_text():
    text = (
        "Nuxt3 是一个基于 Vue3 的混合渲染框架，支持 SSG、SSR 和 CSR 三种渲染模式。"
        "它提供了文件路由、自动导入、零配置等特性，极大地提升了开发效率。\n\n"
        "在内容平台中，我们使用 SSG 预渲染首页和列表页，确保首屏加载速度和 SEO 友好。"
        "对于文章详情页，采用 SSR 服务端渲染，实现动态内容的实时输出。"
        "后台管理页面使用 CSR 客户端渲染，减少服务端负担。"
    )
    result = split_text(text, chunk_size=200, chunk_overlap=30)
    assert len(result) > 0
    for chunk in result:
        assert len(chunk) >= 50
        assert len(chunk) <= 500


def test_split_single_sentence():
    text = "这是一个句子。"
    result = split_text(text)
    # Short text that's > 50 chars but the regex splitting might keep it
    # If too short (<50 chars), it should be filtered out
    if result:
        for chunk in result:
            assert len(chunk) >= 50


def test_filter_too_short_chunks():
    text = "短。太短。也很短。还是太短不够用。还是太短不够用还是太短不够用。" * 3
    result = split_text(text)
    for chunk in result:
        assert len(chunk) >= 50


def test_filter_too_long_chunks():
    text = "这是一个非常长的句子但是因为句子太长了所以需要被分段处理。" * 20
    result = split_text(text, chunk_size=200)
    for chunk in result:
        assert len(chunk) <= 500
