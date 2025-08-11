
# Codtech Dashboard - Dash app
# Run: pip install -r requirements.txt
# Then: python app.py
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("codtech_dashboard_dataset_10000.csv", parse_dates=["order_date"])

app = dash.Dash(__name__, title="Codtech - Data Analyst Internship Dashboard")

app.layout = html.Div([
    html.H1("Codtech - Sales Dashboard (Synthetic Dataset)"),
    html.Div([
        html.Div([
            html.Label("Region"),
            dcc.Dropdown(id="region-filter", options=[{"label":r,"value":r} for r in sorted(df["region"].unique())], multi=True, value=[]),
        ], style={"width":"30%","display":"inline-block","padding":"10px"}),
        html.Div([
            html.Label("Category"),
            dcc.Dropdown(id="category-filter", options=[{"label":c,"value":c} for c in sorted(df["category"].unique())], multi=True, value=[]),
        ], style={"width":"30%","display":"inline-block","padding":"10px"}),
        html.Div([
            html.Label("Customer Segment"),
            dcc.Dropdown(id="segment-filter", options=[{"label":s,"value":s} for s in sorted(df["customer_segment"].unique())], multi=True, value=[]),
        ], style={"width":"30%","display":"inline-block","padding":"10px"}),
    ]),
    dcc.Graph(id="timeseries-sales"),
    html.Div([
        html.Div(dcc.Graph(id="sales-by-category"), style={"width":"48%","display":"inline-block"}),
        html.Div(dcc.Graph(id="top-products"), style={"width":"48%","display":"inline-block"})
    ]),
    html.Div([
        html.Div(dcc.Graph(id="sales-by-region"), style={"width":"48%","display":"inline-block"}),
        html.Div(dcc.Graph(id="profit-vs-sales"), style={"width":"48%","display":"inline-block"})
    ]),
    html.H4("Key Metrics"),
    html.Div(id="kpi-area", style={"display":"flex","gap":"20px"})
])

def filter_df(region_vals, category_vals, segment_vals):
    d = df.copy()
    if region_vals:
        d = d[d["region"].isin(region_vals)]
    if category_vals:
        d = d[d["category"].isin(category_vals)]
    if segment_vals:
        d = d[d["customer_segment"].isin(segment_vals)]
    return d

@app.callback(
    Output("timeseries-sales","figure"),
    Output("sales-by-category","figure"),
    Output("top-products","figure"),
    Output("sales-by-region","figure"),
    Output("profit-vs-sales","figure"),
    Output("kpi-area","children"),
    Input("region-filter","value"),
    Input("category-filter","value"),
    Input("segment-filter","value"),
)
def update_charts(region_vals, category_vals, segment_vals):
    d = filter_df(region_vals, category_vals, segment_vals)
    timeseries = d.groupby(pd.Grouper(key="order_date", freq="M")).agg({"sales":"sum"}).reset_index()
    fig_time = px.line(timeseries, x="order_date", y="sales", title="Monthly Sales (Filtered)")
    cat = d.groupby("category").agg({"sales":"sum"}).reset_index().sort_values("sales", ascending=False)
    fig_cat = px.bar(cat, x="category", y="sales", title="Sales by Category")
    prod = d.groupby("product").agg({"sales":"sum"}).reset_index().sort_values("sales", ascending=False).head(10)
    fig_prod = px.pie(prod, values="sales", names="product", title="Top 10 Products (by Sales)")
    region = d.groupby("region").agg({"sales":"sum"}).reset_index().sort_values("sales", ascending=False)
    fig_reg = px.bar(region, x="region", y="sales", title="Sales by Region")
    fig_scatter = px.scatter(d, x="sales", y="profit", color="category", hover_data=["product","city"], title="Profit vs Sales (each order)")
    # KPIs
    total_sales = f"Total sales: ₹{d['sales'].sum():,.0f}"
    avg_order = f"Avg order value: ₹{d['sales'].mean():,.0f}"
    total_profit = f"Total profit: ₹{d['profit'].sum():,.0f}"
    kpis = [html.Div(html.H3(total_sales)), html.Div(html.H3(avg_order)), html.Div(html.H3(total_profit))]
    return fig_time, fig_cat, fig_prod, fig_reg, fig_scatter, kpis

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
