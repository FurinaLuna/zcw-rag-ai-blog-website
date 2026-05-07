"""测试 RAG 文本清洗模块"""

from app.services.rag.cleaner import clean_markdown


def test_clean_headers():
    text = "# 一级标题\n## 二级标题\n### 三级标题\n正文内容"
    result = clean_markdown(text)
    assert "一级标题" in result
    assert "二级标题" in result
    assert "三级标题" in result
    assert "#" not in result


def test_clean_bold():
    text = "这是**加粗文本**和__下划线加粗__内容"
    result = clean_markdown(text)
    assert "加粗文本" in result
    assert "下划线加粗" in result
    assert "**" not in result


def test_clean_inline_code():
    text = "使用`print()`输出内容"
    result = clean_markdown(text)
    assert "print()" in result
    assert "`" not in result


def test_clean_code_blocks():
    text = "```python\nprint('hello')\n```\n\n正文"
    result = clean_markdown(text)
    assert "正文" in result
    assert "print" not in result
    assert "```" not in result


def test_clean_links():
    text = "[链接文本](https://example.com)"
    result = clean_markdown(text)
    assert "链接文本" in result
    assert "https://example.com" not in result
    assert "[" not in result


def test_clean_images():
    text = "![图片描述](image.png)"
    result = clean_markdown(text)
    assert "图片描述" not in result
    assert "[" not in result


def test_clean_blockquotes():
    text = "> 这是一段引用\n\n正文"
    result = clean_markdown(text)
    assert "正文" in result
    assert ">" not in result


def test_clean_unordered_lists():
    text = "- 列表项1\n- 列表项2\n\n正文"
    result = clean_markdown(text)
    assert "列表项1" in result
    assert "列表项2" in result
    assert "-" not in result


def test_clean_ordered_lists():
    text = "1. 第一项\n2. 第二项\n\n正文"
    result = clean_markdown(text)
    assert "第一项" in result
    assert "第二项" in result


def test_clean_tables():
    text = "| 列1 | 列2 |\n|-----|-----|\n| 值1 | 值2 |\n\n正文"
    result = clean_markdown(text)
    assert "正文" in result
    assert "|" not in result


def test_clean_strikethrough():
    text = "这是~~删除线~~文本"
    result = clean_markdown(text)
    assert "删除线" in result
    assert "~~" not in result


def test_clean_horizontal_rules():
    text = "段落1\n\n---\n\n段落2"
    result = clean_markdown(text)
    assert "段落1" in result
    assert "段落2" in result


def test_clean_multiple_newlines():
    text = "段落1\n\n\n\n段落2"
    result = clean_markdown(text)
    assert result.count("\n\n") <= 2


def test_clean_multiple_spaces():
    text = "文字  中间有  多个空格"
    result = clean_markdown(text)
    assert "   " not in result


def test_clean_empty_text():
    result = clean_markdown("")
    assert result == ""


def test_clean_text_without_markdown():
    text = "纯文本内容，没有任何Markdown标记。"
    result = clean_markdown(text)
    assert "纯文本内容" in result


def test_clean_complex_document(sample_markdown):
    result = clean_markdown(sample_markdown)
    # 验证基本内容保留
    assert "测试标题" in result
    assert "加粗" in result
    assert "行内代码" in result
    assert "二级标题" in result
    assert "列表项" in result
    assert "链接文本" in result
    assert "普通段落" in result
    # 验证Markdown标记已清除
    assert "#" not in result
    assert "```" not in result
    assert "|" not in result
    assert ">" not in result
    assert "[" not in result


def test_clean_chinese_text():
    text = "# 智能内容平台\n\n这是一个基于 **Nuxt3** 的内容平台。\n\n- 支持 SSG\n- 支持 SSR"
    result = clean_markdown(text)
    assert "智能内容平台" in result
    assert "Nuxt3" in result
    assert "SSG" in result
    assert "SSR" in result
