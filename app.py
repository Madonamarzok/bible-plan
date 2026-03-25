import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import urllib.parse

st.set_page_config(page_title="Bible Plans", layout="centered", page_icon="📖")

# --- 1. تهيئة الذاكرة (عشان يفتكر جدولك) ---
if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = False

# --- 2. تحميل البيانات ---
file_name = "Bible_Data.xlsx"
try:
    df_bible = pd.read_excel(file_name)
    if "Table 1" in df_bible.columns or "Unnamed: 0" in df_bible.columns:
        df_bible = pd.read_excel(file_name, skiprows=1)
    df_bible.columns = df_bible.columns.str.strip()
    col_name = "اسم السفر"
    col_chapters = "عدد الأصحاحات"
    all_books = df_bible[col_name].dropna().tolist()
except:
    st.error("❌ تأكدي من ملف الإكسيل")
    st.stop()

# --- 3. إدارة التنقل بين "الإعداد" و "العرض" ---
if st.session_state.view_mode and st.session_state.generated_plan is not None:
    # ---------------- صفحة عرض الجدول والمتابعة ----------------
    st.title("✅ متابعة إنجازك اليومي")
    st.write("علمي على الأصحاحات اللي قريتيها.. ربنا معاكي!")

    # عرض الجدول كـ Data Editor عشان التشيك بوكس يشتغل
    edited_df = st.data_editor(
        st.session_state.generated_plan,
        column_config={
            "خلصت؟ ✅": st.column_config.CheckboxColumn("خلصت؟ ✅", default=False),
            "تنبيه مشترك 🔔": None # نخفيه هنا عشان الشكل يبقى أنضف
        },
        disabled=["اليوم", "التاريخ", "القراءة"],
        hide_index=True,
        use_container_width=True
    )
    
    # حفظ حالة التشيك بوكس فوراً
    st.session_state.generated_plan = edited_df

    st.write("---")
    if st.button("🔙 العودة لتعديل الخطة"):
        st.session_state.view_mode = False
        st.rerun()

else:
    # ---------------- صفحة إعداد الخطة (القديمة) ----------------
    st.title("📖 Bible Plans")
    st.subheader("خطتك الشخصية المتقدمة")

    if 'display_list' not in st.session_state:
        st.session_state.display_list = []
    if 'actual_chapters' not in st.session_state:
        st.session_state.actual_chapters = []

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 تاريخ البداية", datetime.now())
    with col2:
        end_date = st.date_input("🏁 تاريخ النهاية", datetime.now() + timedelta(days=30))

    st.write("---")
    with st.expander("🔗 شارك الخطة مع صديق (اختياري)"):
        friend_email = st.text_input("أدخل إيميل صديقك (Gmail):", placeholder="example@gmail.com")

    st.markdown("### ➕ أضيفي أجزاء للخطة")
    selected_book = st.selectbox("اختر السفر:", [""] + all_books)

    if selected_book:
        max_ch = int(df_bible[df_bible[col_name] == selected_book][col_chapters].values[0])
        c1, c2 = st.columns(2)
        with c1:
            from_ch = st.number_input("من أصحاح:", min_value=1, max_value=max_ch, value=1)
        with c2:
            to_ch = st.number_input("إلى أصحاح:", min_value=from_ch, max_value=max_ch, value=max_ch)
        
        if st.button("➕ إضافة للسلة"):
            st.session_state.display_list.append(f"📖 {selected_book} ({from_ch}-{to_ch})")
            new_chaps = [f"{selected_book} {ch}" for ch in range(from_ch, to_ch + 1)]
            st.session_state.actual_chapters.extend(new_chaps)
            st.success("تمت الإضافة!")

    if st.session_state.display_list:
        st.write("---")
        for item in st.session_state.display_list:
            st.write(f"* {item}")
        
        if st.button("🗑️ مسح السلة"):
            st.session_state.display_list = []
            st.session_state.actual_chapters = []
            st.session_state.generated_plan = None
            st.rerun()

        if st.button("✨ توليد الجدول النهائي ✨"):
            all_chapters_list = st.session_state.actual_chapters
            total_chapters = len(all_chapters_list)
            num_days = (end_date - start_date).days + 1
            
            if num_days > 0 and total_chapters > 0:
                plan_data = []
                ch_per_day = total_chapters // num_days
                extra = total_chapters % num_days
                idx = 0
                for d in range(num_days):
                    count = ch_per_day + (1 if d < extra else 0)
                    if count == 0: continue
                    day_date = start_date + timedelta(days=d)
                    reading = " + ".join(all_chapters_list[idx : idx + count])
                    
                    base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
                    title = urllib.parse.quote(f"قراءة: {reading}")
                    date_str = day_date.strftime("%Y%m%d")
                    cal_link = f"{base_url}&text={title}&dates={date_str}/{date_str}"
                    if friend_email:
                        cal_link += f"&add={urllib.parse.quote(friend_email)}"

                    plan_data.append({
                        "خلصت؟ ✅": False,
                        "اليوم": d + 1,
                        "التاريخ": day_date.strftime("%Y-%m-%d"),
                        "القراءة": reading,
                        "تنبيه مشترك 🔔": cal_link
                    })
                    idx += count
                
                st.session_state.generated_plan = pd.DataFrame(plan_data)
                st.balloons()

        # زرار عرض الجدول (الجديد)
        if st.session_state.generated_plan is not None:
            st.write("---")
            if st.button("📲 عرض الجدول وتتبع الإنجاز"):
                st.session_state.view_mode = True
                st.rerun()

            # زرار التحميل يفضل موجود
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                st.session_state.generated_plan.to_excel(writer, index=False)
            st.download_button("📥 تحميل الجدول (Excel)", data=buffer.getvalue(), file_name="My_Plan.xlsx")
