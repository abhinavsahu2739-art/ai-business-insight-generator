import streamlit as st
import pandas as pd
import plotly.express as px

from ai_insights import generate_ai_insight

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Business Insight Generator",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/SampleSuperstore_clean.csv")

df = load_data()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📌 Dashboard Filters")

regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

segments = st.sidebar.multiselect(
    "Segment",
    options=sorted(df["Segment"].unique()),
    default=sorted(df["Segment"].unique())
)

# Apply Filters
df_filtered = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Segment"].isin(segments))
]

# =====================================================
# HEADER
# =====================================================

st.title("📊 AI Business Insight Generator")

st.markdown(
"""
Transform raw sales data into **interactive dashboards**
and **AI-powered business insights**.
"""
)

st.divider()

# =====================================================
# KPI CARDS
# =====================================================

total_sales = df_filtered["Sales"].sum()
total_profit = df_filtered["Profit"].sum()
total_orders = len(df_filtered)
avg_sales = df_filtered["Sales"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"${total_sales:,.2f}")
col2.metric("📈 Total Profit", f"${total_profit:,.2f}")
col3.metric("🛒 Total Orders", f"{total_orders:,}")
col4.metric("💵 Avg Sales", f"${avg_sales:,.2f}")

st.markdown("---")
st.header("📈 Business Health Score")

score = 100

profit_margin = (
    df_filtered["Profit"].sum()
    / df_filtered["Sales"].sum()
) * 100

if profit_margin < 5:
    score -= 30
elif profit_margin < 10:
    score -= 15

avg_discount = df_filtered["Discount"].mean()

if avg_discount > 0.25:
    score -= 20
    
    
loss_orders = len(df_filtered[df_filtered["Profit"] < 0])

loss_percent = (
    loss_orders /
    len(df_filtered)
) * 100

if loss_percent > 20:
    score -= 20
    
score = max(score, 0)

col1, col2 = st.columns([1,3])
with col1:

    st.metric(
        "Health Score",
        f"{score}/100"
    )

with col2:
    st.metric("📊 Business Health Score", f"{score}%", delta=f"{profit_margin:.2f}%")
    
if score >= 90:
    st.success("🟢 Excellent Business Health")

elif score >= 75:
    st.info("🔵 Healthy Business")

elif score >= 60:
    st.warning("🟡 Needs Improvement")

else:
    st.error("🔴 Critical Attention Required")

st.divider()

# =====================================================
# CHARTS
# =====================================================

left, right = st.columns(2)

# ----------------------------
# Sales by Category
# ----------------------------

sales_category = (
    df_filtered
    .groupby("Category", as_index=False)["Sales"]
    .sum()
)

fig_sales = px.bar(
    sales_category,
    x="Category",
    y="Sales",
    color="Category",
    text_auto=".2s",
    title="Sales by Category"
)

left.plotly_chart(fig_sales, use_container_width=True)

# ----------------------------
# Profit by Category
# ----------------------------

profit_category = (
    df_filtered
    .groupby("Category", as_index=False)["Profit"]
    .sum()
)

fig_profit = px.bar(
    profit_category,
    x="Category",
    y="Profit",
    color="Category",
    text_auto=".2s",
    title="Profit by Category"
)

right.plotly_chart(fig_profit, use_container_width=True)

# =====================================================
# SALES BY REGION
# =====================================================

sales_region = (
    df_filtered
    .groupby("Region", as_index=False)["Sales"]
    .sum()
)

fig_region = px.pie(
    sales_region,
    names="Region",
    values="Sales",
    hole=0.45,
    title="Sales by Region"
)

st.plotly_chart(fig_region, use_container_width=True)

# =====================================================
# TOP 10 STATES
# =====================================================

