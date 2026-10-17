import dash_ag_grid as dag
from dash import Dash, html, dcc, callback, Input, Output
import plotly.express as px

app = Dash()

data = [
    {"Менеджер": "Иван", "Январь": 120, "Фераль": 150, "Март": 180},
    {"Менеджер": "Ольга", "Январь": 200, "Фераль": 190, "Март": 220},
    {"Менеджер": "Анна", "Январь": 90, "Фераль": 110, "Март": 130}
]

app.layout = html.Div([
    html.H3("Продажи менеджеров (Кликните на строку для просмотра графика)"),
    dag.AgGrid(
        id="managers-grid",
        rowData=data,
        columnDefs=[
            {"field": "Менеджер", "checkboxSelection": True},
            {"field": "Январь"},
            {"field": "Фераль"},
            {"field": "Март"},
        ],
        defaultColDef={"sortable": True, "filter": True},
        dashGridOptions={"rowSelection": "single"},
    ),
    html.Br(),
    dcc.Graph(id="managers-sales-graph"),
],
    style={"padding": "20px", "font-family": "Arial"},
)


@app.callback(
    Output(component_id='managers-sales-graph', component_property='figure'),
    Input(component_id='managers-grid', component_property='selectedRows'),
)
def update_graph(selected_rows):
    if not selected_rows:
        row_data = data[0]
    else:
        row_data = selected_rows[0]

    months = ["Январь", "Фераль", "Март"]
    sales_values = [row_data[month] for month in months]

    fig = px.line(
        x=months,
        y=sales_values,
        title=f"Динамика продаж: {row_data['Менеджер']}",
        labels={"x": "Месяц", "y": "Объем продаж"},
        markers=True
    )

    fig.update_layout(yaxis_range=[0, 300])

    return fig


if __name__ == '__main__':
    app.run(debug=True)
