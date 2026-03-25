import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import urllib.parse

st.set_page_config(page_title="Bible Plans", layout="centered", page_icon="📖")

st.title("📖 Bible Plans")
st.subheader("خطتك الشخصية المتقدمة")

# --- 1. تحميل البيانات ---
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

# --- 2. إدارة الجلسة ---
if 'display_list' not in st.session_state:
    st.session_state.display_list = []
if 'actual_chapters' not in st.session_state:
    st.session_state.actual_chapters = []

# --- 3. الواجهة الأساسية ---
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 تاريخ البداية", datetime.now())
with col2:
    end_date = st.date_input("🏁 تاريخ النهاية", datetime.now() + timedelta(days=30))

# --- ميزة المشاركة الجديدة ---
st.write("---")
with st.expander("🔗 شارك الخطة مع صديق (اختياري)"):
    friend_email = st.text_input("أدخل إيميل صديقك (Gmail):", placeholder="example@gmail.com")
    if friend_email:
        st.info(f"سيتم إضافة {friend_email} تلقائياً للمواعيد عند الضغط على زر التنبيه.")

st.write("---")
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
        summary_text = f"📖 سفر **{selected_book}** (من أصحاح **{from_ch}** إلى **{to_ch}**)"
        st.session_state.display_list.append(summary_text)
        new_chaps = [f"{selected_book} {ch}" for ch in range(from_ch, to_ch + 1)]
        st.session_state.actual_chapters.extend(new_chaps)
        st.success("تمت الإضافة!")

# --- 4. العرض والتوليد ---
if st.session_state.display_list:
    st.write("---")
    st.markdown("### 📝 تفاصيل خطتك الحالية:")
    for item in st.session_state.display_list:
        st.write(f"* {item}")
    
    if st.button("🗑️ مسح السلة"):
        st.session_state.display_list = []
        st.session_state.actual_chapters = []
        st.rerun()

    st.write("---")
    if st.button("✨ توليد الجدول النهائي ✨"):
        all_chapters_list = st.session_state.actual_chapters
        total_chapters = len(all_chapters_list)
        num_days = (end_date - start_date).days + 1
        
        if num_days > 0 and total_chapters > 0:
            ch_per_day = total_chapters // num_days
            extra = total_chapters % num_days
            plan_data = []
            idx = 0
            
            for d in range(num_days):
                count = ch_per_day + (1 if d < extra else 0)
                if count == 0: continue
                
                day_date = start_date + timedelta(days=d)
                reading = " + ".join(all_chapters_list[idx : idx + count])
                
                # إنشاء لينك جوجل كلندر مع ميزة الـ Guests
                base_url = "https://www.google.com/calendar/render?action=TEMPLATE"
                title = urllib.parse.quote(f"قراءة الكتاب المقدس: {reading}")
                date_str = day_date.strftime("%Y%m%d")
                
                # إضافة إيميل الصديق للينك لو موجود
                cal_link = f"{base_url}&text={title}&dates={date_str}/{date_str}"
                if friend_email:
                    cal_link += f"&add={urllib.parse.quote(friend_email)}"
                
                plan_data.append({
                    "اليوم": d + 1,
                    "التاريخ": day_date.strftime("%Y-%m-%d"),
                    "القراءة": reading,
                    "تنبيه مشترك 🔔": cal_link
                })
                idx += count
            
            df_final = pd.DataFrame(plan_data)
            st.dataframe(
                df_final,
                column_config={"تنبيه مشترك 🔔": st.column_config.LinkColumn("اضغط للتنبيه لك ولصديقك 🤝")},
                hide_index=True,
            )
            st.balloons()import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import urllib.parse

st.set_page_config(page_title="Bible Plans", layout="centered", page_icon="📖")

st.title("📖 Bible Plans")
st.subheader("خطتك الشخصية المتقدمة")

# --- 1. تحميل البيانات ---
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

# --- 2. إدارة سلة القراءات (تخزين التفاصيل) ---
if 'display_list' not in st.session_state:
    st.session_state.display_list = [] # لعرض النصوص (سفر كذا من كذا لكذا)
if 'actual_chapters' not in st.session_state:
    st.session_state.actual_chapters = [] # لحساب الأصحاحات الفعلية للجدول

# --- 3. الواجهة ---
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 تاريخ البداية", datetime.now())
with col2:
    end_date = st.date_input("🏁 تاريخ النهاية", datetime.now() + timedelta(days=30))

st.write("---")
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
        # 1. حفظ النص للعرض
        summary_text = f"📖 سفر **{selected_book}** (من أصحاح **{from_ch}** إلى **{to_ch}**)"
        st.session_state.display_list.append(summary_text)
        
        # 2. حفظ الأصحاحات الفعلية للحسابات
        new_chaps = [f"{selected_book} {ch}" for ch in range(from_ch, to_ch + 1)]
        st.session_state.actual_chapters.extend(new_chaps)
        st.success("تمت الإضافة بنجاح!")

# --- 4. عرض ملخص الخطة (طلبك هنا!) ---
if st.session_state.display_list:
    st.write("---")
    st.markdown("### 📝 تفاصيل خطتك الحالية:")
    
    # عرض كل جزء في سطر لوحده بنقطة
    for item in st.session_state.display_list:
        st.write(f"* {item}")
    
    st.info(f"🔢 إجمالي الأصحاحات المجمعة: **{len(st.session_state.actual_chapters)}**")
    
    if st.button("🗑️ مسح السلة"):
        st.session_state.display_list = []
        st.session_state.actual_chapters = []
        st.rerun()

    st.write("---")
    if st.button("✨ توليد الجدول النهائي ✨"):
        all_chapters_list = st.session_state.actual_chapters
        total_chapters = len(all_chapters_list)
        num_days = (end_date - start_date).days + 1
        
        if num_days > 0 and total_chapters > 0:
            ch_per_day = total_chapters // num_days
            extra = total_chapters % num_days
            plan_data = []
            idx = 0
            
            for d in range(num_days):
                count = ch_per_day + (1 if d < extra else 0)
                if count == 0: continue
                
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
                    "إضافة للتقويم 📅": cal_link
                })
                idx += count
            
            df_final = pd.DataFrame(plan_data)
            st.dataframe(
                df_final,
                column_config={"إضافة للتقويم 📅": st.column_config.LinkColumn("اضغط للتنبيه 🔔")},
                hide_index=True,
            )
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_final.drop(columns=["إضافة للتقويم 📅"]).to_excel(writer, index=False, sheet_name='Plan')
            
            st.download_button(label="📥 تحميل الجدول (Excel)", data=buffer.getvalue(), file_name="My_Bible_Plan.xlsx")
            st.balloons()
