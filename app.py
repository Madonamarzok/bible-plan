import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import urllib.parse

# هنا رجعنا العناوين زي ما كانت بالضبط
st.set_page_config(page_title="Bible Plans", layout="centered", page_icon="📖")

st.title("📖 Bible Plans")
st.subheader("خطتك الشخصية للكتاب المقدس")

# --- باقي الكود بتاع تحميل البيانات والواجهة (زي ما هو) ---
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
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 تاريخ البداية", datetime.now())
    with col2:
        end_date = st.date_input("🏁 تاريخ النهاية", datetime.now() + timedelta(days=30))

    selected_books = st.multiselect("📚 اختاري الأسفار:", all_books)

    if st.button("توليد الجدول ✨"):
        if selected_books:
            chosen_df = df_bible[df_bible[col_name].isin(selected_books)].copy()
            chosen_df[col_chapters] = pd.to_numeric(chosen_df[col_chapters], errors='coerce')
            total_chapters = int(chosen_df[col_chapters].sum())
            num_days = (end_date - start_date).days + 1
            
            if num_days > 0:
                st.success(f"✅ الخطة جاهزة: {total_chapters} أصحاح على {num_days} يوم")
                
                all_chapters_list = []
                for _, row in chosen_df.iterrows():
                    for ch in range(1, int(row[col_chapters]) + 1):
                        all_chapters_list.append(f"{row[col_name]} {ch}")
                
                ch_per_day = total_chapters // num_days
                extra = total_chapters % num_days
                plan_data = []
                idx = 0
                
                for d in range(num_days):
                    count = ch_per_day + (1 if d < extra else 0)
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
                
                st.write("اضغطي على اللينك في عمود التنبيه لإضافة اليوم لتقويم موبايلك:")
                st.dataframe(
                    df_final,
                    column_config={
                        "تنبيه 🔔": st.column_config.LinkColumn("إضافة للتقويم 📅")
                    },
                    hide_index=True,
                )
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_final.drop(columns=["تنبيه 🔔"]).to_excel(writer, index=False, sheet_name='Plan')
                
                st.download_button(
                    label="📥 تحميل الجدول كاملاً (Excel)",
                    data=buffer.getvalue(),
                    file_name="My_Bible_Plan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.balloons()
            else:
                st.warning("⚠️ تاريخ النهاية غير منطقي!")
        else:
            st.warning("⚠️ اختاري سفر أولاً.")
