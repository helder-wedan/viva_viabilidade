import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, ClientsideFunction, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from babel.numbers import format_currency
import openpyxl

# import load_workbook
# =======================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server
# =======================

dir = "database/banco_tabuas.xlsx"
tabuas = pd.read_excel(dir)

lista = tabuas.columns[1:]

def comutacao(nome_tabua):
    tabua = tabuas[['x',nome_tabua]].dropna()
    tabua.columns = ['x','qx']
    
    tabua['lx'] = 1000000
    for i in tabua.x[1:]:
        tabua.loc[i,'lx'] = (1 - tabua.qx[i-1]) * tabua.lx[i-1]

    tabua['Lx']= tabua.lx /2
    for i in tabua.x[1:]:
        tabua.loc[i-1,'Lx'] = (tabua.lx[i-1] + tabua.lx[i]) /2

    tabua['Tx'] = tabua['Lx'].sum()
    for i in tabua.x:
        tabua.loc[i,'Tx'] = tabua.loc[i:,'Lx'].sum()
        
    tabua['ex_o'] = 0
    for i in tabua.x[:-1]:
        tabua.loc[i,'ex_o'] = tabua.loc[i+1:,'lx'].sum() / tabua.loc[i,'lx']
    
    tabua['ex'] = tabua.Tx / tabua.lx

    return tabua

tabua = comutacao(lista[5])


def card(name,id):
    cardbody = dbc.Card([dbc.CardBody([
                                    html.H5(name, className="card-text"),
                                    html.H6(#style={"color": "#5d8aa7"}, 
                                            id=id, className="card-text"),
                                    ])
                                ], id=id+"tooltip",
                                color="#003e4c", outline=True,inverse=True, style={"margin-top": "20px","margin-left": "15px",
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                        #"color": "#FFFFFF"
                                        },)
    return cardbody


def criar_figura(tabela, y1_col, y2_col, y2_name, title):
    fig = go.Figure(layout={"template": "plotly_white"})
    x = tabela['Mês']
    y1 = tabela[y1_col]
    y2 = tabela[y2_col]

    fig.add_trace(
        go.Scatter(
            x=x, 
            y=y1,
            name=y1.name,
            fill='tozeroy',
            line=dict(color='#003e4c', width=4)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=x, 
            y=y2,
            yaxis='y2',
            name=y2_name,
            line=dict(color='#a50000', width=4),
        )
    )

    fig.update_layout(
        separators=',.',
        margin=dict(l=60, r=40, b=40, t=60),
        title={
            "text": f'<b>{title}</b>',
            "font": dict(size=14),
            "y": 0.9,
            'x': 0.5,
            'xanchor': 'center',
            "yanchor": "top",
        },
        legend=dict(
            xanchor="center",
            x=0.5,
            orientation="h"
        ),
        yaxis2=dict(
            title=y2_name,
            titlefont=dict(color="#a50000"),
            tickfont=dict(color="#a50000"),
            anchor="x",
            overlaying="y",
            side="right",
        ),
    )

    fig.update_yaxes(mirror=True, showline=True, linewidth=2, showspikes=True, fixedrange=False)
    fig.update_xaxes(mirror=True, showline=True, linewidth=2)

    return fig

# PARÂMETROS #

tx_juros_anual = 3.5 /100
comissao = 2 /100
tx_adm_anual = 0.9 /100
portabilidade = 1000000.00
tx_liquida_anual = (1+tx_juros_anual)/(1+tx_adm_anual) -1

tx_juros_mensal = (tx_juros_anual+1)**(1/12) -1
tx_adm_mensal = (tx_adm_anual+1)**(1/12) -1
tx_liquida_mensal = (tx_liquida_anual+1)**(1/12) -1

idade = 55
expectativa = tabua.loc[idade,'ex']
meses = int(expectativa*12)
idade_final = idade + expectativa
beneficio = tx_liquida_mensal * portabilidade / (1-(1+tx_liquida_mensal)**-meses)

