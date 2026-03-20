import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Do-Bible-Na Plans", layout="centered", page_icon="📖")

st.title("📖 Do-Bible-Na Plans")
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
        st.error(f"❌ مشكلة في العناوين في ملف الإكسيل")
        all_books = []
        
except Exception as e:
    st.error(f"❌ تأكدي إن ملف {file_name} موجود ومرفوع على GitHub")
    all_books = []

# --- 2. الواجهة ---
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
        end_date = st.date_input("🏁 تاريخ النهاية", datetime.now() + timedelta(days=365))

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
                    plan_data.append({
                        "اليوم": d + 1,
                        "التاريخ": day_date.strftime("%Y-%m-%d"),
                        "القراءة": " + ".join(all_chapters_list[idx : idx + count])
                    })
                    idx += count
                
                df_final_plan = pd.DataFrame(plan_data)
                st.dataframe(df_final_plan, hide_index=True)
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_final_plan.to_excel(writer, index=False, sheet_name='Reading Plan')
                
                st.download_button(
                    label="📥 تحميل الجدول (Excel)",
                    data=buffer.getvalue(),
                    file_name=f"My_Bible_Plan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.info("💡 نصيحة: تقدري تفتحي الملف وتضيفي المواعيد لتقويم موبايلك.")
                st.balloons()
            else:
                st.warning("⚠️ تاريخ النهاية لازم يكون بعد تاريخ البداية!")
        else:
            st.warning("⚠️ من فضلك اختاري سفر واحد على الأقل.")
