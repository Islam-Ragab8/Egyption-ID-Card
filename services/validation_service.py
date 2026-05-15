"""
Validation Service — التحقق من صحة بيانات البطاقة
===================================================

  7 فحوصات:
    1. required_fields    →  هل كل الحقول الأساسية موجودة؟
    2. nid_format         →  هل الرقم القومي 14 رقم؟
    3. century_digit      →  هل أول رقم 2 أو 3؟
    4. birth_date         →  هل التاريخ حقيقي ومنطقي؟
    5. governorate        →  هل كود المحافظة صحيح؟
    6. gender             →  هل رقم الجنس صحيح؟
    7. name_consistency   →  هل الاسم الأول متطابق مع الاسم الكامل؟

  النتيجة:
    - كلهم صح     →  VERIFIED  ✅
    - في مخالفات  →  REJECTED  🚨  +  عدد وأسماء المخالفات
"""

from datetime import date
from config.settings import GOVERNORATES



def _check_required_fields(parsed_data: dict) -> dict:
    """لازم كل الحقول الأساسية تكون موجودة."""
    missing = []
    required = {
        "first_name": "الاسم الأول",
        "second_name": "اسم العيلة",
        "address": "العنوان",
        "national_id": "الرقم القومي",
    }

    for field, arabic_name in required.items():
        value = parsed_data.get(field, "")
        if not value or not value.strip():
            missing.append(arabic_name)

    passed = len(missing) == 0
    return {
        "check": "required_fields",
        "description": "لازم كل الحقول الأساسية تكون موجودة",
        "passed": passed,
        "message": "كل الحقول موجودة" if passed else f"ناقص: {', '.join(missing)}",
    }


def _check_nid_format(nid: str) -> dict:
    """الرقم القومي لازم يكون 14 رقم بالظبط."""
    if not nid:
        return {
            "check": "nid_format",
            "description": "الرقم القومي لازم يكون 14 رقم",
            "passed": False,
            "message": "الرقم القومي مش موجود",
        }

    issues = []
    if len(nid) != 14:
        issues.append(f"{len(nid)} رقم بدل 14")
    if not nid.isdigit():
        issues.append("فيه حروف مش أرقام")

    passed = len(issues) == 0
    return {
        "check": "nid_format",
        "description": "الرقم القومي لازم يكون 14 رقم",
        "passed": passed,
        "message": "الرقم القومي سليم (14 رقم)" if passed else " — ".join(issues),
    }


def _check_century_digit(nid: str) -> dict:
    """أول رقم لازم يكون 2 (1900s) أو 3 (2000s)."""
    if len(nid) < 1 or not nid[0].isdigit():
        return {
            "check": "century_digit",
            "description": "رقم القرن لازم يكون 2 أو 3",
            "passed": False,
            "message": "مش قادر أحدد رقم القرن",
        }

    century = nid[0]
    passed = century in ("2", "3")
    return {
        "check": "century_digit",
        "description": "رقم القرن لازم يكون 2 أو 3",
        "passed": passed,
        "message": f"القرن: {century} ✓" if passed else f"رقم القرن ({century}) مش صحيح — لازم 2 أو 3",
    }


def _check_birth_date(nid: str) -> dict:
    """التاريخ المستخرج من الرقم القومي لازم يكون حقيقي ومنطقي."""
    if len(nid) < 7 or not nid[:7].isdigit():
        return {
            "check": "birth_date",
            "description": "تاريخ الميلاد لازم يكون تاريخ صحيح ومنطقي",
            "passed": False,
            "message": "مش قادر أستخرج تاريخ الميلاد",
        }

    century_digit = int(nid[0])
    if century_digit not in (2, 3):
        return {
            "check": "birth_date",
            "description": "تاريخ الميلاد لازم يكون تاريخ صحيح ومنطقي",
            "passed": False,
            "message": "رقم القرن مش صحيح — مش قادر أحسب التاريخ",
        }

    try:
        year = (1900 if century_digit == 2 else 2000) + int(nid[1:3])
        month = int(nid[3:5])
        day = int(nid[5:7])
        birth = date(year, month, day)

        today = date.today()
        age = (today - birth).days // 365

        if birth > today:
            return {
                "check": "birth_date",
                "description": "تاريخ الميلاد لازم يكون تاريخ صحيح ومنطقي",
                "passed": False,
                "message": f"تاريخ الميلاد ({birth}) في المستقبل!",
            }

        if age > 120:
            return {
                "check": "birth_date",
                "description": "تاريخ الميلاد لازم يكون تاريخ صحيح ومنطقي",
                "passed": False,
                "message": f"العمر ({age} سنة) مش منطقي",
            }

        return {
            "check": "birth_date",
            "description": "تاريخ الميلاد لازم يكون تاريخ صحيح ومنطقي",
            "passed": True,
            "message": f"تاريخ الميلاد: {birth} (العمر: {age} سنة)",
        }

    except ValueError:
        return {
            "check": "birth_date",
            "description": "تاريخ الميلاد لازم يكون تاريخ صحيح ومنطقي",
            "passed": False,
            "message": f"تاريخ الميلاد مش حقيقي (شهر: {nid[3:5]}, يوم: {nid[5:7]})",
        }


def _check_governorate(nid: str) -> dict:
    """كود المحافظة (الرقم 8 و 9) لازم يكون كود محافظة مصرية."""
    if len(nid) < 9:
        return {
            "check": "governorate",
            "description": "كود المحافظة لازم يكون صحيح",
            "passed": False,
            "message": "الرقم القومي قصير — مش قادر أحدد المحافظة",
        }

    gov_code = nid[7:9]
    gov_name = GOVERNORATES.get(gov_code)
    passed = gov_name is not None

    return {
        "check": "governorate",
        "description": "كود المحافظة لازم يكون صحيح",
        "passed": passed,
        "message": f"المحافظة: {gov_name}" if passed else f"كود المحافظة ({gov_code}) مش موجود في مصر",
    }


def _check_gender(nid: str) -> dict:
    """الرقم 13 — فردي = ذكر، زوجي = أنثى."""
    if len(nid) < 13 or not nid[12].isdigit():
        return {
            "check": "gender",
            "description": "رقم الجنس لازم يكون رقم صحيح",
            "passed": False,
            "message": "مش قادر أحدد رقم الجنس",
        }

    gender_digit = int(nid[12])
    gender = "ذكر" if gender_digit % 2 != 0 else "أنثى"

    return {
        "check": "gender",
        "description": "رقم الجنس لازم يكون رقم صحيح",
        "passed": True,
        "message": f"الجنس: {gender}",
    }


def _check_name_consistency(parsed_data: dict) -> dict:
    """الاسم الأول لازم يتطابق مع بداية الاسم الكامل."""
    first = parsed_data.get("first_name", "").strip()
    full = parsed_data.get("full_name", "").strip()

    # لو البيانات ناقصة — مش هنفشّل الفحص
    if not first or not full:
        return {
            "check": "name_consistency",
            "description": "الاسم الأول لازم يتطابق مع الاسم الكامل",
            "passed": True,
            "message": "مش قادر أتحقق — بيانات ناقصة",
        }

    passed = full.startswith(first)
    return {
        "check": "name_consistency",
        "description": "الاسم الأول لازم يتطابق مع الاسم الكامل",
        "passed": passed,
        "message": "الأسماء متطابقة" if passed else f"الاسم الأول ({first}) مش موجود في أول الاسم الكامل ({full})",
    }


# ─────────────────────────────────────────────
#  الفحص الرئيسي — بيشغّل كل الفحوصات
#  وبيطلع القرار النهائي
# ─────────────────────────────────────────────

def run_all_validations(parsed_data: dict) -> dict:
    """
    بيشغّل كل الفحوصات ويرجّع النتيجة النهائية + القرار.

    Args:
        parsed_data: Output from parsing_service.parse_extracted_fields()

    Returns:
        {
            "verdict": "VERIFIED" | "REJECTED",
            "is_valid": bool,
            "total_checks": int,
            "passed_count": int,
            "failed_count": int,
            "checks": [all check results with passed/failed],
            "violations": [failed checks only],
            "violation_names": [str, ...],
            "summary": str,
        }
    """
    nid = parsed_data.get("national_id", "")

    # ── تشغيل كل الفحوصات بالترتيب ──
    checks = [
        _check_required_fields(parsed_data),
        _check_nid_format(nid),
        _check_century_digit(nid),
        _check_birth_date(nid),
        _check_governorate(nid),
        _check_gender(nid),
        _check_name_consistency(parsed_data),
    ]

    # ── حساب النتائج ──
    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    violations = [c for c in checks if not c["passed"]]
    violation_names = [v["check"] for v in violations]

    is_valid = failed_count == 0
    verdict = "VERIFIED" if is_valid else "REJECTED"

    # ── ملخص بالعربي ──
    if is_valid:
        summary = "✅ البطاقة سليمة — كل الفحوصات اتعدت بنجاح"
    else:
        messages = "، ".join(v["message"] for v in violations)
        summary = f"🚨 البطاقة مرفوضة — {failed_count} مخالفة: {messages}"

    return {
        "verdict": verdict,
        "is_valid": is_valid,
        "total_checks": len(checks),
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "violations": violations,
        "violation_names": violation_names,
        "summary": summary,
    }
