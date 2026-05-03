import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from app.queries import (
    get_transactions,
    get_summary,
    get_category_totals,
    get_monthly_totals,
    get_categories,
    export_csv,
)

st.set_page_config(page_title="Expense Tracker", layout="wide", page_icon="💰")

def format_currency(value):
    return f"${value:,.2f}"

def main():
    st.title("💰 Expense Tracker")
    
    summary = get_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Income", format_currency(summary["total_income"]))
    with col2:
        st.metric("Total Expense", format_currency(summary["total_expense"]))
    with col3:
        st.metric("Balance", format_currency(summary["balance"]))
    with col4:
        month_net = summary["month_income"] - summary["month_expense"]
        st.metric("This Month Net", format_currency(month_net))
    
    st.divider()
    
    tabs = st.tabs(["📊 Dashboard", "📈 Trends", "📁 Categories", "📋 Transactions", "📥 Export"])
    
    with tabs[0]:
        st.header("Dashboard")
        
        category_totals = get_category_totals()
        
        if category_totals:
            df_cat = pd.DataFrame(category_totals)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Expenses by Category")
                expense_df = df_cat[df_cat["transaction_type"] == "expense"]
                if not expense_df.empty:
                    fig_pie = px.pie(
                        expense_df, 
                        values="total", 
                        names="category",
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("Income by Category")
                income_df = df_cat[df_cat["transaction_type"] == "income"]
                if not income_df.empty:
                    fig_pie_inc = px.pie(
                        income_df, 
                        values="total", 
                        names="category",
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_pie_inc, use_container_width=True)
        else:
            st.info("No transactions yet. Add some via Discord!")
    
    with tabs[1]:
        st.header("Trends")
        
        monthly_data = get_monthly_totals()
        
        if monthly_data:
            df_monthly = pd.DataFrame(monthly_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Monthly Income vs Expense")
                fig_line = px.line(
                    df_monthly,
                    x="month",
                    y="total",
                    color="transaction_type",
                    markers=True,
                    color_discrete_map={"income": "#2ecc71", "expense": "#e74c3c"}
                )
                fig_line.update_layout(yaxis_title="Amount ($)")
                st.plotly_chart(fig_line, use_container_width=True)
            
            with col2:
                st.subheader("Net Savings Over Time")
                df_pivot = df_monthly.pivot(index="month", columns="transaction_type", values="total").fillna(0)
                df_pivot["net"] = df_pivot.get("income", 0) - df_pivot.get("expense", 0)
                
                fig_bar = go.Figure(go.Bar(
                    x=df_pivot.index,
                    y=df_pivot["net"],
                    marker_color=["#2ecc71" if v >= 0 else "#e74c3c" for v in df_pivot["net"]]
                ))
                fig_bar.update_layout(yaxis_title="Net Savings ($)", xaxis_title="Month")
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.subheader("Expenses Trend by Category")
            transactions = get_transactions(limit=1000)
            if transactions:
                df = pd.DataFrame(transactions)
                df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
                
                expense_df = df[df["transaction_type"] == "expense"]
                if not expense_df.empty:
                    cat_trend = expense_df.groupby(["month", "category"])["amount"].sum().reset_index()
                    fig_area = px.area(
                        cat_trend,
                        x="month",
                        y="amount",
                        color="category",
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    fig_area.update_layout(yaxis_title="Amount ($)")
                    st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("No transactions yet to show trends.")
    
    with tabs[2]:
        st.header("Categories Breakdown")
        
        category_totals = get_category_totals()
        
        if category_totals:
            df = pd.DataFrame(category_totals)
            
            expense_df = df[df["transaction_type"] == "expense"].sort_values("total", ascending=False)
            income_df = df[df["transaction_type"] == "income"].sort_values("total", ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top Expense Categories")
                if not expense_df.empty:
                    fig_bar = px.bar(
                        expense_df,
                        x="total",
                        y="category",
                        orientation="h",
                        color="total",
                        color_continuous_scale="Reds"
                    )
                    fig_bar.update_layout(xaxis_title="Amount ($)")
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.subheader("Top Income Categories")
                if not income_df.empty:
                    fig_bar_inc = px.bar(
                        income_df,
                        x="total",
                        y="category",
                        orientation="h",
                        color="total",
                        color_continuous_scale="Greens"
                    )
                    fig_bar_inc.update_layout(xaxis_title="Amount ($)")
                    st.plotly_chart(fig_bar_inc, use_container_width=True)
            
            st.subheader("Category Comparison")
            expense_by_cat = df[df["transaction_type"] == "expense"][["category", "total"]].rename(columns={"total": "expense"})
            income_by_cat = df[df["transaction_type"] == "income"][["category", "total"]].rename(columns={"total": "income"})
            
            if not income_by_cat.empty:
                merged = expense_by_cat.merge(income_by_cat, on="category", how="outer").fillna(0)
                merged["net"] = merged["income"] - merged["expense"]
                merged = merged.sort_values("net")
                
                fig_comp = go.Figure(go.Bar(
                    x=merged["net"],
                    y=merged["category"],
                    orientation="h",
                    marker=dict(color=["#2ecc71" if v >= 0 else "#e74c3c" for v in merged["net"]])
                ))
                fig_comp.update_layout(xaxis_title="Net (Income - Expense)")
                st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No transactions yet.")
    
    with tabs[3]:
        st.header("Transactions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        categories = ["All"] + get_categories()
        
        with col1:
            filter_type = st.selectbox("Type", ["All", "expense", "income"])
        with col2:
            filter_category = st.selectbox("Category", categories)
        with col3:
            filter_search = st.text_input("Search", "")
        with col4:
            filter_limit = st.selectbox("Limit", [50, 100, 200, 500], index=1)
        
        filters = {}
        if filter_type != "All":
            filters["transaction_type"] = filter_type
        if filter_category != "All":
            filters["category"] = filter_category
        if filter_search:
            filters["search"] = filter_search
        
        transactions = get_transactions(filters=filters, limit=filter_limit)
        
        if transactions:
            df = pd.DataFrame(transactions)
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df["amount"] = df["amount"].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "date": st.column_config.TextColumn("Date"),
                    "transaction_type": st.column_config.TextColumn("Type"),
                    "category": st.column_config.TextColumn("Category"),
                    "description": st.column_config.TextColumn("Description"),
                    "amount": st.column_config.TextColumn("Amount"),
                }
            )
            
            st.caption(f"Showing {len(transactions)} transactions")
        else:
            st.info("No transactions match filters.")
    
    with tabs[4]:
        st.header("Export Data")
        
        csv_data = export_csv()
        
        if csv_data:
            st.success(f"Export ready: {len(csv_data.splitlines())} rows")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            with col2:
                st.code(csv_data[:500] + "...", language="csv")
        else:
            st.info("No data to export.")

if __name__ == "__main__":
    main()