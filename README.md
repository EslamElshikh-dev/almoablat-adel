# المبلط عادل — موقع خدمات البلاط في الرياض

نسخة متعددة الصفحات مبنية كملفات HTML/CSS/JavaScript ثابتة، سريعة وقابلة للنشر على GitHub Pages أو Vercel.

## البنية

- الصفحة الرئيسية
- صفحة تجمع الخدمات
- 9 صفحات خدمة مستقلة
- صفحة المدونة
- 10 مقالات شاملة مرتبطة بالخدمات
- Sitemap وRobots وManifest وملف إعداد Vercel
- بيانات منظمة: HomeAndConstructionBusiness وService وBreadcrumbList وBlogPosting وFAQPage وItemList

## الصور

صفحات الموقع تستخدم صور الخدمات الموجودة أصلًا في المستودع داخل `assets/images/` بالأسماء التالية:

- `tile.jpg`
- `ceramic.jpg`
- `porcelain.jpg`
- `marble.jpg`
- `granite.jpg`
- `stone.jpg`
- `polishing.jpg`
- `waterproofing.jpg`
- `repair.jpg`

تتضمن الحزمة شعار SVG وأيقونة موقع جديدين، لكنها لا تكرر ملفات الصور الفوتوغرافية الموجودة في المستودع.

## اختبار محلي

```bash
python3 tools/validate_site.py
python3 -m http.server 8000
```

ثم افتح `http://localhost:8000/`.

## النطاق الأساسي

تم اعتماد رابط الإنتاج على Vercel في Canonical وSitemap وبيانات المشاركة:
`https://almoablat-adel.vercel.app/`.

عند ربط نطاق مخصص مستقبلًا، يجب استبدال هذا الرابط في جميع الصفحات وملفات
`sitemap.xml` و`robots.txt` قبل طلب الفهرسة.

## ملاحظات SEO

الصفحات لا تستخدم تقييمات أو مراجعات مختلقة، ولا تعتمد على حشو أسماء الأحياء. تحقيق الظهور يحتاج بعد النشر إلى ربط Search Console، إرسال Sitemap، تحسين ملف Google التجاري، جمع مراجعات حقيقية، متابعة سرعة الموقع، وبناء إشارات محلية موثوقة.
