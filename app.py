import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

# إعداد الصفحة
st.set_page_config(page_title="نظام تحليل البيانات الشامل", layout="wide", page_icon="📊")

# تجاهل التحذيرات
warnings.filterwarnings('ignore')

class ComprehensiveAnalysisSystem:
    """نظام تحليل بيانات شامل مع دعم اللغتين العربية والإنجليزية"""
    
    def __init__(self):
        self.df = None
        # قائمة التحليلات
        self.analysis_groups = {
            '1': 'تحليل المبيعات الأساسي',
            '2': 'تحليل المبيعات المتقدم',
            '3': 'تحليل المخزون الأساسي',
            '5': 'تحليل الموظفين الأساسي',
            '7': 'تحليل العملاء الأساسي',
        }
        
    def load_data(self, uploaded_file):
        """تحميل البيانات من ملف Streamlit"""
        try:
            if uploaded_file.name.endswith('.csv'):
                self.df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(uploaded_file)
            else:
                st.error("نوع الملف غير مدعوم. استخدم CSV أو Excel")
                return False
            
            st.success(f"✓ تم تحميل {len(self.df)} صف و {len(self.df.columns)} عمود بنجاح")
            with st.expander("عرض البيانات الأولية"):
                st.dataframe(self.df.head())
            st.info(f"الأعمدة المتاحة: {', '.join(self.df.columns)}")
            return True
        except Exception as e:
            st.error(f"✗ خطأ في تحميل البيانات: {str(e)}")
            return False
    
    def safe_calculate(self, func, default=0):
        """تنفيذ آمن للعمليات الحسابية"""
        try:
            result = func()
            return result if pd.notna(result) else default
        except Exception as e:
            st.warning(f"تحذير حسابي: {str(e)}")
            return default
    
    # ==================== المجموعة 1: تحليل المبيعات الأساسي ====================
    def group1_basic_sales(self, sales_col='المبيعات', profit_col='الربح', 
                          product_col='المنتج', region_col='المنطقة',
                          category_col='الفئة', customer_col='العميل',
                          date_col='التاريخ'):
        
        st.markdown("### 📊 المجموعة 1: تحليل المبيعات الأساسي")
        st.markdown("---")
        
        results = {}
        
        col1, col2 = st.columns(2)
        
        # 1. إجمالي المبيعات
        if sales_col in self.df.columns:
            results['إجمالي المبيعات'] = self.safe_calculate(lambda: self.df[sales_col].sum())
            col1.metric("إجمالي المبيعات", f"{results['إجمالي المبيعات']:,.2f}")
        
        # 2. إجمالي الأرباح
        if profit_col in self.df.columns:
            results['إجمالي الأرباح'] = self.safe_calculate(lambda: self.df[profit_col].sum())
            col2.metric("إجمالي الأرباح", f"{results['إجمالي الأرباح']:,.2f}")
        
        # 3. أفضل 10 منتجات
        if product_col in self.df.columns and sales_col in self.df.columns:
            st.subheader("3. أفضل 10 منتجات مبيعاً")
            top_products = self.df.groupby(product_col)[sales_col].sum().nlargest(10)
            st.bar_chart(top_products)
            st.dataframe(top_products, use_container_width=True)
        
        # 4. أقل 10 منتجات
        if product_col in self.df.columns and sales_col in self.df.columns:
            st.subheader("4. أقل 10 منتجات مبيعاً")
            bottom_products = self.df.groupby(product_col)[sales_col].sum().nsmallest(10)
            st.dataframe(bottom_products, use_container_width=True)
        
        # 5. المبيعات حسب المنطقة
        if region_col in self.df.columns and sales_col in self.df.columns:
            st.subheader("5. المبيعات حسب المنطقة")
            sales_by_region = self.df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
            st.dataframe(sales_by_region, use_container_width=True)
        
        # 6. المبيعات حسب الفئة
        if category_col in self.df.columns and sales_col in self.df.columns:
            st.subheader("6. المبيعات حسب الفئة")
            sales_by_category = self.df.groupby(category_col)[sales_col].sum().sort_values(ascending=False)
            st.dataframe(sales_by_category, use_container_width=True)
        
        # 7. المبيعات حسب العميل
        if customer_col in self.df.columns and sales_col in self.df.columns:
            st.subheader("7. أفضل 10 عملاء")
            sales_by_customer = self.df.groupby(customer_col)[sales_col].sum().nlargest(10)
            st.dataframe(sales_by_customer, use_container_width=True)
        
        # 8. المبيعات حسب الشهر
        if date_col in self.df.columns and sales_col in self.df.columns:
            st.subheader("8. المبيعات حسب الشهر")
            try:
                self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
                sales_by_month = self.df.groupby(self.df[date_col].dt.to_period('M').astype(str))[sales_col].sum()
                st.line_chart(sales_by_month)
            except Exception as e:
                st.error(f"خطأ في معالجة التاريخ: {e}")
        
        return results

    # ==================== المجموعة 2: تحليل المبيعات المتقدم ====================
    def group2_advanced_sales(self, sales_col='المبيعات', profit_col='الربح',
                             product_col='المنتج', category_col='الفئة',
                             price_col='السعر', channel_col='القناة',
                             stock_col='المخزون', promo_col='ترويج',
                             date_col='التاريخ'):
        
        st.markdown("### 📈 المجموعة 2: تحليل المبيعات المتقدم")
        st.markdown("---")
        
        results = {}
        
        # 11. معدل الربح لكل منتج
        if product_col in self.df.columns and profit_col in self.df.columns:
            st.subheader("11. معدل الربح لكل منتج (أعلى 10)")
            profit_per_product = self.df.groupby(product_col)[profit_col].mean().nlargest(10)
            st.dataframe(profit_per_product, use_container_width=True)
        
        # 13. متوسط سعر البيع
        if price_col in self.df.columns:
            avg_price = self.df[price_col].mean()
            st.metric("13. متوسط سعر البيع", f"{avg_price:,.2f}")
        
        # 14. هامش الربح
        if sales_col in self.df.columns and profit_col in self.df.columns:
            try:
                self.df['هامش_الربح'] = (self.df[profit_col] / self.df[sales_col] * 100)
                st.subheader("14. متوسط هامش الربح لكل منتج (أعلى 10)")
                margin_by_product = self.df.groupby(product_col)['هامش_الربح'].mean().nlargest(10)
                st.dataframe(margin_by_product, use_container_width=True)
            except Exception as e:
                st.warning("تعذر حساب هامش الربح")

        # 17. المبيعات الموسمية
        if date_col in self.df.columns and sales_col in self.df.columns:
            st.subheader("17. المبيعات الموسمية (حسب الشهر)")
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            seasonal_sales = self.df.groupby(self.df[date_col].dt.month)[sales_col].sum()
            st.bar_chart(seasonal_sales)

        return results

    # ==================== المجموعة 3: تحليل المخزون الأساسي ====================
    def group3_basic_inventory(self, stock_col='المخزون', product_col='المنتج',
                               category_col='الفئة', warehouse_col='المستودع',
                               sales_col='المبيعات'):
        
        st.markdown("### 📦 المجموعة 3: تحليل المخزون الأساسي")
        st.markdown("---")
        
        results = {}
        
        # 21. إجمالي المخزون
        if stock_col in self.df.columns:
            total_stock = self.df[stock_col].sum()
            st.metric("21. إجمالي المخزون", f"{total_stock:,.0f}")
        
        # 22. المخزون حسب المنتج
        if product_col in self.df.columns and stock_col in self.df.columns:
            st.subheader("22. أعلى 10 منتجات في المخزون")
            stock_by_product = self.df.groupby(product_col)[stock_col].sum().nlargest(10)
            st.dataframe(stock_by_product, use_container_width=True)

        # 25. المنتجات منخفضة المخزون
        if stock_col in self.df.columns and product_col in self.df.columns:
            st.subheader("25. المنتجات منخفضة المخزون (أقل 10)")
            low_stock = self.df.nsmallest(10, stock_col)[[product_col, stock_col]]
            st.dataframe(low_stock, use_container_width=True)

        return results
    
    # ==================== المجموعة 5: تحليل الموظفين الأساسي ====================
    def group5_basic_employees(self, dept_col='القسم', role_col='الدور',
                              salary_col='الراتب', date_col='تاريخ_التوظيف',
                              status_col='الحالة', attendance_col='الحضور'):
        
        st.markdown("### 👥 المجموعة 5: تحليل الموظفين الأساسي")
        st.markdown("---")
        
        results = {}
        
        # 41. عدد الموظفين حسب القسم
        if dept_col in self.df.columns:
            st.subheader("41. عدد الموظفين حسب القسم")
            emp_by_dept = self.df[dept_col].value_counts()
            st.dataframe(emp_by_dept, use_container_width=True)
        
        # 43. متوسط الراتب حسب القسم
        if dept_col in self.df.columns and salary_col in self.df.columns:
            st.subheader("43. متوسط الراتب حسب القسم")
            avg_salary_dept = self.df.groupby(dept_col)[salary_col].mean()
            st.dataframe(avg_salary_dept, use_container_width=True)

        return results

    # ==================== المجموعة 7: تحليل العملاء الأساسي ====================
    def group7_basic_customers(self, customer_col='العميل', date_col='التاريخ',
                              status_col='الحالة'):
        
        st.markdown("### 🤝 المجموعة 7: تحليل العملاء الأساسي")
        st.markdown("---")
        
        results = {}
        
        # 61. عدد العملاء الكلي
        if customer_col in self.df.columns:
            total_customers = self.df[customer_col].nunique()
            st.metric("61. عدد العملاء الكلي", f"{total_customers:,}")
        
        # 62. العملاء الجدد
        if customer_col in self.df.columns and date_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            new_customers = self.df[self.df[date_col] >= (datetime.now() - timedelta(days=30))][customer_col].nunique()
            st.metric("62. العملاء الجدد (آخر 30 يوم)", f"{new_customers:,}")
        
        # 63. العملاء النشطين (هنا كان الخطأ وتم إصلاحه)
        if status_col in self.df.columns:
            active_customers = len(self.df[self.df[status_col].str.contains('نشط|active', case=False, na=False)])
            st.metric("63. العملاء النشطين", f"{active_customers}")
        
        return results

