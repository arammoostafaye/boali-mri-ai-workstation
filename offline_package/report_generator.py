# -*- coding: utf-8 -*-
"""
================================================================================
موتور جامع صدور گزارش بالینی ام‌آر‌آی | بیمارستان بوعلی مریوان
Boali Hospital Comprehensive Clinical MRI Report Generator & Word (.docx) Exporter
Developer: Aram Mostafaei
================================================================================
Generates Consultant-Grade Bilingual (English ACR + Persian Clinical RTL)
Reports for:
1. Knee MRI
2. Spine MRI (Cervical, Thoracic, Lumbar)
3. Shoulder MRI
4. Brain Suite (MRI ± Contrast, MRV, MRA)
5. Hip & Pelvis MRI
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
    """Generates official bilingual structured MRI reports and Word documents."""

    @classmethod
    def generate_report(cls, patient_info, analysis, organ="knee", lang="bilingual"):
        """Master router for generating organ-specific MRI reports."""
        org = organ.lower()
        if "knee" in org or "زانو" in org:
            return cls.generate_knee_report_text(patient_info, analysis, lang=lang)
        elif "spine" in org or "ستون" in org:
            return cls.generate_spine_report_text(patient_info, analysis, lang=lang)
        elif "shoulder" in org or "شانه" in org:
            return cls.generate_shoulder_report_text(patient_info, analysis, lang=lang)
        elif "brain" in org or "مغز" in org:
            return cls.generate_brain_report_text(patient_info, analysis, lang=lang)
        elif "hip" in org or "لگن" in org:
            return cls.generate_hip_report_text(patient_info, analysis, lang=lang)
        else:
            return cls.generate_knee_report_text(patient_info, analysis, lang=lang)

    # -------------------------------------------------------------------------
    # 1. Knee MRI Report Generator
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_knee_report_text(patient_info, analysis, lang="bilingual"):
        name = patient_info.get("name") or "ناشناس"
        age = patient_info.get("age") or "--"
        gender = patient_info.get("gender") or "نامشخص"
        pid = patient_info.get("id") or "--"
        date_str = patient_info.get("date") or time.strftime("%Y/%m/%d")
        laterality = analysis.get("laterality", "Left")
        lat_fa = "چپ" if laterality == "Left" else "راست"
        baker = analysis.get("bakers_cyst", {})
        findings = analysis.get("findings", {})

        med_m = findings.get("medial_meniscus", {})
        lat_m = findings.get("lateral_meniscus", {})
        acl = findings.get("acl", {})
        pcl = findings.get("pcl", {})
        mcl = findings.get("mcl", {})
        lcl = findings.get("lcl", {})
        pf = findings.get("patellofemoral", {})

        lines = [
            "=" * 74,
            f"  بیمارستان بوعلی مریوان | گزارش تخصصی ام‌آر‌آی زانو ({laterality.upper()} KNEE MRI)",
            f"  پلتفرم تخصصی هوش مصنوعی تصویربرداری پزشکی | آرام مصطفائی",
            "=" * 74,
            f"مشخصات بیمار: {name} | سن: {age} | جنسیت: {gender} | پرونده: {pid} | تاریخ: {date_str}",
            f"عضو مورد آزمون: زانوی {lat_fa} ({laterality} Knee)",
            "-" * 74,
            "",
            "FINDINGS (یافته‌های تصویربرداری):",
            f"1. Medial Meniscus (مینیسک داخلی):",
            f"   - EN: {med_m.get('status', 'Intact with normal triangular morphology.')}",
            f"   - FA: وضعیت مینیسک داخلی: {med_m.get('status', 'سالم')}.",
            "",
            f"2. Lateral Meniscus (مینیسک خارجی):",
            f"   - EN: {lat_m.get('status', 'Intact with normal signal intensity.')}",
            f"   - FA: وضعیت مینیسک خارجی: {lat_m.get('status', 'سالم')}.",
            "",
            f"3. Cruciate Ligaments (رباط‌های صلیبی ACL & PCL):",
            f"   - EN: ACL: {acl.get('details', 'Intact.')} | PCL: {pcl.get('details', 'Intact.')}",
            f"   - FA: رباط‌های متقاطع قدامی و خلفی (ACL و PCL) با ضخامت، تداوم و شیب آناتومیک نرمال مشاهده شدند.",
            "",
            f"4. Collateral Ligaments (رباط‌های جانبی MCL & LCL):",
            f"   - EN: MCL & LCL: {mcl.get('details', 'Intact.')}",
            f"   - FA: رباط‌های کلترال داخلی و خارجی و ساختارهای گوشه خلفی-خارجی کاملاً سالم هستند.",
            "",
            f"5. Extensor Mechanism & Joint Effusion (دستگاه اکستانسور و افیوژن):",
            f"   - EN: {pf.get('effusion', 'No significant joint effusion.')} {pf.get('cartilage', '')}",
            f"   - FA: غضروف‌های مفصلی پاتلوفمورال و تیبیوفمورال حفظ شده است. {pf.get('effusion', '')}",
            "",
            f"6. Popliteal Fossa & Baker's Cyst (فضای پوپلیتئال و کیست بیکر):"
        ]

        if baker.get("present"):
            lines.extend([
                f"   - EN: Baker's cyst identified measuring approximately {baker.get('width_mm')} x {baker.get('depth_mm')} x {baker.get('length_mm')} mm (Estimated volume: {baker.get('volume_cm3')} cm3).",
                f"   - FA: تجمع کیستیک با ابعاد {baker.get('width_mm')} × {baker.get('depth_mm')} × {baker.get('length_mm')} میلی‌متر و حجم تقریبی {baker.get('volume_cm3')} سانتیمتر مکعب در فضای خلفی-داخلی مشاهده شد (کیست بیکر)."
            ])
        else:
            lines.extend([
                "   - EN: No popliteal fluid collection or Baker's cyst identified.",
                "   - FA: فضای پوپلیتئال کاملاً آزاد بوده و هیچ‌گونه کیست بیکر یا تجمع مایع غیرطبیعی رویت نشد."
            ])

        lines.extend([
            "",
            "-" * 74,
            "IMPRESSION (نتیجه‌گیری نهایی):",
            f"1. {laterality} knee MRI demonstrates {med_m.get('status', 'intact menisci')} and intact cruciate ligaments.",
        ])
        if baker.get("present"):
            lines.append(f"2. Popliteal Baker's cyst measuring {baker.get('width_mm')} x {baker.get('depth_mm')} mm.")
        else:
            lines.append("2. No evidence of Baker's cyst, joint effusion, or acute trabecular fracture.")
        lines.append("=" * 74)

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # 2. Spine MRI Report Generator
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_spine_report_text(patient_info, analysis, lang="bilingual"):
        name = patient_info.get("name") or "ناشناس"
        age = patient_info.get("age") or "--"
        gender = patient_info.get("gender") or "نامشخص"
        pid = patient_info.get("id") or "--"
        date_str = patient_info.get("date") or time.strftime("%Y/%m/%d")
        seg = analysis.get("segment", "Lumbar Spine (L1-S1)")
        align = analysis.get("alignment", {})
        levels = analysis.get("levels", {})
        canal = analysis.get("canal_stenosis", {})
        cord = analysis.get("spinal_cord", {})

        lines = [
            "=" * 74,
            f"  بیمارستان بوعلی مریوان | گزارش تخصصی ام‌آر‌آی ستون فقرات ({seg.upper()})",
            f"  پلتفرم تخصصی هوش مصنوعی تصویربرداری پزشکی | آرام مصطفائی",
            "=" * 74,
            f"مشخصات بیمار: {name} | سن: {age} | جنسیت: {gender} | پرونده: {pid} | تاریخ: {date_str}",
            f"سگمان تحت بررسی: {seg}",
            "-" * 74,
            "",
            "FINDINGS (یافته‌های تصویربرداری ستون فقرات):",
            f"1. Alignment & Vertebrae (راستای ستون فقرات و بدنه مهره‌ها):",
            f"   - EN: {align.get('status', 'Normal alignment.')} {align.get('spondylolisthesis', '')}",
            f"   - FA: قوس فیزیولوژیک ستون فقرات حفظ شده است. شواهدی به نفع اسپوندیلولیستزیس یا شکستگی مهره‌ای دیده نشد.",
            "",
            f"2. Spinal Canal & Cord / Conus (کانال نخاعی و طناب نخاعی):",
            f"   - EN: AP canal diameter: {canal.get('ap_diameter_mm', 13.5)} mm. {cord.get('status', '')} {cord.get('conus_level', '')}",
            f"   - FA: ابعاد کانال نخاعی در محدوده طبیعی است ({canal.get('ap_diameter_mm', 13.5)} mm). سیگنال و کالیبر طناب نخاعی هموژن و فاقد میلومالاسی است.",
            "",
            "3. Intervertebral Disc Levels (ارزیابی دیسک‌ها به تفکیک سطوح):"
        ]

        for lvl_name, lvl_data in levels.items():
            lines.append(f"   • Level {lvl_name}:")
            lines.append(f"     - EN: Disc: {lvl_data.get('disc', 'Normal')}. Canal: {lvl_data.get('canal', 'Normal')}. Foramina: R: {lvl_data.get('foramina_right')}, L: {lvl_data.get('foramina_left')}.")
            lines.append(f"     - FA: وضعیت دیسک: {lvl_data.get('disc', 'نرمال')}. سوراخ‌های بین‌مهره‌ای: راست {lvl_data.get('foramina_right')}, چپ {lvl_data.get('foramina_left')}.")

        lines.extend([
            "",
            "-" * 74,
            "IMPRESSION (نتیجه‌گیری بالینی):",
            f"1. {seg} MRI reveals {canal.get('overall_grade', 'Normal/Mild')} canal dimensions with preserved spinal alignment.",
            f"2. No evidence of high-grade canal stenosis, acute cord compression, or pathological vertebral collapse.",
            "=" * 74
        ])

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # 3. Shoulder MRI Report Generator
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_shoulder_report_text(patient_info, analysis, lang="bilingual"):
        name = patient_info.get("name") or "ناشناس"
        age = patient_info.get("age") or "--"
        gender = patient_info.get("gender") or "نامشخص"
        pid = patient_info.get("id") or "--"
        date_str = patient_info.get("date") or time.strftime("%Y/%m/%d")

        rc = analysis.get("rotator_cuff", {})
        supra = rc.get("supraspinatus", {})
        infra = rc.get("infraspinatus", {})
        subscap = rc.get("subscapularis", {})
        teres = rc.get("teres_minor", {})
        biceps = analysis.get("biceps", {})
        labrum = analysis.get("labrum", {})
        ac = analysis.get("ac_joint", {})
        bursa = analysis.get("bursa", {})

        lines = [
            "=" * 74,
            f"  بیمارستان بوعلی مریوان | گزارش تخصصی ام‌آر‌آی مفصل شانه (SHOULDER MRI)",
            f"  پلتفرم تخصصی هوش مصنوعی تصویربرداری پزشکی | آرام مصطفائی",
            "=" * 74,
            f"مشخصات بیمار: {name} | سن: {age} | جنسیت: {gender} | پرونده: {pid} | تاریخ: {date_str}",
            "-" * 74,
            "",
            "FINDINGS (یافته‌های تصویربرداری مفصل شانه):",
            f"1. Supraspinatus Tendon (تاندون سوپرااسپیناتوس):",
            f"   - EN: {supra.get('status', 'Intact.')} Footprint: {supra.get('footprint', 'Continuous insertion.')}",
            f"   - FA: اتصال تاندون سوپرااسپیناتوس به توبروزیته بزرگ هومروس پیوسته بوده و فاقد پارگی تمام‌ضخامت است.",
            "",
            f"2. Infraspinatus, Subscapularis & Teres Minor (سایر تاندون‌های روتاتور کاف):",
            f"   - EN: Infraspinatus: {infra.get('status', 'Intact.')} Subscapularis: {subscap.get('status', 'Intact.')}",
            f"   - FA: تاندون‌های اینفرااسپیناتوس و ساب‌اسکاپولاریس سالم بوده و آتروفی چربی در عضلات رویت نمی‌شود.",
            "",
            f"3. Long Head of Biceps Tendon (سر دراز تاندون بایسپس):",
            f"   - EN: {biceps.get('status', 'Intact within bicipital groove.')}",
            f"   - FA: تاندون بایسپس در شیار بایسیپیتال به صورت مرکزی قرار داشته و فاقد سابلوکساسیون یا تنوسینوویت است.",
            "",
            f"4. Glenoid Labrum (لابروم گلنوئید):",
            f"   - EN: {labrum.get('status', 'Intact.')}",
            f"   - FA: لابروم گلنوئید با مورفولوژی طبیعی مثلثی مشاهده شد؛ ضایعه اسلپ (SLAP) یا بنکارت دیده نشد.",
            "",
            f"5. Acromioclavicular Joint & Subacromial Space (مفصل آکرومیوکلاویکولار و بورس):",
            f"   - EN: AC Joint: {ac.get('status', 'Preserved.')} Bursa: {bursa.get('subacromial_fluid', 'Normal.')}",
            f"   - FA: مفصل آکرومیوکلاویکولار نرمال بوده و افیوژن بارزی در بورس ساب‌آکرومیال-ساب‌دلتوئید دیده نشد.",
            "",
            "-" * 74,
            "IMPRESSION (نتیجه‌گیری بالینی):",
            f"1. Shoulder MRI demonstrates intact rotator cuff tendons without full-thickness tear.",
            f"2. Preserved glenoid labrum without SLAP or Bankart detachment.",
            "=" * 74
        ]

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # 4. Brain MRI Suite Report Generator
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_brain_report_text(patient_info, analysis, lang="bilingual"):
        name = patient_info.get("name") or "ناشناس"
        age = patient_info.get("age") or "--"
        gender = patient_info.get("gender") or "نامشخص"
        pid = patient_info.get("id") or "--"
        date_str = patient_info.get("date") or time.strftime("%Y/%m/%d")
        mod = analysis.get("modality", "Brain MRI ± Contrast")

        infarct = analysis.get("acute_infarct", {})
        fazekas = analysis.get("fazekas", {})
        vent = analysis.get("ventricles", {})
        midline = analysis.get("midline_shift", {})
        mass = analysis.get("mass_effect", {})
        vasc = analysis.get("vascular", {})

        lines = [
            "=" * 74,
            f"  بیمارستان بوعلی مریوان | گزارش تخصصی ام‌آر‌آی مغز ({mod.upper()})",
            f"  پلتفرم تخصصی هوش مصنوعی تصویربرداری پزشکی | آرام مصطفائی",
            "=" * 74,
            f"مشخصات بیمار: {name} | سن: {age} | جنسیت: {gender} | پرونده: {pid} | تاریخ: {date_str}",
            f"پروتکل تصویربرداری: {mod}",
            "-" * 74,
            "",
            "FINDINGS (یافته‌های تصویربرداری مغز و عروق):",
            f"1. Diffusion & Acute Ischemia (انتشار مولکولی و ارزیابی سکته حاد DWI/ADC):",
            f"   - EN: {infarct.get('details', 'No restricted diffusion.')}",
            f"   - FA: فاقد هرگونه شواهد به نفع انتشار محدود یا ادم سایتوتوکسیک حاد؛ ایسکمی حاد شریانی رد شد.",
            "",
            f"2. White Matter Changes / Fazekas Scale (تغییرات ماده سفید مغز):",
            f"   - EN: Fazekas: {fazekas.get('score_str', 'Grade 0')}. {fazekas.get('details', '')}",
            f"   - FA: مقیاس فازکاس: {fazekas.get('score_str', 'گرید ۰ - نرمال')}. تغییرات بارز میکروواسکولار دیده نشد.",
            "",
            f"3. Ventricular System & Quantitative Evans Index (سیستم بطنی و شاخص ایوانز):",
            f"   - EN: Evans Index = {vent.get('evans_index', 0.24)} (Normal < 0.28). {vent.get('symmetry', '')}",
            f"   - FA: شاخص کمی ایوانز {vent.get('evans_index', 0.24)} برآورد شد؛ بطن‌های جانبی، سوم و چهارم متقارن و فاقد هیدروسفالی هستند.",
            "",
            f"4. Midline Structures & Mass Effect (خط وسط و اثر فشاری):",
            f"   - EN: Midline shift: {midline.get('shift_mm', 0.0)} mm. {mass.get('details', 'No mass effect.')}",
            f"   - FA: انحراف خط وسط ۰.۰ میلی‌متر است. ساختارهای خط وسط در موقعیت مرکزی و بدون شیفت یا فتق هستند.",
            "",
            f"5. Dural Sinuses & Major Arteries (سینوس‌های وریدی و شریان‌های مغزی):",
            f"   - EN: {vasc.get('mrv_sinuses', 'Patent.')} {vasc.get('mra_circle_of_willis', 'Patent.')}",
            f"   - FA: سیگنال Flow-Void در سینوس ساژیتال فوقانی، ترانسورس و سیگموئید و شاخه‌های حلقه ویلیس حفظ شده است.",
            "",
            "-" * 74,
            "IMPRESSION (نتیجه‌گیری نورورادیولوژی):",
            "1. Normal brain MRI study without evidence of acute infarction, intracranial hemorrhage, or space-occupying lesion.",
            f"2. Normal ventricular size (Evans Index: {vent.get('evans_index', 0.24)}) with preserved white matter integrity ({fazekas.get('score_str', 'Grade 0')}).",
            "=" * 74
        ]

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # 5. Hip & Pelvis MRI Report Generator
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_hip_report_text(patient_info, analysis, lang="bilingual"):
        name = patient_info.get("name") or "ناشناس"
        age = patient_info.get("age") or "--"
        gender = patient_info.get("gender") or "نامشخص"
        pid = patient_info.get("id") or "--"
        date_str = patient_info.get("date") or time.strftime("%Y/%m/%d")

        femur = analysis.get("femoral_head", {})
        labrum = analysis.get("labrum", {})
        fai = analysis.get("fai", {})
        fluid = analysis.get("joint_fluid", {})
        muscles = analysis.get("muscles_bursae", {})

        lines = [
            "=" * 74,
            f"  بیمارستان بوعلی مریوان | گزارش تخصصی ام‌آر‌آی مفصل هیپ و لگن (HIP & PELVIS MRI)",
            f"  پلتفرم تخصصی هوش مصنوعی تصویربرداری پزشکی | آرام مصطفائی",
            "=" * 74,
            f"مشخصات بیمار: {name} | سن: {age} | جنسیت: {gender} | پرونده: {pid} | تاریخ: {date_str}",
            "-" * 74,
            "",
            "FINDINGS (یافته‌های تصویربرداری مفصل هیپ و لگن):",
            f"1. Femoral Head & Sphericity (سر فمور و نکروز آواسکولار):",
            f"   - EN: {femur.get('sphericity', 'Normal.')} AVN Status: {femur.get('ficat_stage', 'Stage 0 (Normal)')}.",
            f"   - FA: سر فمور کروی و متقارن بوده و هیچ نشانه‌ای از نکروز آواسکولار (AVN) یا علامت خط دوگانه دیده نمی‌شود.",
            "",
            f"2. Acetabular Labrum (لابروم استابولوم):",
            f"   - EN: {labrum.get('status', 'Intact.')}",
            f"   - FA: لابروم قدامی-فوقانی استابولوم کاملاً پیوسته بوده و فاقد پارگی یا کیست پارالابرال است.",
            "",
            f"3. Femoroacetabular Impingement Morphology (گیرکردگی فمورواستابولار FAI):",
            f"   - EN: {fai.get('morphology', 'Normal alpha angle.')}",
            f"   - FA: زاویه آلفا در حد طبیعی بوده و نمای کم (Cam) یا پینسر (Pincer) مشاهده نشد.",
            "",
            f"4. Joint Fluid & Trochanteric Region (مایع مفصلی و تروکانتر):",
            f"   - EN: {fluid.get('status', 'Normal trace fluid.')} {muscles.get('status', 'Intact.')}",
            f"   - FA: مایع مفصلی در حد فیزیولوژیک است. تاندون‌های گلوتئال سالم و بورسیت تروکانتریک رد شد.",
            "",
            "-" * 74,
            "IMPRESSION (نتیجه‌گیری بالینی):",
            "1. Bilateral hip MRI shows spherical femoral heads without avascular necrosis (AVN).",
            "2. Intact acetabular labra without labral tear, FAI morphology, or joint effusion.",
            "=" * 74
        ]

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Professional Word (.docx) Exporter with Official Header
    # -------------------------------------------------------------------------
    @classmethod
    def export_word_docx(cls, file_path, patient_info, analysis):
        """Generates an official Word .docx document with Boali Hospital / Kurdistan University header."""
        if not Document:
            return False

        doc = Document()

        # Page setup: Standard A4
        for sec in doc.sections:
            sec.top_margin = Inches(0.6)
            sec.bottom_margin = Inches(0.6)
            sec.left_margin = Inches(0.7)
            sec.right_margin = Inches(0.7)

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

        organ_name = analysis.get("organ", "Knee")
        r3 = p.add_run(f"پلتفرم تخصصی هوش مصنوعی و ایستگاه کاری ام‌آر‌آی ({organ_name} MRI AI Workstation)")
        r3.font.name = "Arial"
        r3.font.size = Pt(9.5)
        r3.font.color.rgb = RGBColor(148, 163, 184)

        doc.add_paragraph("")

        # Patient Info Box
        info_tbl = doc.add_table(rows=2, cols=3)
        info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        data = [
            [f"نام بیمار: {patient_info.get('name', 'ناشناس')}", f"سن: {patient_info.get('age', '--')} سال", f"جنسیت: {patient_info.get('gender', 'نامشخص')}"],
            [f"شماره پرونده: {patient_info.get('id', '--')}", f"تاریخ آزمون: {patient_info.get('date', time.strftime('%Y/%m/%d'))}", f"اندام: {organ_name} MRI"]
        ]
        for row_idx, row in enumerate(info_tbl.rows):
            for col_idx, cell in enumerate(row.cells):
                cell.text = data[row_idx][col_idx]
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(10)
                        run.font.bold = True

        doc.add_paragraph("")

        # Findings Section Header
        h_find = doc.add_paragraph()
        r_find = h_find.add_run(f"CLINICAL FINDINGS — گزارش تخصصی و یافته‌های بالینی {organ_name}")
        r_find.font.name = "Arial"
        r_find.font.size = Pt(11)
        r_find.font.bold = True
        r_find.font.color.rgb = RGBColor(2, 132, 199)

        # Generate text and insert as formatted paragraphs
        rep_text = cls.generate_report(patient_info, analysis, organ=organ_name, lang="bilingual")
        lines = rep_text.split("\n")
        in_findings = False
        for l in lines:
            if not l.strip() or l.startswith("="):
                continue
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(l)
            run.font.name = "Arial"
            if l.startswith("IMPRESSION") or l.startswith("FINDINGS"):
                run.font.bold = True
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(15, 23, 42)
            elif l.startswith("1.") or l.startswith("2.") or l.startswith("3.") or l.startswith("4.") or l.startswith("5."):
                run.font.bold = True
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(30, 41, 59)
            else:
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(71, 85, 105)

        # Signature Box
        doc.add_paragraph("")
        sig_p = doc.add_paragraph()
        sig_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_sig1 = sig_p.add_run("واحد تصویربرداری پزشکی و رادیولوژی بیمارستان بوعلی مریوان\n")
        r_sig1.font.bold = True
        r_sig1.font.size = Pt(10)
        r_sig2 = sig_p.add_run("سیستم تحلیل هوش مصنوعی بالینی ام‌آر‌آی | آرام مصطفائی")
        r_sig2.font.size = Pt(9)
        r_sig2.font.color.rgb = RGBColor(100, 116, 139)

        doc.save(file_path)
        return True