def header():
    header_geral = html.Div([
        html.Div([
            dbc.Row([
                dbc.Col(
                    html.H3(
                        dbc.Badge(
                            "VIVAPREV",
                            color="#5d8aa7",
                            className="me-1",
                                    )
                        )
                    ),
                    dbc.Col([
                        html.Img(
                            id="logo",
                            src=app.get_asset_url("logo.png"),
                            height=50,
                            )
                        ],style={"textAlign": "right"},),
                    ]),
                ],style={
                    "background-color": "#003e4c",  # 003e4c",
                    "margin": "0px",
                    "padding": "20px",
                    },
        ),
        html.Div([
            dbc.Nav([
                dbc.Navbar(
                    dbc.Container(
                        children=[
                            dbc.NavItem(
                                dbc.NavLink(
                                    "",#PEONA   ",
                                    href="",#/peona",
                                    className="nav-link",
                                    ),
                                    style={
                                        "margin": "-20px",
                                        "margin-left": "20px",
                                    },
                                ),
                            dbc.NavItem(
                                dbc.NavLink(' ',#Margem de Solvência   ',
                                             href=' ',#/prestadores', 
                                             className="nav-link"),
                                             style={"margin": "-20px",
                                                    "margin-left": "20px"},),
                                    ],
                            fluid=True,
                        ),
                        color="light",
                        dark=False,
                        # class_name='collapse navbar-collapse',
                    )
                ],class_name="navbar navbar-light bg-light",),
                # ]),
            ]),
    ])

    return header_geral

tela = html.Div(children=[
        dbc.Row([
            header()
                ]),
            dbc.Row([
                dbc.Col([
                    html.H5(
                        dbc.Badge(
                            "Escolha a Tábua de Mortalidade:",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "25px",
                                "margin-top": "10px",
                                },
                                    )
                            ),
                        dcc.Dropdown(
                            id="select-table",
                            value=lista[5],
                            options=[
                                {
                                    "label": i,
                                    "value": i,
                                }
                                for i in lista
                            ],
                            placeholder="Selecione a tábua",
                            style={
                                "width": "60%",
                                #'padding': '3px',
                                "margin-left": "10px",
                                "margin-bottom": "20px",
                                #'font-size':'18px',
                                "textAlign": "center",
                            },
                            ),
                        
                        dbc.Badge(
                            "Idade",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "25px",
                                "margin-top": "10px",
                                },
                                    ),                        
                        dcc.Input(id="idade", type="number", placeholder="Idade",
                                  min=10, max=100, value=55,
                                  style={'width' : '5%'}, ),

                        dbc.Badge(
                            "Comissão (%)",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "25px",
                                "margin-top": "10px",
                                },
                                    ),
                        dcc.Input(id="comissao", type="number", placeholder="Comissão (%)",
                                  value=2.00,min=0,
                                  style={'width' : '5%'}),
                        
                        dbc.Badge(
                            "Taxa de Juros (% a.a.)",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "25px",
                                "margin-top": "10px",
                                },
                                    ),
                        dcc.Input(id="tx_juros_anual", type="number", placeholder="Taxa de Juros (% a.a.)",
                                  value=3.5,min=0,
                                  style={'width' : '5%'}),

                        dbc.Badge(
                            "Taxa de Adm (% a.a.)",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "25px",
                                "margin-top": "10px",
                                },
                                    ),
                        dcc.Input(id="tx_adm_anual", type="number", placeholder="Taxa de Adm (% a.a.)",
                                  value=0.9,min=0,
                                  style={'width' : '5%'}),

                        dbc.Badge(
                            "Portabilidade",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "25px",
                                "margin-top": "10px",
                                },
                                    ),

                        dcc.Input(id="portabilidade", type="number", placeholder="Portabilidade",
                                  value=1000000.00,min=0),

                        dbc.Badge(
                            "Diferimento (meses)",
                            color="#5d8aa7",
                            className="me-1",
                            style={
                                "margin-left": "25px",
                                "margin-top": "10px",
                                },
                                    ),

                        dcc.Input(id="diferimento", type="number", placeholder="Diferimento (meses)",
                                  value=36,min=1,
                                  style={'width' : '5%'}),
            
            ]),
            ]),
            dbc.Row([dbc.Col([
                card("Comissão","comissao_card"),
                card("Benefício","beneficio_card"),
                card("Benefício Diferido","beneficio_diferido_card"),
                card("Expectativa de Vida","expectativa_card"),
                card("Qtd. Meses","meses_card"),
                card("Idade Final","idade_final_card"),
                card("Ponto de Equilíbrio","ponto_equilibrio_card"),
                card("Ponto de Equilíbrio Diferido","ponto_equilibrio_dif_card"),
                ],xs = 7, sm=7, md=5, lg=2),

            dbc.Col([dcc.Loading(id="loading-1",type="dot",),
                     html.Div([dcc.Graph(id="saldo_pga"),],),
                     html.Div([dcc.Graph(id="saldo_portabilidade"),]),
                     html.Div([dcc.Graph(id="saldo_pga_dif"),]),
                     html.Div([dcc.Graph(id="saldo_portabilidade_dif"),]),
            ]),
            ]),
]),

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), 
     html.Div(id="page-content"),
