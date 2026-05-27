# AsyncRecon Framework

إطار عمل متقدم للفحص الشبكي غير المتزامن (Asynchronous Port Scanner) لاستطلاع الشبكات واكتشاف الخدمات المفتوحة.

## الميزات التقنية
* محرك غير متزامن يعتمد على uvloop.
* إدارة الموارد التلقائية (رفع حدود File Descriptors).
* واجهة مستخدم تفاعلية (TUI) عبر مكتبة rich.
* استخراج فوري للترويسات (Banner Grabbing).

## المتطلبات
* Python 3.8+
* نظام تشغيل Linux أو macOS

## التثبيت
نفذ الأوامر التالية بالترتيب:

1. استنساخ المستودع:
   git clone https://github.com/yourusername/AsyncRecon.git
   cd AsyncRecon

2. إنشاء بيئة افتراضية:
   python3 -m venv recon_env

3. تفعيل البيئة:
   source recon_env/bin/activate

4. تثبيت المكتبات:
   pip install -r requirements.txt

5. منح الصلاحيات للسكربت:
   chmod +x async_recon.py

## الاستخدام
يجب تشغيل الأداة أثناء تفعيل البيئة الافتراضية.

الصيغة العامة:
python async_recon.py -t <TARGET_IP> [الخيارات]

الخيارات المتاحة:
-t, --target      عنوان IP المستهدف (إجباري)
-c, --concurrency الحد الأقصى للاتصالات المتزامنة (الافتراضي: 1000)
-to, --timeout    مهلة الاتصال بالثواني (الافتراضي: 1.5)
-s, --start       رقم منفذ البداية (الافتراضي: 1)
-e, --end         رقم منفذ النهاية (الافتراضي: 65535)

أمثلة التشغيل:

فحص النطاق الافتراضي:
python async_recon.py -t 192.168.1.1

فحص مكثف لجميع المنافذ (1-65535) بـ 5000 اتصال متزامن:
python async_recon.py -t 10.0.0.5 -c 5000 -s 1 -e 65535

فحص سريع لشبكة محلية بمهلة اتصال قصيرة:
python async_recon.py -t 127.0.0.1 -to 0.5 -c 2000 -s 1 -e 1024