top_states = (
    df_filtered
    .groupby("State", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
    .head(10)
)

fig_states = px.bar(
    top_states,
    x="Sales",
    y="State",
    orientation="h",
    color="Sales",
    title="Top 10 States by Sales"
)

fig_states.update_layout(yaxis=dict(categoryorder="total ascending"))

st.plotly_chart(fig_states, use_container_width=True)

top_sub_sales = (
    df_filtered.groupby("Sub-Category")["Sales"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
      .reset_index()
)

fig_sub_sales = px.bar(
    top_sub_sales,
    x="Sales",
    y="Sub-Category",
    orientation="h",
    color="Sales",
    color_continuous_scale="Blues",
    text_auto=".2s",
    title="Top 10 Sub-Categories by Sales"
)

fig_sub_sales.update_layout(
    template="plotly_dark",
    yaxis=dict(categoryorder="total ascending"),
    coloraxis_showscale=False
)

col1.plotly_chart(
    fig_sub_sales,
    use_container_width=True,
    config={"displayModeBar": False}
)

top_sub_profit = (
    df_filtered.groupby("Sub-Category")["Profit"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
      .reset_index()
)

fig_sub_profit = px.bar(
    top_sub_profit,
    x="Profit",
    y="Sub-Category",
    orientation="h",
    color="Profit",
    color_continuous_scale="Greens",
    text_auto=".2s",
    title="Top 10 Sub-Categories by Profit"
)

fig_sub_profit.update_layout(
    template="plotly_dark",
    yaxis=dict(categoryorder="total ascending"),
    coloraxis_showscale=False
)

col2.plotly_chart(
    fig_sub_profit,
    use_container_width=True,
    config={"displayModeBar": False}
)

# =====================================================
# PROFIT ANALYSIS
# =====================================================

st.markdown("---")
st.header("💰 Profit Analysis")

col1, col2 = st.columns([1.2, 1.2])

with col1:
    state_profit = (
        df_filtered.groupby("State")["Profit"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        state_profit,
        x="Profit",
        y="State",
        orientation="h",
        color="Profit",
        color_continuous_scale="Greens",
        text_auto=".2s",
        title="Top 10 States by Profit"
    )

    fig.update_layout(yaxis=dict(categoryorder="total ascending"))

    st.plotly_chart(fig, use_container_width=True)

with col2:
    loss_states = (
        df_filtered.groupby("State")["Profit"]
        .sum()
        .sort_values()
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        loss_states,
        x="Profit",
        y="State",
        orientation="h",
        color="Profit",
        color_continuous_scale="Reds",
        text_auto=".2s",
        title="Bottom 10 States by Profit"
    )

    st.plotly_chart(fig, use_container_width=True)

st.subheader("Profit vs Sales")

fig = px.scatter(
    df_filtered,
    x="Sales",
    y="Profit",
    color="Category",
    size="Quantity",
    hover_name="Sub-Category",
    hover_data=["Region", "Segment","Discount"],
    title="Relationship between Sales and Profit",
    template="plotly_dark"
)
st.markdown("---")
st.header("📦 Sub-Category Analysis")

col1, col2 = st.columns([1.2, 1.2])

st.plotly_chart(fig, use_container_width=True)

st.subheader("Profit Distribution")

fig = px.histogram(
    df_filtered,
    x="Profit",
    nbins=50,
    color_discrete_sequence=["green"]
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("🎯 Discount vs Profit Analysis")


fig_discount = px.scatter(
    df_filtered,
    x="Discount",
    y="Profit",
    size="Sales",
    color="Category",
    hover_name="Sub-Category",
    hover_data=[
        "State",
        "Region",
        "Quantity",
        "Sales"
    ],
    title="Relationship between Discount and Profit",
    template="plotly_dark"
)

fig_discount.add_hline(
    y=0,
    line_dash="dash",
    line_color="red",
    annotation_text="Break-even"
)

fig_discount.update_traces(
    opacity=0.7
)

fig_discount.update_layout(
    height=600,
    xaxis_title="Discount",
    yaxis_title="Profit",
    legend_title="Category"
)

st.plotly_chart(
    fig_discount,
    use_container_width=True,
    config={"displayModeBar": False}
)
st.info("""
### 📌 Business Insights

• Higher discounts are generally associated with lower profits.

• Several highly discounted orders resulted in negative profits.

• Technology products remain profitable even with moderate discounts.

• Furniture contains many loss-making transactions at higher discount levels.

• Reducing unnecessary discounts could significantly improve overall profitability.
""")

# =====================================================
# DATA PREVIEW
# =====================================================

with st.expander("📄 View Dataset"):
    st.dataframe(df_filtered)
    
st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=df_filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_business_data.csv",
    mime="text/csv",
)
    
    
# ==========================================
# 🤖 AI BUSINESS INSIGHTS
# ==========================================

st.markdown("---")
st.header("🤖 AI Business Insights")

# Highest Sales Category
top_category = (
    df_filtered.groupby("Category")["Sales"]
      .sum()
      .idxmax()
)

# Highest Profit Category
top_profit_category = (
    df_filtered.groupby("Category")["Profit"]
      .sum()
      .idxmax()
)

# Best Region
best_region = (
    df_filtered.groupby("Region")["Sales"]
      .sum()
      .idxmax()
)

# Lowest Profit Region
worst_region = (
    df_filtered.groupby("Region")["Profit"]
      .sum()
      .idxmin()
)

# Most Profitable State
best_state = (
    df_filtered.groupby("State")["Profit"]
      .sum()
      .idxmax()
)

# Highest Selling Sub-Category
best_subcategory = (
    df_filtered.groupby("Sub-Category")["Sales"]
      .sum()
      .idxmax()
)

# Most Discounted Category
discount_category = (
    df_filtered.groupby("Category")["Discount"]
      .mean()
      .idxmax()
)

# Highest Average Order Value Category
avg_order_category = (
    df_filtered.groupby("Category")["Sales"]
      .mean()
      .idxmax()
)

st.success(f"✅ **{top_category}** generates the highest total sales.")

st.success(f"💰 **{top_profit_category}** contributes the highest overall profit.")

st.info(f"🌍 **{best_region}** is the strongest sales region.")

st.warning(f"⚠ **{worst_region}** has the lowest overall profit.")

st.success(f"🏆 **{best_state}** is the most profitable state.")

st.info(f"📦 **{best_subcategory}** is the highest-selling sub-category.")

st.warning(f"🏷 **{discount_category}** receives the highest average discount.")

st.info(f"🛒 **{avg_order_category}** has the highest average order value.")


# ==========================================
# 🧠 AI RECOMMENDATION ENGINE
# ==========================================

st.markdown("---")
st.header("🧠 AI Recommendations")

recommendations = []

# ----------------------------------------
# 1. High Discount Warning
# ----------------------------------------

avg_discount = df_filtered["Discount"].mean()

if avg_discount > 0.20:
    recommendations.append(
        f"⚠ The average discount is **{avg_discount:.0%}**. Consider reducing discounts to improve profitability."
    )

# ----------------------------------------
# 2. Loss Making Category
# ----------------------------------------

category_profit = df_filtered.groupby("Category")["Profit"].sum()

if (category_profit < 0).any():
    loss_category = category_profit.idxmin()

    recommendations.append(
        f"📉 **{loss_category}** is generating an overall loss. Review pricing and operational costs."
    )

# ----------------------------------------
# 3. Best Selling Category
# ----------------------------------------

best_sales_category = (
    df_filtered.groupby("Category")["Sales"]
      .sum()
      .idxmax()
)
if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

recommendations.append(
    f"🚀 Increase inventory and marketing for **{best_sales_category}**, as it generates the highest sales."
)

# ----------------------------------------
# 4. Most Profitable State
# ----------------------------------------

best_state = (
    df.groupby("State")["Profit"]
      .sum()
      .idxmax()
)

recommendations.append(
    f"🏆 Expand operations in **{best_state}**, the most profitable state."
)

# ----------------------------------------
# 5. Worst Profit State
# ----------------------------------------

worst_state = (
    df_filtered.groupby("State")["Profit"]
      .sum()
      .idxmin()
)

recommendations.append(
    f"🔍 Investigate **{worst_state}**, which records the lowest overall profit."
)

# ----------------------------------------
# 6. Highest Profit Category
# ----------------------------------------

best_profit_category = (
    df_filtered.groupby("Category")["Profit"]
      .sum()
      .idxmax()
)

recommendations.append(
    f"💰 Focus more on **{best_profit_category}** products to maximize profits."
)

# ----------------------------------------
# Show Recommendations
# ----------------------------------------

for rec in recommendations:
    st.info(rec)
    
    
    
    
profit_margin = (df_filtered["Profit"].sum() / df_filtered["Sales"].sum()) * 100      
        
summary = f"""
Business Summary

Total Sales: ${df_filtered["Sales"].sum():,.2f}
Total Profit: ${df_filtered["Profit"].sum():,.2f}
Total Orders: {len(df_filtered)}
Profit Margin: {profit_margin:.2f}%
Average Sales: ${df_filtered["Sales"].mean():,.2f}

Top Category:
{df_filtered.groupby("Category")["Sales"].sum().idxmax()}

Highest Profit Category:
{df_filtered.groupby("Category")["Profit"].sum().idxmax()}

Most Profitable State:
{df_filtered.groupby("State")["Profit"].sum().idxmax()}

Best Region:
{df_filtered.groupby("Region")["Sales"].sum().idxmax()}

Worst Region:
{df_filtered.groupby("Region")["Profit"].sum().idxmin()}


Worst State:
{df_filtered.groupby("State")["Profit"].sum().idxmin()}

Highest Selling Sub-Category:
{df_filtered.groupby("Sub-Category")["Sales"].sum().idxmax()}

Highest Profit Sub-Category:
{df_filtered.groupby("Sub-Category")["Profit"].sum().idxmax()}

Average Discount:
{df_filtered["Discount"].mean():.2%}

"""
def create_pdf(report_text):

    if report_text is None:
        report_text = "No AI report available."

    styles = getSampleStyleSheet()

    pdf = SimpleDocTemplate("AI_Business_Report.pdf")

    story = []

    for line in str(report_text).split("\n"):

        if line.strip():
            story.append(
                Paragraph(line, styles["BodyText"])
            )

    pdf.build(story)

    return "AI_Business_Report.pdf"

# =====================================================
# 🤖 AI BUSINESS ASSISTANT
# =====================================================

st.markdown("---")
st.header("🤖 AI Business Assistant")

st.caption("Ask questions about your business and receive AI-powered insights.")

# --------------------------
# Quick Questions
# --------------------------

st.write("### ⚡ Quick Questions")

c1, c2, c3 = st.columns(3)

if "question" not in st.session_state:
    st.session_state.question = ""

with c1:
    if st.button("📈 Increase Sales"):
        st.session_state.question = "How can I increase sales?"

with c2:
    if st.button("💰 Improve Profit"):
        st.session_state.question = "Why is my profit low?"

with c3:
    if st.button("🚀 Growth Strategy"):
        st.session_state.question = "Suggest a business growth strategy."

if st.button("🗑 Clear Chat"):

    st.session_state.chat_history = []

    st.rerun()

# --------------------------
# Question Box
# --------------------------

question = st.text_area(
    "Ask your business question",
    value=st.session_state.question,
    placeholder="Example:\n\nWhy is my profit low?\nWhich category should I invest in?\nSuggest marketing strategies.",
    height=140
)

# --------------------------
# Ask Button
# --------------------------

if st.button("🚀 Analyze Business"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:

        with st.spinner("🤖 Gemini is analyzing..."):
            answer = generate_ai_insight(question, summary)

        # Save conversation
        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer
            }
        )

        # Save latest answer for PDF
        st.session_state.latest_answer = answer
        
if "latest_answer" in st.session_state:

    pdf_file = create_pdf(st.session_state.latest_answer)

    with open(pdf_file, "rb") as file:

        st.download_button(
            "📄 Download PDF Report",
            data=file,
            file_name="AI_Business_Report.pdf",
            mime="application/pdf"
        )
        
            
st.header("🤖 AI Business Assistant")

# Store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
# -----------------------------------
# Chat History
# -----------------------------------
st.markdown("---")
st.subheader("📈 Executive Dashboard")

if st.session_state.chat_history:

    st.markdown("---")
    st.subheader("💬 Conversation")

    for chat in reversed(st.session_state.chat_history):

        with st.chat_message("user"):
            st.markdown(chat["question"])

        with st.chat_message("assistant"):
            st.success("📋 AI Executive Report")

            st.markdown(chat["answer"])
            
            if "latest_answer" in st.session_state and chat["answer"] == st.session_state.latest_answer:
                pdf_file = create_pdf(chat["answer"])

                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=file,
                        file_name="AI_Business_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )