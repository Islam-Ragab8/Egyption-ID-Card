"""
LLM Explanation Service
=======================
Uses Gemini to generate a human-readable Arabic explanation of the
verification verdict.  Falls back to a rule-based explanation when no
API key is configured or the LLM call fails.
"""

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


def _build_prompt(parsed_data: dict, decoded_data: dict, validation_result: dict) -> str:
    """Build an English prompt that instructs Gemini to respond in Arabic."""
    checks_text = ""
    for c in validation_result["checks"]:
        status = "PASS" if c["passed"] else "FAIL"
        checks_text += f"  - [{status}] {c['description']}: {c['message']}\n"

    prompt = f"""
You are an expert in Egyptian national ID card verification.
An Egyptian ID card has been analyzed and the results are listed below.

## Extracted Data
- First Name : {parsed_data.get('first_name', 'N/A')}
- Last Name  : {parsed_data.get('second_name', 'N/A')}
- Full Name  : {parsed_data.get('full_name', 'N/A')}
- National ID: {parsed_data.get('national_id', 'N/A')}
- Address    : {parsed_data.get('address', 'N/A')}

## Decoded from National ID
- Birth Date  : {decoded_data.get('Birth Date', 'N/A')}
- Governorate : {decoded_data.get('Governorate', 'N/A')}
- Gender      : {decoded_data.get('Gender', 'N/A')}

## Validation Results ({validation_result['passed_count']}/{validation_result['total_checks']} passed)
- Verdict: {validation_result['verdict']}
- Checks:
{checks_text}

## Instructions
Write a concise report **in Arabic** (3-5 sentences) that:
1. States whether the card was accepted or rejected, and why.
2. Lists any violations found (if any).
3. Gives a clear recommendation.

Use a professional and clear tone. If the card is valid, state that explicitly.
"""
    return prompt.strip()


def _fallback_explanation(validation_result: dict) -> str:
    """Rule-based fallback explanation when the LLM is unavailable."""
    verdict = validation_result["verdict"]
    violations = validation_result["violations"]

    if verdict == "VERIFIED":
        return (
            "تم التحقق من البطاقة بنجاح.\n\n"
            "كل الفحوصات اتعدت بنجاح — الرقم القومي صحيح 14 رقم، "
            "تاريخ الميلاد منطقي، كود المحافظة صحيح، "
            "وكل الحقول المطلوبة موجودة.\n\n"
            "**التوصية:** البطاقة سليمة ويمكن قبولها."
        )

    count = validation_result["failed_count"]
    lines = [f"البطاقة مرفوضة — تم رصد {count} مخالفة:\n"]

    for i, v in enumerate(violations, 1):
        lines.append(f"{i}. {v['message']}")

    lines.append("")
    lines.append(
        f"**التوصية:** البطاقة فيها {count} مخالفة — "
        "يُنصح برفضها ومراجعتها يدوياً."
    )

    return "\n".join(lines)


def generate_explanation(
    parsed_data: dict,
    decoded_data: dict,
    validation_result: dict,
) -> str:
    """
    Generate a human-readable Arabic explanation for the validation decision.

    Tries Gemini first; falls back to rule-based explanation.
    """
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)

            prompt = _build_prompt(parsed_data, decoded_data, validation_result)
            response = model.generate_content(prompt)

            if response and response.text:
                return response.text.strip()

        except Exception as e:
            print(f"LLM explanation failed, using fallback: {e}")

    return _fallback_explanation(validation_result)