#     html.Link(rel="stylesheet", href=css_print_path, className="dash-spreadsheet"),
]
)

@app.callback(
    [   Output("loading-1", "children"),
        Output("comissao_card", "children"),
        Output("beneficio_card", 'children'),
        Output("beneficio_diferido_card", 'children'),
        Output("expectativa_card", 'children'),
        Output("meses_card", 'children'),
        Output('idade_final_card', 'children'),
        Output('ponto_equilibrio_card', 'children'),
        Output('ponto_equilibrio_dif_card', 'children'),
        Output('saldo_pga', 'figure'),
        Output('saldo_portabilidade', 'figure'),
        Output("saldo_pga_dif", 'figure'),
        Output("saldo_portabilidade_dif", 'figure'),
    ],
    [
        Input('select-table', 'value'),
        Input('idade', 'value'),
        Input('comissao', 'value'),
        Input('tx_juros_anual', 'value'),
        Input('tx_adm_anual', 'value'),
        Input('portabilidade', 'value'),
        Input('diferimento', 'value'),
    ],
)
def update_values(tabua_nome, idade,comissao,tx_juros_anual,tx_adm_anual,portabilidade,diferimento):
    tabua = comutacao(tabua_nome)
    tx_juros_anual = tx_juros_anual /100
    comissao = comissao /100
    comissao_valor = format_currency(portabilidade*comissao + 0.0, "BRL", locale="pt_BR")
    tx_adm_anual = tx_adm_anual /100
    tx_liquida_anual = (1+tx_juros_anual)/(1+tx_adm_anual) -1
    tx_juros_mensal = (tx_juros_anual+1)**(1/12) -1
    tx_adm_mensal = (tx_adm_anual+1)**(1/12) -1
    tx_liquida_mensal = (tx_liquida_anual+1)**(1/12) -1
    expectativa = tabua.loc[idade,'ex']
    meses = int(expectativa*12)
    idade_final = idade + expectativa
    beneficio = tx_liquida_mensal * portabilidade / (1-(1+tx_liquida_mensal)**-meses)
    tabela = pd.DataFrame(columns=['Mês','Saldo Portabilidade','Comissão','Rentabilidade','Benefício','Taxa Adm','Saldo PGA'])

    tabela['Mês'] = range(1,meses+1)
    tabela['Benefício'] = beneficio

    for i,r in tabela.iterrows():
        if i == 0:
            tabela.loc[i,'Saldo Portabilidade'] = portabilidade
            tabela.loc[i,'Comissão'] = comissao * portabilidade
            tabela.loc[i,'Rentabilidade'] = tabela.loc[i,'Saldo Portabilidade'] * (1+tx_juros_mensal)
            tabela.loc[i,'Taxa Adm'] = tabela.loc[i,'Rentabilidade'] * tx_adm_mensal        
            tabela.loc[i,'Saldo PGA'] = tabela.loc[i,'Taxa Adm'] - tabela.loc[i,'Comissão']
    tx_2 = (tabela['Rentabilidade'][0] - portabilidade - tabela['Taxa Adm'][0]) / portabilidade

    beneficio = tx_2 * portabilidade / (1-(1+tx_2)**-meses)

    tabela['Benefício'] = beneficio

    for i,r in tabela.iterrows():
        if i == 0:
            tabela.loc[i,'Saldo Portabilidade'] = portabilidade
            tabela.loc[i,'Comissão'] = comissao * portabilidade
            tabela.loc[i,'Rentabilidade'] = tabela.loc[i,'Saldo Portabilidade'] * (1+tx_juros_mensal)
            tabela.loc[i,'Taxa Adm'] = tabela.loc[i,'Rentabilidade'] * tx_adm_mensal        
            tabela.loc[i,'Saldo PGA'] = tabela.loc[i,'Taxa Adm'] - tabela.loc[i,'Comissão']
        
        else:
            tabela.loc[i,'Saldo Portabilidade'] = tabela.loc[i-1,'Rentabilidade'] - tabela.loc[i-1,'Taxa Adm'] - beneficio
            tabela.loc[i,'Rentabilidade'] = tabela.loc[i,'Saldo Portabilidade'] * (1+tx_juros_mensal)
            tabela.loc[i,'Taxa Adm'] = tabela.loc[i,'Rentabilidade'] * tx_adm_mensal
            tabela.loc[i,'Saldo PGA'] = tabela.loc[i,'Taxa Adm'] + tabela.loc[i-1,'Saldo PGA']
    
    pronto_equilibrio = tabela[tabela['Saldo PGA']>0]['Mês'].min()
    
    saldo_diferido = portabilidade*(1+tx_2)**diferimento
    beneficio_diferido = tx_2 * saldo_diferido / (1-(1+tx_2)**-(meses-diferimento))

    tabela_diferida = pd.DataFrame(columns=['Mês','Saldo Portabilidade','Comissão','Rentabilidade','Benefício','Taxa Adm','Saldo PGA'])

    tabela_diferida['Mês'] = range(1,meses+1)
    tabela_diferida['Benefício'] = np.where(tabela_diferida['Mês'] <= diferimento,0,beneficio_diferido)

    for i,r in tabela_diferida.iterrows():
        if i == 0:
            tabela_diferida.loc[i,'Saldo Portabilidade'] = portabilidade
            tabela_diferida.loc[i,'Comissão'] = comissao * portabilidade
            tabela_diferida.loc[i,'Rentabilidade'] = tabela_diferida.loc[i,'Saldo Portabilidade'] * (1+tx_juros_mensal)
            tabela_diferida.loc[i,'Taxa Adm'] = tabela_diferida.loc[i,'Rentabilidade'] * tx_adm_mensal        
            tabela_diferida.loc[i,'Saldo PGA'] = tabela_diferida.loc[i,'Taxa Adm'] - tabela_diferida.loc[i,'Comissão']
        
        else:
            tabela_diferida.loc[i,'Saldo Portabilidade'] = tabela_diferida.loc[i-1,'Rentabilidade'] - tabela_diferida.loc[i-1,'Taxa Adm'] - tabela_diferida.loc[i-1,'Benefício']
            tabela_diferida.loc[i,'Rentabilidade'] = tabela_diferida.loc[i,'Saldo Portabilidade'] * (1+tx_juros_mensal)
            tabela_diferida.loc[i,'Taxa Adm'] = tabela_diferida.loc[i,'Rentabilidade'] * tx_adm_mensal
            tabela_diferida.loc[i,'Saldo PGA'] = tabela_diferida.loc[i,'Taxa Adm'] + tabela_diferida.loc[i-1,'Saldo PGA']

    ponto_equilibrio_dif = tabela_diferida[tabela_diferida['Saldo PGA']>0]['Mês'].min()

    figura1 = criar_figura(tabela, 'Saldo PGA', 'Taxa Adm', 'Tx Adm Mensal', 'Saldo do PGA e Taxa Adm Mensal')
    figura2 = criar_figura(tabela, 'Saldo Portabilidade', 'Benefício', 'Benefício', 'Saldo de Portabilidade e Benefício Mensal')
    figura3 = criar_figura(tabela_diferida, 'Saldo PGA', 'Taxa Adm', 'Tx Adm Mensal', 'Saldo do PGA e Taxa Adm Mensal (com diferimento)')
    figura4 = criar_figura(tabela_diferida, 'Saldo Portabilidade', 'Benefício', 'Benefício', 'Saldo de Portabilidade e Benefício Mensal (com diferimento)')

    return "",comissao_valor,format_currency(beneficio + 0.0, "BRL", locale="pt_BR"),format_currency(beneficio_diferido + 0.0, "BRL", locale="pt_BR"),f"{round(expectativa,2)} anos",meses,f"{round(idade_final,2)} anos",f"{pronto_equilibrio} meses",f"{ponto_equilibrio_dif} meses",figura1,figura2,figura3,figura4


@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if (
        pathname == "/provisoes"
        or pathname == "/"
    ):
        return tela
    elif pathname == '':#/prestadores':
        return tela
    
    elif pathname == ' ':#/pesl':
        return tela
        
    else:
        return tela
#======================================


if __name__ == "__main__":
    app.run_server(debug=True)  # , port=8051)
    