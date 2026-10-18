# import sqlite3
# import pandas as pd

# conn = sqlite3.connect('company_metrics.db')
#
# data = {
#     "Месяц": ['2026-01', "2026-02", '2026-01', "2026-02"],
#     "Департамент": ["IT", "IT", "Маркетинг", "Маркетинг"],
#     "Продуктивность": [75.9, 75.2, 73.4, 76.2],
#     "Часы_работы": [160, 120, 180, 170],
#     "Удовлетворенность": [4.2, 4.5, 3.9, 4.1]
# }
#
# df_init = pd.DataFrame(data)
#
# df_init.to_sql('hr_metrics', con=conn, if_exists='replace', index=False)
# conn.close()
# print("База данных успешно создана и наполнена")


import sqlite3
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

app = Dash()

conn = sqlite3.connect('company_metrics.db')
all_months = pd.read_sql("SELECT DISTINCT Месяц FROM hr_metrics ORDER BY Месяц", conn)["Месяц"].to_list()
print(all_months)
conn.close()

app.layout = html.Div([
    html.H1("Дашборд с подключением к SQLite"),
    dcc.RangeSlider(
        id='month-slider',
        min=0,
        max=len(all_months) - 1,
        value=[0, len(all_months) - 1],
        marks={i: m for i, m in enumerate(all_months)},
        step=None,
    ),
    dcc.Graph(id='db-scatter-chart'),
])


@app.callback(
    Output('db-scatter-chart', 'figure'),
    [Input('month-slider', 'value')]
)
def update_graph(selected_month_id):
    chosen_months = all_months[selected_month_id[0]:selected_month_id[1] + 1]
    conn = sqlite3.connect('company_metrics.db')
    query = "SELECT * FROM hr_metrics WHERE Месяц IN ({})".format(
        ",".join("?" for m in chosen_months)
    )

    filtered_df = pd.read_sql(query, conn, params=chosen_months)
    conn.close()

    fig = px.scatter(
        filtered_df,
        x="Часы_работы",
        y="Продуктивность",
        color="Департамент",
        title="Данные из реальной базы SQLite"
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)
