import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import plotly.graph_objs as go

# Load the main_data.csv file using pandas
df = pd.read_csv('https://raw.githubusercontent.com/FransiscoReadyPermana/E-commerce-public-dicoding/main/Dashboard/main_data.csv?token=GHSAT0AAAAAACGFXXOZOANY7NHHAZQZTUBEZJBIS4A', parse_dates=['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'])
min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max()

# Create a Streamlit app
st.markdown('''
# E-Commerce Public
''')

option = df['customer_city'].unique()
option = np.insert(option, 0, 'Semua Kota')

col1, col2 = st.columns(2)
with col1:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
with col2:
    city = st.selectbox('Pilih Kota', option, index=0)

if city != 'Semua Kota':
    df = df[df['customer_city'] == city]

df = df[(df["order_purchase_timestamp"] >= str(start_date)) & 
                (df["order_purchase_timestamp"] <= str(end_date))]



unique_order = len(df['order_id'].unique())
unique_customer = len(df['customer_id'].unique())
unique_product = len(df['product_id'].unique())
total_revenue = df['price'].sum()


# Add a checkbox to the app
if st.checkbox('Show dataframe'):
    st.write(df)

    with st.expander('See the data description'):
        st.write(f'''
        Dataset ini terdiri dari 100.000 pesanan dari tahun 2016 hingga 2018 yang dibuat di berbagai marketplace di Brasil. setelah saya olah, didapatkan beberapa informasi sebagai berikut:
        - Terdapat {unique_order} total pesanan
        - Terdapat {unique_customer} total pelanggan
        - Terdapat {unique_product} total produk
        - Rata-rata waktu untuk menyelesaikan satu pesanan adalah {time_to_solve} jam
        - Pendapatan yang dihasilkan adalah {total_revenue} R$
        ''')

# add columns to the app
col1, col2, col3 = st.columns(3)

# Menambahkan elemen ke kolom pertama
with col1:
    st.markdown(f'''
    ## {unique_order}
    ### Total Orders
    ''')
    
# Menambahkan elemen ke kolom kedua
with col2:
    st.markdown(f'''
    ## {unique_customer}
    ### Total Customers
    ''')

with col3:
    st.markdown(f'''
    ## {unique_product}
    ### Unique Products
    ''')

st.title('')

st.markdown('''# Trend Order Bulanan''')
# menampilkan plot dari plotly
lima = df.copy()
lima.set_index('order_purchase_timestamp', inplace=True)


# Meresample data ke bulanan dan menghitung jumlah pesanan
monthly_orders = lima.resample('m').size().reset_index()
monthly_orders.columns = ['Month', 'Number of Orders']

# Membuat plot interaktif dengan Plotly Express
figTrend = px.scatter(monthly_orders, x='Month', y='Number of Orders', labels={'Month': 'Month', 'Number of Orders': 'Number of Orders'}, height=400, color_discrete_sequence=['#f63366'])

# Menambahkan mode hover untuk menampilkan detail saat dihover
figTrend.update_traces(mode='lines+markers', marker=dict(size=8), hovertemplate='Month: %{x}<br>Number of Orders: %{y}', line=dict(color='#f63366', width=2.5), name='')

# Menyesuaikan tampilan plot
figTrend.update_layout(xaxis_title='Month', yaxis_title='Number of Orders', xaxis=dict(tickangle=45))

st.plotly_chart(figTrend)

# Mengelompokkan data
category_stats = lima.groupby(['product_category_name_english']).agg(
    avg_price=('price', 'mean'),
    count=('product_category_name_english', 'size')
).reset_index()

category_stats['revenue'] = np.floor(category_stats['avg_price'] * category_stats['count'])

# Mengurutkan dan mengambil 10 kategori teratas berdasarkan 'count'
top_5_categories = category_stats.sort_values(by='count', ascending=True).tail(5)

top_5_categories_revenue = category_stats.sort_values(by='revenue', ascending=True).tail(5)

# Membuat plot bar dengan Plotly Express
figCount = px.bar(
    top_5_categories,
    x='count',
    y='product_category_name_english',
    text='count',
    title='Top 5 Product Categories by Count',
    labels={'count': 'Count', 'product_category_name_english': 'Product Category'},
    orientation='h',  
    color_discrete_sequence=['#f63366'], 
)

# Membuat plot bar dengan Plotly Express
figRevenue = px.bar(
    top_5_categories_revenue,
    x='revenue',
    y='product_category_name_english',
    text='revenue',
    title='Top 5 Product Categories by revenue',
    labels={'revenue': 'revenue', 'product_category_name_english': ' '},
    orientation='h',  
    color_discrete_sequence=['#f63366'], 
    width=350,
)

# Mengaktifkan fungsi hover
figRevenue.update_traces(texttemplate='%{text}', textposition='outside')
figCount.update_traces(texttemplate='%{text}', textposition='outside')

rating = df.copy()
rating['ratingInt'] = rating['review_score'].astype(int)
rating = rating.groupby('product_category_name_english').agg(
    avg_rating=('ratingInt', 'mean'),
    count=('product_category_name_english', 'size')
).reset_index().sort_values(by='avg_rating', ascending=True).tail()

rating['ratingInt'] = rating['avg_rating'].apply(lambda x: round(x, 3))

figRating = px.bar(
    rating,
    x='avg_rating',
    y='product_category_name_english',
    text='avg_rating',
    title='Average Rating by Category',
    labels={'avg_rating': 'Average Rating', 'product_category_name_english': 'Product Category'},
    orientation='h',  
    color_discrete_sequence=['#f63366'], 
    range_x=[3.5, 5],
    width=350,
)


st.plotly_chart(figCount)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(figRating)
    
with col2:  
    st.plotly_chart(figRevenue)