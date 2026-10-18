from dash import Dash, html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from fontTools.cffLib import width
from plotly.graph_objs.layout import title

months = [f"2026-{str(i).zfill(2)}" for i in
          range(1, 7)]  # ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06']
departments = ["IT", "Маркетинг", "Продажи", "HR"]

data = []
for month in months:
    for dept in departments:
        num_employees = np.random.randint(10, 30)
        for i in range(num_employees):
            data.append({
                "Месяц": month,
                "Департамент": dept,
                "Продуктивность": np.random.randint(50, 100),
                "Часы_работы": np.random.randint(120, 180),
                "Удовлетворенность": np.random.uniform(1.0, 5.0),
            })

df = pd.DataFrame(data)

app = Dash()

app.layout = html.Div(
    style={
        "font-family": "Arial, sans-serif",
        "background-color": "#f8f9fa",
        "padding": "30px"
    },
    children=[
        html.H1("Интерактивная панель аналитики (2026)", style={"textAlign": "center", "color": "#FF0000"}),
        html.Div(
            style={
                "background-color": "white",
                "borderRadius": "10px",
                "padding": "20px",
                "boxShadow": "0 4px 6px rgba(0,0,0,0.08)",
                "display": "flex",
                "justifyContent": "space-around",
                "alignItems": "center",
                "marginBottom": "25px",
            },
            children=[
                html.Div(
                    style={"width": "45%"},
                    children=[
                        html.Label("Выберите Департамент:"),
                        dcc.Tabs(
                            id="dept-tabs",
                            value="All",
                            children=[
                                         dcc.Tab(
                                             label="Все отделы",
                                             value="All",
                                             style={"padding": "10px"},
                                         )
                                     ]
                                     + [
                                         dcc.Tab(
                                             label=dept,
                                             value=dept,
                                             style={"padding": "10px"},
                                         )
                                         for dept in departments
                                     ]
                        )
                    ]),
                html.Div(
                    style={"width": "45%"},
                    children=[
                        html.Label(
                            "Временной диапазон",
                            style={
                                "fontWeight": "bold",
                                "color": "#34495e",
                                "marginBottom": "15px",
                                "display": "block",
                            }
                        ),
                        dcc.RangeSlider(
                            id="month-slider",
                            min=0,
                            max=len(months) - 1,
                            value=[0, len(months) - 1],
                            marks={i: month for i, month in enumerate(months)},
                            step=None,
                        )
                    ]
                )
            ]),
        html.Div(
            id="kpi-cards-container",
            style={
                "display": "flex",
                "justify-content": "space-between",
                "marginBottom": "25px",
            }
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[
                html.Div(
                    children=[dcc.Graph(id="scatter-chart")]
                ),
                html.Div(
                    children=[dcc.Graph(id="heatmap-chart")]
                )
            ]
        )
    ])


def create_kpi_card(title, value, color):
    return html.Div(
        style={
            "width": "30%",
            "backgroundColor": "width",
            "padding": "20px",
            "borderRadius": "10px",
            "boxShadow": "0 4px 6px rgba(0,0,0,0.08)",
            "borderLeft": f"5px solid {color}",
            "textAlign": "center",
        },
        children=[
            html.H3(title, style={"margin": "0 0 10px 0", "color": "#7f8c8d", "fontSize": "16px"}),
            html.H2(value, style={"margin": "0", "color": "#2c3e50", "fontSize": "28px"}),
        ]
    )


@app.callback(
    [
        Output("kpi-cards-container", "children"),
        Output("scatter-chart", "figure"),
        Output("heatmap-chart", "figure"),
    ],
    [Input("dept-tabs", "value"), Input("month-slider", "value")],
)
def update_metrics(selected_dept, selected_month_idx):
    selected_month = months[selected_month_idx[0]:selected_month_idx[1] + 1]
    filtered_df = df[df["Месяц"].isin(selected_month)]

    if selected_dept != "All":
        filtered_df = filtered_df[filtered_df["Департамент"] == selected_dept]
    avg_prod = f"{filtered_df['Продуктивность'].mean():.1f}%"
    total_hours = f"{filtered_df['Часы_работы'].sum():,}"
    avg_sat = f"{filtered_df['Удовлетворенность'].mean():.2f} / 5.0"

    kpis = [
        create_kpi_card("Ср. Продуктивность", avg_prod, color="#2ecc71"),
        create_kpi_card("Всего отработанных часов", total_hours, color="#3498db"),
        create_kpi_card("Уровень удовлетворенности", avg_sat, color="#e67e22"),
    ]

    fig_scatter = px.scatter(
        filtered_df,
        x="Часы_работы",
        y="Продуктивность",
        color="Департамент" if selected_dept == "All" else None,
        size="Удовлетворенность",
        hover_data=["Месяц"],
        title="Связь выроботки часов и продуктивности сотрудников",
        labels={
            "Часы_работы": "Отработанные часы",
            "Продуктивность": "Эффективность (%)"
        },
        color_discrete_sequence=px.colors.qualitative.Safe,
    )

    pivot_df = (
        filtered_df.groupby(["Департамент", "Месяц"])["Продуктивность"].mean().reset_index()
    )

    fig_heatmap = px.density_heatmap(
        pivot_df,
        x="Месяц",
        y="Департамент",
        z="Продуктивность",
        histfunc="avg",
        title="Тепловая карта средней эффективност",
        color_continuous_scale="Viridis",
        labels={"Продуктивность": "Ср. Эффект."}
    )

    for fig in [fig_scatter, fig_heatmap]:
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            title_font_color="#2c3e50"
        )

    return kpis, fig_scatter, fig_heatmap


if __name__ == '__main__':
    app.run(debug=True)
