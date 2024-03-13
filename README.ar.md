# shamela2epub | أداة تحميل كتب الشاملة من الموقع بصيغة EPUB

> أداة سطر أوامر وواجهة رسومية لتحميل الكتب من [موقع المكتبة الشاملة](https://shamela.ws) بصيغة كتاب إلكتروني EPUB.

[![ara](https://img.shields.io/badge/README-Arabic-AB8B64.svg)](README.ar.md)
[![en](https://img.shields.io/badge/README-English-AB8B64.svg)](README.md)

![logo](shamela2epub/assets/books-duotone.svg)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/901b1123964c4468a88b0cfcde9147fe)](https://www.codacy.com/gh/yshalsager/shamela2epub/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=yshalsager/shamela2epub&amp;utm_campaign=Badge_Grade)
[![PyPI version](https://badge.fury.io/py/shamela2epub.svg)](https://pypi.org/project/shamela2epub/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/shamela2epub?period=total\&units=international_system\&left_color=grey\&right_color=blue\&left_text=Total%20Downloads%20\(PyPI\))](https://pepy.tech/project/shamela2epub)

[![GitHub release](https://img.shields.io/github/release/yshalsager/shamela2epub.svg)](https://github.com/yshalsager/shamela2epub/releases/)
[![GitHub Downloads](https://img.shields.io/github/downloads/yshalsager/shamela2epub/total.svg)](https://github.com/yshalsager/shamela2epub/releases/latest)

[![made-with-python](https://img.shields.io/badge/Made%20with-Python%203-3776AB?style=flat\&labelColor=3776AB\&logo=python\&logoColor=white\&link=https://www.python.org/)](https://www.python.org/)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=flat\&labelColor=00457C\&logo=PayPal\&logoColor=white\&link=https://www.paypal.me/yshalsager)](https://www.paypal.me/yshalsager)
[![LiberaPay](https://img.shields.io/badge/Liberapay-Support-F6C915?style=flat\&labelColor=F6C915\&logo=Liberapay\&logoColor=white\&link=https://liberapay.com/yshalsager)](https://liberapay.com/yshalsager)

**إخلاء مسؤولية:**

* هذا البرنامَج مجاني ومفتوح المصدر ومخصص فقط للاستخدام الشخصي أو التعليمي.

## التثبيت

### من PyPI

```bash
pip install shamela2epub
```

### من المستودع

```bash
# Using poetry
poetry install

# or using pip 18+
pip install .
```

## الاستخدام

### أداة سطر الأوامر

```bash
python3 -m shamela2epub download URL
# python3 -m shamela2epub download "https://shamela.ws/book/823"

python3 -m shamela2epub download --help
Usage: python -m shamela2epub download [OPTIONS] URL

  Download Shamela book form URL to ePub

Options:
  -o, --output TEXT  ePub output book custom name
  --help             Show this message and exit.
```

### الواجهة الرسومية

![gui](gui.png)

* إذا كنت قد ثبتت الحُزْمَة من PyPI فيمكنك استخدام الأمر التالي:

```bash
shamela2epubgui
```

* وإذا كنت قد حملت المِلَفّ التنفيذي الخاص بالإصدار الأخير من الواجهة الرسومية يمكنك فتحه وتشغيله بالطريقة العادية.
* بخلاف ما سبق، استخدم أمر بايثون التالي::

```bash
python3 -m shamela2epub gui
```

## الميزات

* أداة سطر أوامر وواجهة رسومية.
* إنشاء كتاب [EPUB3](https://www.w3.org/publishing/epub3/epub-spec.html) عربي قياسي.
* إضافة صفحة لمعلومات الكتاب.
* إنشاء فِهْرِس المحتويات مع دعم المستويات الفرعية.
* إضافة رقم الجزء ورقم الصفحة أسفل كل صفحة من الكتاب.
* تنقية HTML الكتاب من العناصر والمعلومات غير الضرورية.
* تحويل تنسيقات ألوان CSS الداخلية إلى فئات.
* تحويل الهوامش إلى نوافذ منبثقة inline footnote لسهولة التنقل منها وإليها.

## المشاكل المعروفة

* الكتب التي بها قسم فرعي أخير في مستوى ما في الفِهْرِس (مثلا 3) وهذا المستوى أعمق من المستوى التالي له (2 مثلا)،
  وكلاهما له نفس رَقَم الصفحة (مثلا `page_017.xhtml`)، لا يمكن تحويلها إلى KFX إلا عندما يحذف القسم الفرعي المذكور.

## قائمة المهام

### التالية

* أخبرني أنت :)

### المحتملة

* حل مشكلة الفِهْرِس خلال التحويل عندما يكون آخر قسم ذو مستوى أعمق من المستوى التالي له، ورقم صفحة كلا منهما نفس
  الرَّقَم، عبر حذف المستوى الأعمق من الفِهْرِس.

## شكر وتقدير

* شكرا لفريق [Phosphor Icons](https://phosphoricons.com/) على أيقونة الواجهة الرسومية (books - duotone - `#AB8B64`).
