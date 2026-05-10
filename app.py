import streamlit as st
import mysql.connector
import pandas as pd
import webbrowser

st.set_page_config(
    page_title="CarVilla Rental System",
    page_icon="🚗",
    layout="wide"
)
def get_db_connection():
    return mysql.connector.connect(
        host="viaduct.proxy.rlwy.net",
        port=29799,
        user="root",
        password="juAAbLmPALSFqYtiHHGwKCyZyapVRAyA",
        database="railway"
    )

# --- واجهة المستخدم ---
st.title("🚗 نظام CarVilla لإدارة تأجير السيارات")
st.markdown("---")

# إنشاء تبويبات (Tabs) لتنظيم الموقع بشكل احترافي
tab1, tab2, tab3, tab4 = st.tabs(["🚀 السيارات المتاحة", "👥 العملاء", "📅 سجل الحجوزات", "📊 التقارير المالية"])

# --- التبويب الأول: السيارات المتاحة ---
with tab1:
    st.header("قائمة السيارات المتاحة للإيجار")
    conn = get_db_connection()
    # تنفيذ استعلام الـ SQL المكتوب في ملفك
    query_cars = "SELECT car_id, model, brand, year, price, color FROM cars WHERE status = 'Available'"
    df_cars = pd.read_sql(query_cars, conn)
    
    if not df_cars.empty:
        # عرض السيارات في شكل أعمدة (Columns) كبديل للـ CSS
        cols = st.columns(2)
        for index, row in df_cars.iterrows():
            with cols[index % 2]:
                with st.container(border=True): # إطار بسيط لكل سيارة
                    st.subheader(f"{row['brand']} {row['model']}")
                    st.write(f"📅 سنة الصنع: {row['year']}")
                    st.write(f"🎨 اللون: {row['color']}")
                    st.write(f"💰 السعر: **${row['price']:,}**")
                    st.button(f"حجز {row['model']}", key=f"btn_{row['car_id']}")
    else:
        st.info("لا توجد سيارات متاحة حالياً.")
    conn.close()

# --- التبويب الثاني: العملاء ---
with tab2:
    st.header("بيانات العملاء")
    conn = get_db_connection()
    df_customers = pd.read_sql("SELECT customer_name, phone, email, address FROM customers", conn)
    st.table(df_customers) # عرض البيانات في جدول منظم
    conn.close()

# --- التبويب الثالث: الحجوزات (الربط بين الجداول) ---
with tab3:
    st.header("الحجوزات المؤكدة")
    conn = get_db_connection()
    # نفس الكود اللي إنت كاتبه في SQL (Inner Join)
    query_join = """
    SELECT customers.customer_name as 'العميل',
           cars.model as 'السيارة',
           cars.brand as 'الماركة',
           reservations.reservation_date as 'تاريخ الحجز',
           reservations.amount as 'المبلغ'
    FROM reservations
    INNER JOIN customers ON reservations.customer_id = customers.customer_id
    INNER JOIN cars ON reservations.car_id = cars.car_id;
    """
    df_res = pd.read_sql(query_join, conn)
    st.dataframe(df_res, use_container_width=True)
    conn.close()

# --- التبويب الرابع: التقارير المالية ---
with tab4:
    st.header("إجمالي الإيرادات اليومية")
    conn = get_db_connection()
    # كود الـ Group By اللي إنت كتبته
    query_report = """
    SELECT reservation_date, SUM(amount) as total_daily_payments
    FROM reservations
    GROUP BY reservation_date;
    """
    df_report = pd.read_sql(query_report, conn)
    
    if not df_report.empty:
        # عرض رسم بياني احترافي
        st.bar_chart(df_report.set_index('reservation_date'))
        st.write("ملخص المبالغ المحصلة:")
        st.write(df_report)
    conn.close()

# --- الشريط الجانبي لإضافة حجز (Sidebar) ---
st.sidebar.header("📝 تسجيل حجز جديد")
with st.sidebar.form("new_reservation"):
    c_id = st.number_input("رقم العميل", min_value=1)
    v_id = st.number_input("رقم السيارة", min_value=1)
    date = st.date_input("تاريخ الحجز")
    amt = st.number_input("المبلغ المدفوع", min_value=0.0)
    
    if st.form_submit_button("إضافة لـ SQL"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reservations (customer_id, car_id, reservation_date, amount) VALUES (%s, %s, %s, %s)", (c_id, v_id, date, amt))
            conn.commit()
            conn.close()
            st.sidebar.success("تم التحديث في قاعدة البيانات بنجاح!")
            st.rerun()
        except Exception as e: