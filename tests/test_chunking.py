from src.living_authenticity.knowledge.chunking.paragraph_chunker import (
    ParagraphChunker,
)


PERSIAN_NOTE = """
مشاهده مطرح‌شده:
افرادی که در محیط‌های مملو از دغدغه، فشار یا مشکلات مزمن رشد کرده‌اند ممکن است توانایی تجربه آرامش در امور ساده زندگی را از دست بدهند.

نمونه‌های مطرح‌شده:
- تجربه آرامش با احساس اتلاف وقت اشتباه گرفته می‌شود.
- فرد حتی در نبود فشار یا وظیفه بیرونی برای خود تنش ایجاد می‌کند.
- نبود دغدغه ممکن است به جای آرامش، احساس بی‌قراری ایجاد کند.

ارتباطات:
[[سیستم بقا]]
[[سیستم آرامش]]

#peace
#survival

Origin:
مشاهده مبتنی بر تجربه شخصی و فرهنگی 2025/05/12

وضعیت:
مستقل

تعارض با مدل فعلی:
ندارد

سؤال‌های باز:
چگونه می‌توان توانایی تجربه آرامش در امور ساده را بازآموخت و بر بینش شخص تاثیر گذاشت؟
"""


def test_paragraph_chunker_splits_on_blank_lines():
    chunker = ParagraphChunker()
    chunks = chunker.split(PERSIAN_NOTE)

    assert len(chunks) >= 2
    assert any("مشاهده مطرح‌شده" in chunk for chunk in chunks)
    assert any("[[سیستم بقا]]" in chunk for chunk in chunks)
