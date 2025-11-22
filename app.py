import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveAnalysisSystem:
    """نظام تحليل بيانات شامل مع دعم اللغتين العربية والإنجليزية"""
    
    def __init__(self):
        self.df = None
        self.analysis_groups = {
            '1': 'تحليل المبيعات الأساسي',
            '2': 'تحليل المبيعات المتقدم',
            '3': 'تحليل المخزون الأساسي',
            '4': 'تحليل المخزون المتقدم',
            '5': 'تحليل الموظفين الأساسي',
            '6': 'تحليل الموظفين المتقدم',
            '7': 'تحليل العملاء الأساسي',
            '8': 'تحليل العملاء المتقدم',
            '9': 'تحليل التسويق الأساسي',
            '10': 'تحليل التسويق المتقدم',
            '11': 'تحليل الطلاب الأساسي',
            '12': 'تحليل الطلاب المتقدم',
            '13': 'تحليل المشتريات الأساسي',
            '14': 'تحليل المشتريات المتقدم',
            '15': 'تحليل المبيعات حسب الوقت',
            '16': 'تحليل المبيعات حسب المنتجات',
            '17': 'تحليل المخزون حسب المنتجات',
            '18': 'تحليل المخزون حسب الوقت',
            '19': 'تحليل الموظفين حسب الوقت',
            '20': 'تحليل الأداء الوظيفي',
            '21': 'تحليل العملاء والمبيعات',
            '22': 'تحليل التسويق',
            '23': 'تحليل التسويق المتقدم',
            '24': 'تحليل خدمة العملاء',
            '25': 'تحليل التسويق والمبيعات المتقدم',
            '26': 'تحليل سلسلة التوريد',
            '27': 'تحليل خدمة العملاء المتقدم',
            '28': 'تحليل التسويق الرقمي',
            '29': 'تحليل الموارد البشرية',
            '30': 'تحليل الطلاب والتعليم',
            '31': 'تحليل المخزون المتقدم',
            '32': 'تحليل المشتريات الشامل'
        }
        
    def load_data(self, file_path):
        """تحميل البيانات من ملف"""
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path, encoding='utf-8-sig')
            elif file_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_path)
            else:
                raise ValueError("نوع الملف غير مدعوم. استخدم CSV أو Excel")
            
            print(f"✓ تم تحميل {len(self.df)} صف و {len(self.df.columns)} عمود بنجاح")
            print(f"الأعمدة المتاحة: {', '.join(self.df.columns)}")
            return True
        except Exception as e:
            print(f"✗ خطأ في تحميل البيانات: {str(e)}")
            return False
    
    def safe_calculate(self, func, default=0):
        """تنفيذ آمن للعمليات الحسابية"""
        try:
            result = func()
            return result if pd.notna(result) else default
        except Exception as e:
            print(f"تحذير: {str(e)}")
            return default
    
    def validate_columns(self, required_cols):
        """التحقق من وجود الأعمدة المطلوبة"""
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            print(f"✗ الأعمدة التالية مفقودة: {', '.join(missing)}")
            return False
        return True
    
    # ==================== المجموعة 1: تحليل المبيعات الأساسي ====================
    def group1_basic_sales(self, sales_col='المبيعات', profit_col='الربح', 
                          product_col='المنتج', region_col='المنطقة',
                          category_col='الفئة', customer_col='العميل',
                          date_col='التاريخ'):
        """المجموعة 1: تحليل المبيعات الأساسي (1-10)"""
        
        print("\n" + "="*60)
        print("المجموعة 1: تحليل المبيعات الأساسي")
        print("="*60)
        
        results = {}
        
        # 1. إجمالي المبيعات
        if sales_col in self.df.columns:
            results['إجمالي المبيعات'] = self.safe_calculate(
                lambda: self.df[sales_col].sum()
            )
            print(f"\n1. إجمالي المبيعات: {results['إجمالي المبيعات']:,.2f}")
        
        # 2. إجمالي الأرباح
        if profit_col in self.df.columns:
            results['إجمالي الأرباح'] = self.safe_calculate(
                lambda: self.df[profit_col].sum()
            )
            print(f"2. إجمالي الأرباح: {results['إجمالي الأرباح']:,.2f}")
        
        # 3. أفضل 10 منتجات
        if product_col in self.df.columns and sales_col in self.df.columns:
            top_products = self.df.groupby(product_col)[sales_col].sum().nlargest(10)
            results['أفضل 10 منتجات'] = top_products
            print(f"\n3. أفضل 10 منتجات مبيعاً:")
            print(top_products.to_string())
        
        # 4. أقل 10 منتجات
        if product_col in self.df.columns and sales_col in self.df.columns:
            bottom_products = self.df.groupby(product_col)[sales_col].sum().nsmallest(10)
            results['أقل 10 منتجات'] = bottom_products
            print(f"\n4. أقل 10 منتجات مبيعاً:")
            print(bottom_products.to_string())
        
        # 5. المبيعات حسب المنطقة
        if region_col in self.df.columns and sales_col in self.df.columns:
            sales_by_region = self.df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
            results['المبيعات حسب المنطقة'] = sales_by_region
            print(f"\n5. المبيعات حسب المنطقة:")
            print(sales_by_region.to_string())
        
        # 6. المبيعات حسب الفئة
        if category_col in self.df.columns and sales_col in self.df.columns:
            sales_by_category = self.df.groupby(category_col)[sales_col].sum().sort_values(ascending=False)
            results['المبيعات حسب الفئة'] = sales_by_category
            print(f"\n6. المبيعات حسب الفئة:")
            print(sales_by_category.to_string())
        
        # 7. المبيعات حسب العميل
        if customer_col in self.df.columns and sales_col in self.df.columns:
            sales_by_customer = self.df.groupby(customer_col)[sales_col].sum().nlargest(10)
            results['المبيعات حسب العميل'] = sales_by_customer
            print(f"\n7. أفضل 10 عملاء:")
            print(sales_by_customer.to_string())
        
        # 8. المبيعات حسب الشهر
        if date_col in self.df.columns and sales_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            sales_by_month = self.df.groupby(self.df[date_col].dt.to_period('M'))[sales_col].sum()
            results['المبيعات حسب الشهر'] = sales_by_month
            print(f"\n8. المبيعات حسب الشهر:")
            print(sales_by_month.to_string())
        
        # 9. المبيعات حسب اليوم
        if date_col in self.df.columns and sales_col in self.df.columns:
            sales_by_day = self.df.groupby(self.df[date_col].dt.day_name())[sales_col].sum()
            results['المبيعات حسب اليوم'] = sales_by_day
            print(f"\n9. المبيعات حسب اليوم:")
            print(sales_by_day.to_string())
        
        # 10. المبيعات حسب الربع
        if date_col in self.df.columns and sales_col in self.df.columns:
            sales_by_quarter = self.df.groupby(self.df[date_col].dt.quarter)[sales_col].sum()
            results['المبيعات حسب الربع'] = sales_by_quarter
            print(f"\n10. المبيعات حسب الربع المالي:")
            print(sales_by_quarter.to_string())
        
        return results
    
    # ==================== المجموعة 2: تحليل المبيعات المتقدم ====================
    def group2_advanced_sales(self, sales_col='المبيعات', profit_col='الربح',
                             product_col='المنتج', category_col='الفئة',
                             price_col='السعر', channel_col='القناة',
                             stock_col='المخزون', promo_col='ترويج',
                             date_col='التاريخ'):
        """المجموعة 2: تحليل المبيعات المتقدم (11-20)"""
        
        print("\n" + "="*60)
        print("المجموعة 2: تحليل المبيعات المتقدم")
        print("="*60)
        
        results = {}
        
        # 11. معدل الربح لكل منتج
        if product_col in self.df.columns and profit_col in self.df.columns:
            profit_per_product = self.df.groupby(product_col)[profit_col].mean()
            results['معدل الربح لكل منتج'] = profit_per_product
            print(f"\n11. معدل الربح لكل منتج:")
            print(profit_per_product.nlargest(10).to_string())
        
        # 12. معدل الربح لكل فئة
        if category_col in self.df.columns and profit_col in self.df.columns:
            profit_per_category = self.df.groupby(category_col)[profit_col].mean()
            results['معدل الربح لكل فئة'] = profit_per_category
            print(f"\n12. معدل الربح لكل فئة:")
            print(profit_per_category.to_string())
        
        # 13. متوسط سعر البيع
        if price_col in self.df.columns:
            avg_price = self.df[price_col].mean()
            results['متوسط سعر البيع'] = avg_price
            print(f"\n13. متوسط سعر البيع: {avg_price:,.2f}")
        
        # 14. هامش الربح
        if sales_col in self.df.columns and profit_col in self.df.columns:
            self.df['هامش_الربح'] = (self.df[profit_col] / self.df[sales_col] * 100)
            margin_by_product = self.df.groupby(product_col)['هامش_الربح'].mean()
            results['هامش الربح'] = margin_by_product
            print(f"\n14. هامش الربح لكل منتج:")
            print(margin_by_product.nlargest(10).to_string())
        
        # 15. المبيعات حسب القناة
        if channel_col in self.df.columns and sales_col in self.df.columns:
            sales_by_channel = self.df.groupby(channel_col)[sales_col].sum()
            results['المبيعات حسب القناة'] = sales_by_channel
            print(f"\n15. المبيعات حسب القناة:")
            print(sales_by_channel.to_string())
        
        # 16. المبيعات حسب المخزون
        if stock_col in self.df.columns and sales_col in self.df.columns:
            print(f"\n16. علاقة المبيعات بالمخزون:")
            print(f"معامل الارتباط: {self.df[[stock_col, sales_col]].corr().iloc[0,1]:.2f}")
        
        # 17. المبيعات الموسمية
        if date_col in self.df.columns and sales_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            seasonal_sales = self.df.groupby(self.df[date_col].dt.month)[sales_col].sum()
            results['المبيعات الموسمية'] = seasonal_sales
            print(f"\n17. المبيعات حسب الشهر:")
            print(seasonal_sales.to_string())
        
        # 18. المبيعات حسب الترويج
        if promo_col in self.df.columns and sales_col in self.df.columns:
            sales_by_promo = self.df.groupby(promo_col)[sales_col].sum()
            results['المبيعات حسب الترويج'] = sales_by_promo
            print(f"\n18. المبيعات حسب الترويج:")
            print(sales_by_promo.to_string())
        
        # 19. المبيعات اليومية
        if date_col in self.df.columns and sales_col in self.df.columns:
            daily_sales = self.df.groupby(self.df[date_col].dt.date)[sales_col].sum()
            results['المبيعات اليومية'] = daily_sales
            print(f"\n19. إحصائيات المبيعات اليومية:")
            print(f"متوسط المبيعات اليومية: {daily_sales.mean():,.2f}")
            print(f"أعلى مبيعات يومية: {daily_sales.max():,.2f}")
        
        # 20. المبيعات الأسبوعية
        if date_col in self.df.columns and sales_col in self.df.columns:
            weekly_sales = self.df.groupby(self.df[date_col].dt.isocalendar().week)[sales_col].sum()
            results['المبيعات الأسبوعية'] = weekly_sales
            print(f"\n20. متوسط المبيعات الأسبوعية: {weekly_sales.mean():,.2f}")
        
        return results
    
    # ==================== المجموعة 3: تحليل المخزون الأساسي ====================
    def group3_basic_inventory(self, stock_col='المخزون', product_col='المنتج',
                               category_col='الفئة', warehouse_col='المستودع',
                               sales_col='المبيعات', date_col='التاريخ'):
        """المجموعة 3: تحليل المخزون الأساسي (21-30)"""
        
        print("\n" + "="*60)
        print("المجموعة 3: تحليل المخزون الأساسي")
        print("="*60)
        
        results = {}
        
        # 21. إجمالي المخزون
        if stock_col in self.df.columns:
            total_stock = self.df[stock_col].sum()
            results['إجمالي المخزون'] = total_stock
            print(f"\n21. إجمالي المخزون: {total_stock:,.0f}")
        
        # 22. المخزون حسب المنتج
        if product_col in self.df.columns and stock_col in self.df.columns:
            stock_by_product = self.df.groupby(product_col)[stock_col].sum()
            results['المخزون حسب المنتج'] = stock_by_product
            print(f"\n22. أعلى 10 منتجات في المخزون:")
            print(stock_by_product.nlargest(10).to_string())
        
        # 23. المخزون حسب الفئة
        if category_col in self.df.columns and stock_col in self.df.columns:
            stock_by_category = self.df.groupby(category_col)[stock_col].sum()
            results['المخزون حسب الفئة'] = stock_by_category
            print(f"\n23. المخزون حسب الفئة:")
            print(stock_by_category.to_string())
        
        # 24. المخزون حسب المستودع
        if warehouse_col in self.df.columns and stock_col in self.df.columns:
            stock_by_warehouse = self.df.groupby(warehouse_col)[stock_col].sum()
            results['المخزون حسب المستودع'] = stock_by_warehouse
            print(f"\n24. المخزون حسب المستودع:")
            print(stock_by_warehouse.to_string())
        
        # 25. المنتجات منخفضة المخزون
        if stock_col in self.df.columns and product_col in self.df.columns:
            low_stock = self.df.nsmallest(10, stock_col)[[product_col, stock_col]]
            results['المخزون المنخفض'] = low_stock
            print(f"\n25. المنتجات منخفضة المخزون:")
            print(low_stock.to_string())
        
        # 26. المنتجات عالية المخزون
        if stock_col in self.df.columns and product_col in self.df.columns:
            high_stock = self.df.nlargest(10, stock_col)[[product_col, stock_col]]
            results['المخزون العالي'] = high_stock
            print(f"\n26. المنتجات عالية المخزون:")
            print(high_stock.to_string())
        
        # 27. معدل دوران المخزون
        if sales_col in self.df.columns and stock_col in self.df.columns:
            self.df['معدل_الدوران'] = self.df[sales_col] / (self.df[stock_col] + 1)
            turnover = self.df.groupby(product_col)['معدل_الدوران'].mean()
            results['معدل دوران المخزون'] = turnover
            print(f"\n27. معدل دوران المخزون:")
            print(turnover.nlargest(10).to_string())
        
        # 28. المخزون المتوقع
        if sales_col in self.df.columns and stock_col in self.df.columns:
            avg_sales = self.df.groupby(product_col)[sales_col].mean()
            current_stock = self.df.groupby(product_col)[stock_col].last()
            days_of_stock = current_stock / (avg_sales + 1) * 30
            results['أيام المخزون المتبقية'] = days_of_stock
            print(f"\n28. المنتجات التي تحتاج تعبئة (أقل من 30 يوم):")
            print(days_of_stock[days_of_stock < 30].nsmallest(10).to_string())
        
        # 29. المخزون الأمني
        if sales_col in self.df.columns:
            safety_stock = self.df.groupby(product_col)[sales_col].std() * 1.65
            results['المخزون الأمني'] = safety_stock
            print(f"\n29. المخزون الأمني المطلوب:")
            print(safety_stock.nlargest(10).to_string())
        
        # 30. المنتجات المتقادمة
        if date_col in self.df.columns and sales_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            recent_sales = self.df[self.df[date_col] >= (datetime.now() - timedelta(days=90))]
            products_with_sales = recent_sales[product_col].unique()
            obsolete = self.df[~self.df[product_col].isin(products_with_sales)]
            results['المنتجات المتقادمة'] = len(obsolete)
            print(f"\n30. عدد المنتجات المتقادمة (بدون مبيعات 90 يوم): {len(obsolete)}")
        
        return results
    
    # ==================== المجموعة 5: تحليل الموظفين الأساسي ====================
    def group5_basic_employees(self, dept_col='القسم', role_col='الدور',
                              salary_col='الراتب', date_col='تاريخ_التوظيف',
                              status_col='الحالة', attendance_col='الحضور'):
        """المجموعة 5: تحليل الموظفين الأساسي (41-50)"""
        
        print("\n" + "="*60)
        print("المجموعة 5: تحليل الموظفين الأساسي")
        print("="*60)
        
        results = {}
        
        # 41. عدد الموظفين حسب القسم
        if dept_col in self.df.columns:
            emp_by_dept = self.df[dept_col].value_counts()
            results['الموظفين حسب القسم'] = emp_by_dept
            print(f"\n41. عدد الموظفين حسب القسم:")
            print(emp_by_dept.to_string())
        
        # 42. عدد الموظفين حسب الدور
        if role_col in self.df.columns:
            emp_by_role = self.df[role_col].value_counts()
            results['الموظفين حسب الدور'] = emp_by_role
            print(f"\n42. عدد الموظفين حسب الدور:")
            print(emp_by_role.to_string())
        
        # 43. متوسط الراتب حسب القسم
        if dept_col in self.df.columns and salary_col in self.df.columns:
            avg_salary_dept = self.df.groupby(dept_col)[salary_col].mean()
            results['متوسط الراتب حسب القسم'] = avg_salary_dept
            print(f"\n43. متوسط الراتب حسب القسم:")
            print(avg_salary_dept.to_string())
        
        # 44. متوسط الراتب حسب الدور
        if role_col in self.df.columns and salary_col in self.df.columns:
            avg_salary_role = self.df.groupby(role_col)[salary_col].mean()
            results['متوسط الراتب حسب الدور'] = avg_salary_role
            print(f"\n44. متوسط الراتب حسب الدور:")
            print(avg_salary_role.to_string())
        
        # 45. التوظيف الشهري
        if date_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            hiring_by_month = self.df.groupby(self.df[date_col].dt.to_period('M')).size()
            results['التوظيف الشهري'] = hiring_by_month
            print(f"\n45. التوظيف الشهري:")
            print(hiring_by_month.tail(12).to_string())
        
        # 46. معدل الاستقالات
        if status_col in self.df.columns:
            total_emp = len(self.df)
            resigned = len(self.df[self.df[status_col].str.contains('استقال|resigned', case=False, na=False)])
            turnover_rate = (resigned / total_emp) * 100
            results['معدل الاستقالات'] = turnover_rate
            print(f"\n46. معدل الاستقالات: {turnover_rate:.2f}%")
        
        # 47. تحليل الغياب
        if attendance_col in self.df.columns:
            absence_rate = self.df[attendance_col].value_counts()
            results['معدل الغياب'] = absence_rate
            print(f"\n47. تحليل الحضور والغياب:")
            print(absence_rate.to_string())
        
        # 48. تحليل الحضور
        if attendance_col in self.df.columns:
            attendance_pct = (self.df[attendance_col].sum() / len(self.df)) * 100
            results['نسبة الحضور'] = attendance_pct
            print(f"\n48. نسبة الحضور: {attendance_pct:.2f}%")
        
        # 49. تحليل العمر الوظيفي
        if date_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            self.df['العمر_الوظيفي'] = (datetime.now() - self.df[date_col]).dt.days / 365
            avg_tenure = self.df['العمر_الوظيفي'].mean()
            results['متوسط العمر الوظيفي'] = avg_tenure
            print(f"\n49. متوسط العمر الوظيفي: {avg_tenure:.2f} سنة")
        
        # 50. الموظفين الجدد
        if date_col in self.df.columns:
            new_employees = len(self.df[self.df[date_col] >= (datetime.now() - timedelta(days=90))])
            results['الموظفين الجدد'] = new_employees
            print(f"\n50. عدد الموظفين الجدد (آخر 3 أشهر): {new_employees}")
        
        return results
    
    # ==================== المجموعة 7: تحليل العملاء الأساسي ====================
    def group7_basic_customers(self, customer_col='العميل', date_col='التاريخ',
                              sales_col='المبيعات', region_col='المنطقة',
                              category_col='الفئة', age_col='العمر',
                              gender_col='الجنس', status_col='الحالة'):
        """المجموعة 7: تحليل العملاء الأساسي (61-70)"""
        
        print("\n" + "="*60)
        print("المجموعة 7: تحليل العملاء الأساسي")
        print("="*60)
        
        results = {}
        
        # 61. عدد العملاء الكلي
        if customer_col in self.df.columns:
            total_customers = self.df[customer_col].nunique()
            results['عدد العملاء'] = total_customers
            print(f"\n61. عدد العملاء الكلي: {total_customers:,}")
        
        # 62. العملاء الجدد
        if customer_col in self.df.columns and date_col in self.df.columns:
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
            new_customers = self.df[self.df[date_col] >= (datetime.now() - timedelta(days=30))][customer_col].nunique()
            results['العملاء الجدد'] = new_customers
            print(f"\n62. العملاء الجدد (آخر 30 يوم): {new_customers:,}")
        
        # 63. العملاء النشطين
        if status_col in self.df.columns:
            active_customers = len(self.df[self.df[status_col].str.contains('نشط|active', case=False, na=False)])
            results['العملاء النشطين'] = active_customers
            print(f"\n63. العملاء النشطين:
