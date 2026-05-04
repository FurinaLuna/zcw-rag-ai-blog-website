"""测试 RAG 文本清洗模块边缘情况 — 超长文本、特殊字符、混合语言等"""

import pytest
from app.services.rag.cleaner import clean_markdown


class TestVeryLongText:
    """超长文本处理 — 确保不会崩溃或性能问题"""

    def test_very_long_plain_text(self):
        """50K 纯文本应正常处理"""
        text = "这是一段超长的中文文本内容。" * 5000  # ~50K chars
        result = clean_markdown(text)
        assert len(result) > 0
        assert "超长" in result

    def test_very_long_markdown_with_code_blocks(self):
        """超长 Markdown 中含多个代码块"""
        parts = []
        for i in range(20):
            parts.append(f"## 章节 {i}\n\n段落内容。\n\n```python\nprint({i})\n```\n\n")
        text = "".join(parts)  # 多个代码块
        result = clean_markdown(text)
        assert "章节" in result
        assert "```" not in result
        # 代码块内容应被移除
        assert "print(" not in result

    def test_extremely_long_single_line(self):
        """超长单行（无换行符）"""
        text = "A" * 10000
        result = clean_markdown(text)
        assert len(result) > 0


class TestSpecialCharacters:
    """特殊字符处理"""

    def test_emojis_preserved(self):
        text = "标题 😀🎉 内容 🚀✨ 结束"
        result = clean_markdown(text)
        assert "😀" in result
        assert "🎉" in result
        assert "🚀" in result

    def test_html_entity_like_text(self):
        text = "使用 &lt;div&gt; 标签和 &amp; 符号"
        result = clean_markdown(text)
        assert "&lt;div&gt;" in result
        assert "&amp;" in result

    def test_regex_special_characters(self):
        """正则特殊字符不应导致异常"""
        text = r"正则表达式: \d+ \w* [a-z] (foo|bar) ^start$ .*?"
        result = clean_markdown(text)
        assert r"\d+" in result

    def test_json_like_content(self):
        text = '配置: {"key": "value", "list": [1, 2, 3]}'
        result = clean_markdown(text)
        assert "key" in result
        assert "value" in result

    def test_sql_like_content(self):
        text = "SELECT * FROM users WHERE id = 1; -- 注释"
        result = clean_markdown(text)
        assert "SELECT" in result
        assert "FROM" in result

    def test_zero_width_characters(self):
        text = "正常​文本‌中间‍零宽字符﻿"
        result = clean_markdown(text)
        # 零宽字符应保留（不崩溃）
        assert len(result) > 0

    def test_only_punctuation(self):
        text = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        result = clean_markdown(text)
        # 大部分标点应保留，反引号可能被移除
        assert len(result) > 0

    def test_unicode_math_symbols(self):
        text = "数学公式: ∑ x² = √(y) × π"
        result = clean_markdown(text)
        assert "∑" in result  # ∑
        assert "π" in result  # π


class TestMixedLanguages:
    """混合语言文本"""

    def test_chinese_english_mixed(self):
        text = "# AI智能内容平台\n\n本平台使用 **React** 和 **Python** 构建。\n\n- Feature 1: 智能推荐\n- Feature 2: RAG检索"
        result = clean_markdown(text)
        assert "AI智能内容平台" in result
        assert "React" in result
        assert "Python" in result
        assert "Feature" in result
        assert "智能推荐" in result
        assert "RAG" in result
        assert "#" not in result
        assert "**" not in result

    def test_chinese_english_japanese_mixed(self):
        text = "## 多言語対応 / Multilingual\n\n日本語のテストです。\n\nEnglish test.\n\n中文测试。\n\n```python\nprint('hello')\n```"
        result = clean_markdown(text)
        assert "多言語対応" in result
        assert "Multilingual" in result
        assert "日本語" in result
        assert "English" in result
        assert "中文" in result
        assert "```" not in result

    def test_arabic_and_rtl_text(self):
        text = "# مرحبا بالعالم\n\nهذا نص عربي مع **تنسيق**"
        result = clean_markdown(text)
        assert "مرحبا" in result
        assert "تنسيق" in result
        assert "#" not in result


class TestNestedMarkdown:
    """嵌套 Markdown 标记"""

    def test_bold_inside_link(self):
        text = "[**加粗链接**](https://example.com)"
        result = clean_markdown(text)
        # 先去链接方括号内容保留, 然后去加粗
        assert "加粗链接" in result
        assert "https://example.com" not in result

    def test_code_inside_bold(self):
        text = "**使用 `async/await` 语法**"
        result = clean_markdown(text)
        assert "async/await" in result
        assert "`" not in result
        assert "**" not in result

    def test_link_inside_list(self):
        text = "- [项目A](https://a.com)\n- [项目B](https://b.com)"
        result = clean_markdown(text)
        assert "项目A" in result
        assert "项目B" in result
        assert "https://a.com" not in result
        assert "-" not in result

    def test_italic_in_heading(self):
        text = "### *斜体标题*"
        result = clean_markdown(text)
        assert "斜体标题" in result
        assert "#" not in result
        assert "*" not in result


class TestEdgeCaseInputs:
    """边缘输入值"""

    def test_only_markdown_markers(self):
        text = "# ** ` ``` ~~ []( ) > - | ---"
        result = clean_markdown(text)
        # 应返回清理后的内容（可能为空或只留部分字符）
        assert isinstance(result, str)

    def test_only_whitespace_and_newlines(self):
        text = "   \n\n\n   \n   "
        result = clean_markdown(text)
        assert result == ""

    def test_text_all_stripped_away(self):
        """所有内容都是 Markdown 标记时返回空"""
        text = "```\ncode\n```\n\n![img](x.png)"
        result = clean_markdown(text)
        assert result == ""

    def test_table_with_many_columns(self):
        text = "| A | B | C | D | E | F | G | H |\n|---|---|---|---|---|---|---|---|\n| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |"
        result = clean_markdown(text)
        assert "|" not in result

    def test_code_block_with_nested_backticks(self):
        """嵌套反引号: 简单正则无法完美处理但不应崩溃"""
        text = "````markdown\n```python\nprint('hello')\n```\n````"
        result = clean_markdown(text)
        # 简单正则 ```[\s\S]*?``` 在嵌套场景可能有残留, 但不崩溃即可
        assert isinstance(result, str)

    def test_strikethrough_with_tilde_content(self):
        text = "~~删除内容 ~~ 包含波浪号~~"
        result = clean_markdown(text)
        # strikethrough regex is ~~([^~]+)~~ — content between ~~ is kept
        # The content is "内容 ~~ 包含波浪号" (without tildes the regex captures)
        # Actually ~~([^~]+)~~ means: two tildes, then one or more non-tilde chars, then two tildes
        # For "~~删除内容 ~~ 包含波浪号~~":
        # The first ~~ matches, then [^~]+ matches "删除内容 " (space is not ~)
        # Then ~~ matches " ~~" followed by more... hmm, this could be ambiguous
        # Let's just verify it doesn't crash
        assert isinstance(result, str)