# ==============================================================================
# واجهة تشغيل التطبيق (Streamlit Execution Logic)
# ==============================================================================

def main():
    st.title("🚀 نظام MAS لتحليل البيانات")
    st.write("قم برفع ملف البيانات (CSV أو Excel) وسيقوم النظام بالتحليل التلقائي.")
    
    # 1. رفع الملف
    uploaded_file = st.file_uploader("اختر ملف البيانات", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        # إنشاء نسخة من النظام
        system = ComprehensiveAnalysisSystem()
        
        # تحميل البيانات
        if system.load_data(uploaded_file):
            
            # 2. إعدادات الأعمدة (اختياري لتعيين الأسماء الصحيحة)
            st.sidebar.header("🔧 إعدادات الأعمدة")
            st.sidebar.info("تأكد أن أسماء الأعمدة في ملفك تتطابق مع الافتراضية أو اخترها من هنا:")
            
            cols = system.df.columns.tolist()
            
            # قوائم اختيار الأعمدة لربطها بالكود
            c_sales = st.sidebar.selectbox("عمود المبيعات", cols, index=cols.index('المبيعات') if 'المبيعات' in cols else 0)
            c_date = st.sidebar.selectbox("عمود التاريخ", cols, index=cols.index('التاريخ') if 'التاريخ' in cols else 0)
            c_product = st.sidebar.selectbox("عمود المنتج", cols, index=cols.index('المنتج') if 'المنتج' in cols else 0)
            c_profit = st.sidebar.selectbox("عمود الربح", cols, index=cols.index('الربح') if 'الربح' in cols else 0)
            
            # 3. اختيار التحليل
            st.header("🔍 اختر نوع التحليل")
            analysis_type = st.selectbox(
                "القائمة",
                list(system.analysis_groups.values())
            )
            
            run_btn = st.button("بدء التحليل")
            
            if run_btn:
                if analysis_type == 'تحليل المبيعات الأساسي':
                    system.group1_basic_sales(sales_col=c_sales, date_col=c_date, product_col=c_product, profit_col=c_profit)
                
                elif analysis_type == 'تحليل المبيعات المتقدم':
                    system.group2_advanced_sales(sales_col=c_sales, date_col=c_date, product_col=c_product, profit_col=c_profit)
                
                elif analysis_type == 'تحليل المخزون الأساسي':
                    # يمكنك إضافة Selectbox لعمود المخزون إذا أردت
                    c_stock = 'المخزون' if 'المخزون' in cols else cols[0]
                    system.group3_basic_inventory(stock_col=c_stock, product_col=c_product, sales_col=c_sales)
                    
                elif analysis_type == 'تحليل الموظفين الأساسي':
                    system.group5_basic_employees()
                    
                elif analysis_type == 'تحليل العملاء الأساسي':
                    system.group7_basic_customers(date_col=c_date, sales_col=c_sales)

if __name__ == "__main__":
    main()
