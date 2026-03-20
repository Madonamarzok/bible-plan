import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import urllib.parse

st.set_page_config(page_title="Bible Plans", layout="centered", page_icon="📖")

st.title("📖 Bible Plans")
st.subheader("خطتك الشخصية للكتاب المقدس")

# --- 1. تحميل البيانات ---
file_name = "Bible_Data.xlsx"

try:
    df_bible = pd.read_excel(file_name)
    if "Table 1" in df_bible.columns or "Unnamed: 0" in df_bible.columns:
        df_bible = pd.read_excel(file_name, skiprows=1)
    
    df_bible.columns = df_bible.columns.str.strip()
    col_name = "اسم السفر"
    col_chapters = "عدد الأصحاحات"
    
    if col_name in df_bible.columns:
        all_books = df_bible[col_name].dropna().tolist()
    else:
        st.error(f"❌ مشكلة في عناوين الإكسيل")
        all_books = []
except Exception as e:
    st.error(f"❌ تأكدي من وجود ملف {file_name} على GitHub")
    all_books = []

if 'start_clicked' not in st.session_state:
    st.session_state.start_clicked = False

if not st.session_state.start_clicked:
    if st.button("Create your plan"):
        st.session_state.start_clicked = True
        st.rerun()

if st.session_state.start_clicked and all_books:
    st.write("---")
    
    # اختيار التواريخ
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 تاريخ البداية", datetime.now())
    with col2:
        end_date = st.date_input("🏁 تاريخ النهاية", datetime.now() + timedelta(days=30))

    # اختيار السفر وتحديد الأصحاحات
    selected_book = st.selectbox("📚 اختاري السفر:", [""] + all_books)
    
    if selected_book != "":
        max_ch = int(df_bible[df_bible[col_name] == selected_book][col_chapters].values[0])
        
        st.write(f"سفر {selected_book} فيه {max_ch} أصحاح.")
        c1, c2 = st.columns(2)
        with c1:
            from_ch = st.number_input("من أصحاح:", min_value=1, max_value=max_ch, value=1)
        with c2:
            to_ch = st.number_input("إلى أصحاح:", min_value=from_ch, max_value=max_ch, value=max_ch)

        if st.button("توليد الجدول ✨"):
            # إنشاء قائمة الأصحاحات المطلوبة بناءً على اختيار المستخدم
            all_chapters_list = [f"{selected_book} {ch}" for ch in range(from_ch, to_ch + 1)]
            total_chapters = len(all_chapters_list)
            num_days = (end_date - start_date).days + 1
            
            if num_days > 0:
                st.success(f"✅ الخطة جاهزة: {total_chapters} أصحاح على {num_days} يوم")
                
                ch_per_day = total_chapters // num_days
                extra = total_chapters % num_days
                plan_data = []
                idx = 0
                
                for d in range(num_days):
                    count = ch_per_day + (1 if d < extra else 0)
                    if count == 0: continue # لو الأيام أكتر من الأصحاحات
                    
                    day_date = start_date + timedelta(days=d)
                    reading = " + ".join(all_chapters_list[idx : idx + count])
                    
                    # لينك جوجل كلندر
                    base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
                    title = urllib.parse.quote(f"قراءة الكتاب المقدس: {reading}")
                    date_str = day_date.strftime("%Y%m%d")
                    cal_link = f"{base_url}&text={title}&dates={date_str}/{date_str}"
                    
                    plan_data.append({
                        "اليوم": d + 1,
                        "التاريخ": day_date.strftime("%Y-%m-%d"),
                        "القراءة": reading,
                        "تنبيه 🔔": cal_link
                    })
                    idx += count
                
                df_final = pd.DataFrame(plan_data)
                st.dataframe(
                    df_final,
                    column_config={"تنبيه 🔔": st.column_config.LinkColumn("إضافة للتقويم 📅")},
                    hide_index=True,
                )
                
                # زرار التحميل
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_final.drop(columns=["تنبيه 🔔"]).to_excel(writer, index=False, sheet_name='Plan')
                
                st.download_button(
                    label="📥 تحميل الجدول (Excel)",
                    data=buffer.getvalue(),
                    file_name="My_Bible_Plan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.balloons()
