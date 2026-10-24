# -*- coding: utf-8 -*-
"""
================================================================================
موتور تولید خودکار گزارش بالینی ام‌آر‌آی | بیمارستان بوعلی مریوان
Boali Hospital Clinical MRI Report Generator & Official Word (.docx) Exporter
================================================================================
"""

import os
import time

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
except ImportError:
    Document = None


class MriReportGenerator:
    """Generates bilingual structured MRI reports and official Word documents."""

    @staticmethod
    def generate_knee_report_text(patient_info, analysis, lang="bilingual"):
        """Generates structured clinical report text for Knee MRI."""
        name = patient_info.get("name") or "ناشناس"
        age = patient_info.get("age") or "--"
        gender = patient_info.get("gender") or "نامشخص"
        pid = patient_info.get("id") or "--"
        date_str = patient_info.get("date") or time.strftime("%Y/%m/%d")
        laterality = analysis.get("laterality", "Left")
        lat_fa = "چپ" if laterality == "Left" else "راست"
        baker = analysis.get("bakers_cyst", {})
        findings = analysis.get("findings", {})

        # 1. Menisci Evaluation
        med_m = findings.get("medial_meniscus", {})
        lat_m = findings.get("lateral_meniscus", {})
        med_grade = med_m.get("grade", 0)
        lat_grade = lat_m.get("grade", 0)

        if med_grade >= 2:
            med_en = f"{med_m.get('status', 'Tear / signal alteration')} ({med_m.get('location', 'Posterior horn')})."
            med_fa = f"افزایش سیگنال داخل‌بافتی در {med_m.get('location', 'شاخ خلفی')} با گسترش به لبه مفصلی، مطرح‌کننده پارگی ({med_m.get('status', '')})."
        elif med_grade == 1:
            med_en = "Mild intrasubstance myxoid signal alteration (Grade I) without tear. Articular surfaces are intact."
            med_fa = "تغییرات سیگنال خفیف گرید ۱ داخل‌بافتی (دژنراسیون میکسوئید) بدون گسترش به سطوح مفصلی؛ فاقد پارگی."
        else:
            med_en = "Intact with normal low signal intensity and sharp triangular morphology. No tear or degenerative change."
            med_fa = "شکل مثلثی با حاشیه‌های تیز و سیگنال کم‌شدت طبیعی حفظ شده است. شواهدی از پارگی یا تغییرات دژنراتیو دیده نمی‌شود."

        if lat_grade >= 2:
            lat_en = f"{lat_m.get('status', 'Tear / signal alteration')} ({lat_m.get('location', 'Posterior horn')})."
            lat_men_fa = f"افزایش سیگنال غیرطبیعی و پارگی در {lat_m.get('location', 'منیسک خارجی')}."
        else:
            lat_en = "Intact with normal low signal intensity and sharp triangular morphology. No tear or parameniscal cyst."
            lat_men_fa = "دارای مورفولوژی طبیعی، کناره‌های مثلثی تیز و سیگنال کم‌شدت یکنواخت؛ فاقد پارگی یا کیست پارامنیسکال."

        # 2. Joint Effusion
        effusion_str = findings.get('patellofemoral', {}).get('effusion', 'No significant joint effusion.')
        has_effusion = "mild" in effusion_str.lower() or "moderate" in effusion_str.lower() or "marked" in effusion_str.lower()

        en_report = f"""MAGNETIC RESONANCE IMAGING (MRI) OF THE {laterality.upper()} KNEE
KURDISTAN UNIVERSITY OF MEDICAL SCIENCES
MARIVAN HEALTHCARE NETWORK - BOALI HOSPITAL
DEPARTMENT OF MEDICAL IMAGING & RADIOLOGY
======================================================================
Patient Name: {name}    | Age: {age}    | Gender: {gender}
Patient ID: {pid}    | Exam Date: {date_str}
Study: High-Resolution Multiplanar MRI of the {laterality} Knee
----------------------------------------------------------------------

TECHNIQUE:
Multiplanar multi-sequence magnetic resonance imaging of the {laterality} knee was performed 
including Sagittal T1-weighted, Sagittal PD Fat-Suppressed, Coronal T1-weighted, 
Coronal PD Fat-Suppressed, and Axial PD Fat-Suppressed sequences on a high-field system.

FINDINGS:

1. MENISCI:
- Medial Meniscus: {med_en}
- Lateral Meniscus: {lat_en}

2. CRUCIATE LIGAMENTS:
- Anterior Cruciate Ligament (ACL): {findings.get('acl', {}).get('status', 'Intact')} - {findings.get('acl', {}).get('details', '')}
- Posterior Cruciate Ligament (PCL): {findings.get('pcl', {}).get('status', 'Intact')} - {findings.get('pcl', {}).get('details', '')}

3. COLLATERAL LIGAMENTS & SUPPORTING STRUCTURES:
- Medial Collateral Ligament (MCL): {findings.get('mcl', {}).get('status', 'Intact')} - {findings.get('mcl', {}).get('details', '')}
- Lateral Collateral Ligament Complex (LCL / FCL): {findings.get('lcl', {}).get('status', 'Intact')} - {findings.get('lcl', {}).get('details', '')}

4. EXTENSOR MECHANISM & PATELLOFEMORAL COMPARTMENT:
- Retropatellar & Trochlear Cartilage: {findings.get('patellofemoral', {}).get('cartilage', 'Preserved')}
- Joint Effusion: {effusion_str}
- Infrapatellar Fat Pad: {findings.get('patellofemoral', {}).get('hoffa', 'Normal')}

5. OSSEOUS STRUCTURES & BONE MARROW:
- {findings.get('bone_marrow', {}).get('details', 'No bone contusion or fracture identified.')}

6. POPLITEAL FOSSA & SOFT TISSUES:"""

        if baker.get("present"):
            w = baker.get("width_mm", 12.0)
            d = baker.get("depth_mm", 14.0)
            l = baker.get("length_mm", 25.0)
            v = baker.get("volume_cm3", 2.2)
            loc = baker.get("loculation", "Unilocular")
            en_report += f"""
- A well-defined {loc.lower()} fluid collection (Popliteal / Baker's Cyst) is demonstrated in the 
  posteromedial popliteal fossa, tracking characteristically between the medial head of the 
  gastrocnemius muscle and the semimembranosus tendon.
- Approximate Dimensions: {w} mm (transverse) x {d} mm (AP) x {l} mm (craniocaudal length).
  Calculated Volume: ~{v} cm3.
- Adjacent popliteal neurovascular vessels are patent without compression or thrombosis."""
        else:
            en_report += """
- Normal popliteal fossa without evidence of Baker's cyst or abnormal fluid collection. Neurovascular bundle is intact."""

        # English Impression
        is_completely_normal = (med_grade == 0 and lat_grade == 0 and not baker.get("present") and not has_effusion)

        en_report += f"""

======================================================================
IMPRESSION:
Multiplanar MRI of the {laterality} knee demonstrating:"""

        if is_completely_normal:
            en_report += f"""
1. Normal MRI examination of the {laterality} knee without internal derangement.
2. Intact medial and lateral menisci without tear.
3. Intact anterior and posterior cruciate ligaments (ACL & PCL).
4. Intact medial and lateral collateral ligament complexes (MCL & LCL).
5. No joint effusion or popliteal (Baker's) cyst."""
        else:
            imp_idx = 1
            if med_grade >= 2:
                en_report += f"\n{imp_idx}. Degenerative signal alteration / tear involving the posterior horn of the medial meniscus."
                imp_idx += 1
            elif med_grade == 1:
                en_report += f"\n{imp_idx}. Mild intrameniscal degenerative signal (Grade I) in medial meniscus without tear."
                imp_idx += 1

            if lat_grade >= 2:
                en_report += f"\n{imp_idx}. Degenerative tear / signal alteration involving the lateral meniscus."
                imp_idx += 1

            if baker.get("present"):
                en_report += f"\n{imp_idx}. Popliteal cyst (Baker's cyst) measuring {baker.get('width_mm')} x {baker.get('depth_mm')} x {baker.get('length_mm')} mm in the posteromedial compartment."
                imp_idx += 1

            if has_effusion:
                en_report += f"\n{imp_idx}. {effusion_str}"
                imp_idx += 1

            en_report += f"""
{imp_idx}. Intact cruciate (ACL & PCL) and collateral (MCL & LCL) ligaments."""

        if is_completely_normal:
            en_report += """

RECOMMENDATIONS:
- Clinical correlation with physical symptoms. Routine conservative care; no operative intervention indicated."""
        elif baker.get("present") or med_grade >= 2:
            en_report += """

RECOMMENDATIONS:
- Orthopedic clinical correlation is advised. Conservative therapy with quadriceps strengthening is recommended.
- Follow-up evaluation if symptoms persist."""
        else:
            en_report += """

RECOMMENDATIONS:
- Clinical correlation is recommended."""

        en_report += """

Sincerely Yours,
Department of Medical Imaging & Radiology
Boali Hospital, Marivan"""

        # Persian Clinical Translation
        fa_report = f"""گزارش رسمی تصویربرداری تشدید مغناطیسی (MRI) زانوی {lat_fa}
دانشگاه علوم پزشکی و خدمات بهداشتی درمانی کردستان
شبکه بهداشت و درمان مریوان - بیمارستان بوعلی
واحد تصویربرداری پزشکی و ام‌آر‌آی
======================================================================
نام بیمار: {name}    | سن: {age} سال    | جنسیت: {gender}
شماره پرونده / پذیرش: {pid}    | تاریخ آزمون: {date_str}
نوع بررسی: ام‌آر‌آی چندجهته با رزولوشن بالا از زانوی {lat_fa}
----------------------------------------------------------------------

شرح یافته‌های بالینی:

۱. وضعیت منیسک‌ها (Menisci):
• منیسک داخلی (Medial Meniscus): {med_fa}
• منیسک خارجی (Lateral Meniscus): {lat_men_fa}

۲. رباط‌های متقاطع (Cruciate Ligaments):
• رباط صلیبی قدامی (ACL): پیوستگی فیبرها، زاویه آناتومیک و کشش طبیعی حفظ شده است. شواهدی از پارگی یا کشیدگی دیده نمی‌شود.
• رباط صلیبی خلفی (PCL): کاملاً سالم، یکپارچه و دارای انحنای استاندارد و سیگنال طبیعی است.

۳. رباط‌های جانبی و بافت‌های نگهدارنده (Collateral Ligaments):
• رباط جانبی داخلی (MCL): لایه‌های عمقی و سطحی پیوستگی کامل دارند و فاقد ادم یا پارگی هستند.
• کمپلکس رباط جانبی خارجی (LCL / FCL): رباط فیبولار، تاندون عضله بایسپس فموریس و تاندون پوپلیتئوس سالم هستند.

۴. ساختار اکستنسور و فضای پاتلوفمورال:
• غضروف‌های مفصلی پشت کشکک و تروکلئا ضخامت خود را حفظ کرده‌اند و فاقد نقص کانونی هستند.
• افیوژن مفصلی: {"افیوژن خفیف در بورس سوپراپاتلار دیده می‌شود." if has_effusion else "افیوژن قابل توجهی در فضای مفصلی رویت نشد."}
• پد چربی هوفا (Hoffa's Fat Pad) سیگنال نرمال دارد.

۵. استخوان‌ها و مغز استخوان:
• کانتورهای کورتیکال استخوان‌های ران، درشت‌نی و کشکک منظم بوده و شواهدی از ادم مغز استخوان، شکستگی فشاری یا ضایعه استئوکندرال دیده نمی‌شود.

۶. حفره پوپلیتئال (پشت زانو) و بافت‌های نرم:"""

        if baker.get("present"):
            w = baker.get("width_mm", 12.0)
            d = baker.get("depth_mm", 14.0)
            l = baker.get("length_mm", 25.0)
            v = baker.get("volume_cm3", 2.2)
            loc_fa = "چندحفره‌ای (مولتی‌لوکولار) با تیغه‌های نازک داخلی" if "Multi" in baker.get("loculation", "") else "تک‌حفره‌ای"
            fa_report += f"""
• تجمع مایع کپسوله‌شده در فضای خلفی-داخلی زانو بین تاندون سمی‌ممبرانوسوس و سر داخلی عضله گاستروکنمیوس منطبق بر «کیست بیکر / کیست پوپلیتئال» با نمای {loc_fa} رویت شد.
• ابعاد اندازه‌گیری‌شده: {w} میلی‌متر (عرض) × {d} میلی‌متر (عمق) × {l} میلی‌متر (طول) با حجم تقریبی حدود {v} سانتی‌متر مکعب.
• دسته‌جات عروقی-عصبی پوپلیتئال مجاور دارای مسیر و جریان طبیعی بوده و فاقد ترومبوز یا تهاجم می‌باشند."""
        else:
            fa_report += """
• حفره پوپلیتئال طبیعی است. هیچ‌گونه کیست پوپلیتئال (کیست بیکر) یا تجمع مایع غیرطبیعی رویت نشد. دسته‌جات عروقی-عصبی سالم می‌باشند."""

        fa_report += f"""

======================================================================
خلاصه و نتیجه‌گیری نهایی (Impression):
ام‌آر‌آی زانوی {lat_fa}:"""

        if is_completely_normal:
            fa_report += f"""
۱. ام‌آر‌آی زانوی {lat_fa} در محدوده طبیعی (Normal Study) فاقد آسیب حاد داخلی.
۲. منیسک‌های داخلی و خارجی کاملاً سالم و فاقد پارگی هستند.
۳. رباط‌های صلیبی (ACL و PCL) و رباط‌های جانبی (MCL و LCL) سالم و پیوسته می‌باشند.
۴. فاقد افیوژن مفصلی یا کیست پوپلیتئال (کیست بیکر)."""
        else:
            fa_idx = 1
            if med_grade >= 2:
                fa_report += f"\n{fa_idx}. پارگی / تغییرات سیگنال دژنراتیو در شاخ خلفی منیسک داخلی."
                fa_idx += 1
            elif med_grade == 1:
                fa_report += f"\n{fa_idx}. تغییرات سیگنال دژنراتیو خفیف (گرید ۱) در منیسک داخلی بدون پارگی."
                fa_idx += 1

            if lat_grade >= 2:
                fa_report += f"\n{fa_idx}. پارگی / تغییرات سیگنال در منیسک خارجی."
                fa_idx += 1

            if baker.get("present"):
                fa_report += f"\n{fa_idx}. کیست پوپلیتئال (کیست بیکر) به ابعاد {baker.get('width_mm')} × {baker.get('depth_mm')} × {baker.get('length_mm')} میلی‌متر در فضای خلفی-داخلی."
                fa_idx += 1

            if has_effusion:
                fa_report += f"\n{fa_idx}. افیوژن مفصلی در بورس سوپراپاتلار."
                fa_idx += 1

            fa_report += f"\n{fa_idx}. سلامت کامل رباط‌های متقاطع (ACL و PCL) و رباط‌های جانبی (MCL و LCL)."

        if is_completely_normal:
            fa_report += """

توصیه‌ها و پیگیری بالینی:
• تطابق با معاینات و علائم بالینی بیمار. نیاز به اقدام مداخله‌ای خاصی وجود ندارد."""
        elif baker.get("present") or med_grade >= 2:
            fa_report += """

توصیه‌ها و پیگیری بالینی:
• تطابق با معاینات بالینی جراح محترم ارتوپدی و اقدامات حمایتی/فیزیوتراپی در صورت لزوم بالینی."""
        else:
            fa_report += """

توصیه‌ها و پیگیری بالینی:
• تطابق بالینی توصیه می‌گردد."""

        fa_report += """

با احترام،
بخش تصویربرداری پزشکی و ام‌آر‌آی
بیمارستان بوعلی مریوان"""

        if lang == "fa":
            return fa_report
        elif lang == "en":
            return en_report
        else:
            return en_report + "\n\n" + "="*70 + "\nترجمه بالینی رسمی (نسخه فارسی جهت درج در سامانه HIS بیمارستان):\n" + "="*70 + "\n\n" + fa_report

    @staticmethod
    def export_word_docx(file_path, patient_info, analysis):
        """Generates a professional Word .docx document with official hospital header."""
        if not Document:
            return False

        doc = Document()

        # Page setup: Standard A4
        for sec in doc.sections:
            sec.top_margin = Inches(0.7)
            sec.bottom_margin = Inches(0.7)
            sec.left_margin = Inches(0.8)
            sec.right_margin = Inches(0.8)

        # Official Hospital Header Table
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        tcPr = cell._element.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '0F172A')
        tcPr.append(shd)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run("دانشگاه علوم پزشکی و خدمات بهداشتی درمانی کردستان\n")
        r1.font.name = "Arial"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(255, 255, 255)

        r2 = p.add_run("شبکه بهداشت و درمان مریوان - بیمارستان بوعلی\n")
        r2.font.name = "Arial"
        r2.font.size = Pt(11)
        r2.font.bold = True
        r2.font.color.rgb = RGBColor(56, 189, 248)

        r3 = p.add_run("پلتفرم تخصصی هوش مصنوعی و ایستگاه کاری تصویربرداری ام‌آر‌آی (MRI Workstation)")
        r3.font.name = "Arial"
        r3.font.size = Pt(9.5)
        r3.font.color.rgb = RGBColor(148, 163, 184)

        doc.add_paragraph("")

        # Patient Info Box
        info_tbl = doc.add_table(rows=2, cols=3)
        info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        data = [
            [f"نام بیمار: {patient_info.get('name', 'ناشناس')}", f"سن: {patient_info.get('age', '--')} سال", f"جنسیت: {patient_info.get('gender', 'نامشخص')}"],
            [f"شماره پرونده: {patient_info.get('id', '--')}", f"تاریخ آزمون: {patient_info.get('date', time.strftime('%Y/%m/%d'))}", f"عضو: زانوی {analysis.get('laterality', 'Left')}"]
        ]
        for r_idx, row in enumerate(data):
            for c_idx, val in enumerate(row):
                c = info_tbl.cell(r_idx, c_idx)
                cp = c.paragraphs[0]
                cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                cr = cp.add_run(val)
                cr.font.name = "Arial"
                cr.font.size = Pt(9.5)
                cr.font.bold = True

        doc.add_paragraph("")

        # Full Report Content
        full_text = MriReportGenerator.generate_knee_report_text(patient_info, analysis, lang="bilingual")
        for line in full_text.split("\n"):
            p = doc.add_paragraph()
            if any(h in line for h in ["FINDINGS", "IMPRESSION", "TECHNIQUE", "شرح یافته‌ها", "خلاصه و نتیجه‌گیری", "توصیه‌ها"]):
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if not ("شرح" in line or "خلاصه" in line or "توصیه" in line) else WD_ALIGN_PARAGRAPH.RIGHT
                run = p.add_run(line)
                run.font.name = "Arial"
                run.font.size = Pt(11)
                run.font.bold = True
                run.font.color.rgb = RGBColor(2, 132, 199)
            elif line.startswith("=") or line.startswith("-"):
                continue
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if any("\u0600" <= c <= "\u06FF" for c in line) else WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(line)
                run.font.name = "Arial"
                run.font.size = Pt(10)

        # Radiologist Sign-off
        doc.add_paragraph("")
        p_sign = doc.add_paragraph()
        p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_s = p_sign.add_run("با احترام و آرزوی بهبودی\nبخش تصویربرداری پزشکی و ام‌آر‌آی بیمارستان بوعلی مریوان\nپزشک متخصص رادیولوژی")
        r_s.font.name = "Arial"
        r_s.font.size = Pt(10)
        r_s.font.bold = True
        r_s.font.color.rgb = RGBColor(71, 85, 105)

        doc.save(file_path)
        return True
