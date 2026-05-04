import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def sample_markdown() -> str:
    return """# 测试标题

这是一段**加粗**文本，包含`行内代码`。

## 二级标题

- 列表项1
- 列表项2

```python
print("hello world")
```

[链接文本](https://example.com)

![图片](image.png)

> 引用文本

| 表头1 | 表头2 |
|------|------|
| 值1   | 值2   |

普通段落文本。
"""


@pytest.fixture
def sample_cleaned_text() -> str:
    return "测试标题\n\n这是一段加粗文本，包含行内代码。\n\n二级标题\n\n列表项1\n列表项2\n\n链接文本\n\n引用文本\n\n普通段落文本。"
