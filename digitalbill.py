# my_app.py
import streamlit as st
from fpdf import FPDF
import os


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'testApp "electronic bill"', 0, 1, 'C')
        self.cell(0, 10, '---------------------------------------------------------------', 0, 1, 'C')


    def chapter_title(self, item_num, label, price):
        self.set_font('Arial', '', 12)
        # set width of the cell to half of the page width for name and align center
        self.cell(0.5 * self.w, 10, f"Item {item_num} : {label}", 0, 0, 'C') # 0 at the end to not create a new line
        # set width of the cell to half of the page width for price and align center
        self.cell(0.5 * self.w, 10, f"Price: {price} AED", 0, 1, 'C')  # '1' at the end to create a new line after this cell

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body, 0, 'C')
        self.ln()

    def add_customer_info(self, name, mobile, address, order_date, delivery_date):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, "Customer Information", 0, 1, 'C')


        self.set_font('Arial', '', 12)
        self.cell(0, 10, f"Name: {name}", 0, 1, 'C')
        self.cell(0, 10, f"Mobile Number: {mobile}", 0, 1, 'C')
        self.cell(0, 10, f"Address: {address}", 0, 1, 'C')
        self.cell(0, 10, f"Order Date: {order_date.strftime('%Y-%m-%d')}", 0, 1, 'C')
        self.cell(0, 10, f"Delivery Date: {delivery_date.strftime('%Y-%m-%d')}", 0, 1, 'C')
        self.ln(10)  # Add a little space before item list
        self.cell(0, 10, '---------------------------------------------------------------', 0, 1, 'C')


def create_pdf(item_list, customer_info):
    pdf = PDF()
    pdf.add_page()
    pdf.add_customer_info(*customer_info)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "Order Information", 0, 1, 'C')
    gross_price = 0
    for index, item in enumerate(item_list):
        item_price = 0
        if item["price"] and item.get("count", "1"):
            item_price = float(item["price"]) * int(item.get("count", 1))

        item_str = f"   {index + 1} - {item['name']}          [Price: {item['price']} AED * Count: {item['count']}] =  {item_price:.2f} AED"
        pdf.cell(0, 10, item_str, 0, 1, 'C')
        gross_price += item_price

    discount_amount = (st.session_state.discount_percentage / 100) * gross_price
    final_price = gross_price - discount_amount
    pdf.ln(10)  # Add a little space before item list
    pdf.cell(0, 10, '---------------------------------------------------------------', 0, 1, 'C')
    # Adding Gross price, discount, and final price to the PDF
    pdf.cell(0, 10, f"Gross Price : {gross_price:.2f} AED", 0, 1, 'C')
    pdf.cell(0, 10, f"Discount Amount : ({st.session_state.discount_percentage}%): -{discount_amount:.2f} AED", 0, 1, 'C')
    pdf.cell(0, 10, f"Final Price : {final_price:.2f} AED", 0, 1, 'C')

    filename = "items.pdf"
    pdf.output(name=filename, dest='F').encode('latin1')

    return filename


def main():
    st.title("Electronic Bill")
    customer_name = st.text_input("الأسم")
    mobile_number = st.text_input("رقم الموبايل")
    address = st.text_area("العنوان")
    order_date = st.date_input("تاريخ الطلب")
    delivery_date = st.date_input("تاريخ التوصيل")
    st.write('---')

    # Use session state to store dynamic items
    if "item_list" not in st.session_state:
        st.session_state.item_list = [{"name": "", "price": ""}]

    # Display dynamic text boxes
    for index, item in enumerate(st.session_state.item_list):
        col1, col2 ,col3 = st.columns(3)
        with col1:
            item["name"] = st.text_input(f"المنتج {index + 1}", item["name"], key=f"ItemName{index}")


        with col2:
            item["price"] = st.text_input(f"سعر المنتج {index + 1}", item["price"], key=f"ItemPrice{index}")

        with col3:
            item["count"] = st.text_input(f"العدد {index + 1}", item.get("count", "1"), key=f"ItemCount{index}")

    # Add button to create a new text box
    if st.button("إضافة منتج"):
        # Only add a new item if the last item isn't empty
        
        last_item = st.session_state.item_list[-1]
        if last_item["name"] or last_item["price"]:

            st.session_state.item_list.append({"name": "", "price": "", "count": "1"})

    if "apply_discount_clicked" not in st.session_state:
        st.session_state.apply_discount_clicked = False
    if "discount_percentage" not in st.session_state:
        st.session_state.discount_percentage = 0.0
    if st.session_state.apply_discount_clicked or st.button("تطبيق الخصم"):
        st.session_state.apply_discount_clicked = True
        st.session_state.discount_percentage = st.number_input("نسبة الخصم (%)", min_value=0.0, max_value=100.0,
                                                               value=st.session_state.get("discount_percentage", 0.0))
    # Calculate the total, display it, and generate/download PDF
    if st.button("إنتهاء"):
        gross_price = sum([float(item["price"]) * int(item.get("count", 1)) for item in st.session_state.item_list if
                           item["price"].replace('.', '', 1).isdigit()])
        discount_amount = (st.session_state.discount_percentage / 100) * gross_price
        total_price = gross_price - discount_amount

        st.write(f" {gross_price:.2f} AED : السعر الإجمالي")
        st.write(f"({st.session_state.discount_percentage}%): -{discount_amount:.2f} AED : نسبة الخصم")
        st.write(f"{total_price:.2f} AED : السعر النهائي")

        customer_info = (customer_name, mobile_number, address, order_date, delivery_date)

        filename = create_pdf(st.session_state.item_list, customer_info)
        with open(filename, "rb") as f:
            btn = st.download_button(label="تحميل الفاتورة", data=f, file_name=filename, mime="application/pdf")

        # Cleanup after download
        if not btn:
            os.remove(filename)

hide_st_style ="""
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden; }
        </style>
        """
st.markdown (hide_st_style, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
