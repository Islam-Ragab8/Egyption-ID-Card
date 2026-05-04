"""
Home page — Upload an ID card image and view the full verification result.
"""

import os
import tempfile

from PIL import Image
import streamlit as st

from config.settings import DETECTION_OUTPUT_PATH, SUPPORTED_IMAGE_FORMATS
from services.pipeline import process_id_card


def _render_verdict_banner(result):
    """Show the final verdict at the top."""
    if result.verdict == "VERIFIED":
        st.success("## VERIFIED — البطاقة سليمة")
        st.balloons()
    else:
        st.error(f"## REJECTED — بطاقة مرفوضة ({result.failed_count} مخالفة)")


def _render_extracted_data(result):
    """Show extracted fields in a clean layout."""
    st.markdown("### البيانات المستخرجة")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("الاسم الأول", value=result.extracted.get("first_name", ""), disabled=True)
        st.text_input("الاسم الكامل", value=result.extracted.get("full_name", ""), disabled=True)
        st.text_input("العنوان", value=result.extracted.get("address", ""), disabled=True)
    with col2:
        st.text_input("اسم العيلة", value=result.extracted.get("second_name", ""), disabled=True)
        st.text_input("الرقم القومي", value=result.extracted.get("national_id", ""), disabled=True)
        st.text_input("السيريال", value=result.extracted.get("serial", ""), disabled=True)


def _render_decoded_nid(result):
    """Show decoded NID information."""
    st.markdown("### البيانات المفكوكة من الرقم القومي")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("تاريخ الميلاد", result.decoded["birth_date"])
    with col2:
        st.metric("المحافظة", result.decoded["governorate"])
    with col3:
        st.metric("الجنس", result.decoded["gender"])


def _render_validation(result):
    """Show all validation checks, violations, and explanation."""
    st.markdown("### نتائج الفحوصات")

    validation = result.validation

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الفحوصات", validation["total_checks"])
    with col2:
        st.metric("نجح", validation["passed_count"])
    with col3:
        st.metric("فشل", validation["failed_count"])

    # All checks as expanders
    for check in validation["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        with st.expander(f"[{status}] {check['description']}"):
            st.write(check["message"])

    # Violations summary
    if validation["violations"]:
        st.markdown("---")
        st.markdown("### المخالفات المكتشفة")
        for v in validation["violations"]:
            st.write(f"- **{v['check']}**: {v['message']}")
    else:
        st.info("لا يوجد مخالفات — كل الفحوصات اتعدت بنجاح")

    # LLM Explanation
    st.markdown("---")
    st.markdown("### شرح القرار")
    st.markdown(result.explanation)


def render():
    """Render the Home tab."""
    uploaded_file = st.sidebar.file_uploader(
        "ارفع صورة البطاقة", type=SUPPORTED_IMAGE_FORMATS
    )

    if not uploaded_file:
        st.markdown(
            """
            <div style="text-align: center; padding: 80px 20px;">
                <h1>HUWIYA</h1>
                <h3>نظام التحقق من البطاقة المصرية</h3>
                <p style="font-size: 18px; color: #888;">
                    ارفع صورة بطاقة هوية مصرية من الشريط الجانبي لبدء التحقق
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    image = Image.open(temp_path)
    st.sidebar.image(image, caption="الصورة المرفوعة")

    try:
        with st.spinner("جاري تحليل البطاقة..."):
            result = process_id_card(temp_path)

        # Show annotated detection image
        if os.path.exists(DETECTION_OUTPUT_PATH):
            st.image(
                Image.open(DETECTION_OUTPUT_PATH),
                caption="الحقول المكتشفة",
                use_container_width=True,
            )

        st.markdown("---")

        # Verdict Banner
        _render_verdict_banner(result)
        st.markdown("---")

        # All sections in tabs
        tab1, tab2, tab3 = st.tabs([
            "البيانات", "الرقم القومي", "الفحوصات والقرار"
        ])

        with tab1:
            _render_extracted_data(result)

        with tab2:
            _render_decoded_nid(result)

        with tab3:
            _render_validation(result)

    except ValueError as e:
        st.error(f"مش بطاقة هوية — ارفع صورة تانية\n\n{e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        st.error(f"حصل خطأ: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
