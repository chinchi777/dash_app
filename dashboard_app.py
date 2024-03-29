import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
import warnings
warnings.filterwarnings('ignore')
logo_link = 'https://raw.githubusercontent.com/chinchi777/dash_app/main/real_estate_report_logo.png'

df_house=pd.read_csv('newtaipei_house_19-23.csv')
df_house.drop_duplicates()
df_resident=df_house[(df_house['交易標的']!='土地')&(df_house['交易標的']!='車位')& (df_house['單價元平方公尺'].notnull())&(df_house['都市土地使用分區']=='住')]
df_resident[['交易年月日','總價元']]=df_resident[['交易年月日','總價元']].astype('int')
df_resident[['建物移轉總面積平方公尺','單價元平方公尺']]=df_resident[['建物移轉總面積平方公尺','單價元平方公尺']].astype('float')
df_resident['總坪數']=df_resident['建物移轉總面積平方公尺'].apply(lambda x:x/3.3)
df_resident['單價元(坪)']=df_resident['單價元平方公尺'].apply(lambda x:x*3.3)
df_resident=df_resident[df_resident['交易年月日']>1071231]
df_resident['西元年月日']=df_resident['交易年月日'].apply(lambda x:x+19110000)
df_resident['西元年月日']=pd.to_datetime(df_resident['西元年月日'].astype('str'),format='%Y%m%d')
df_resident['西元年']=df_resident['西元年月日'].dt.strftime("%Y")
df_resident['西元年']=df_resident['西元年'].astype('int')
df_resident.sort_values('交易年月日', ascending=True)

df_city = df_resident.groupby('鄉鎮市區').agg({'單價元(坪)':lambda x: round(x.mean()/10000,1), '單價元平方公尺':pd.Series.count}).reset_index().rename(columns={'單價元平方公尺':'成交件數', '單價元(坪)':'平均單價（萬/坪）'})
df_city_scatter = px.scatter(df_city, x='平均單價（萬/坪）', y='成交件數', color='鄉鎮市區', width=550, height=900, custom_data=['鄉鎮市區'],title='各行政區平均單價與成交件數')
df_city_scatter.update_layout({'legend':dict(orientation='h', y=-0.7,x=1, yanchor='bottom', xanchor='right'),'title':{'x':0.5}})

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
  children=[
    html.Img(
      src=logo_link, 
      style={'width':'600px','margin':'30px 0px 0px 0px' }
    ),
    html.H1('新北市2019~2023年房價與成交件數概況', style={'font-family': 'Arial','color':'#36454F',}),
    html.Div(
      children=[
        html.Div(
          children=[
              html.Div(
                children=[
                  html.Div(
                    children=[
                      html.H1('181046', style={'fontWeight': 'bold','color':'#4169E1',}),
                      html.Label('總案件數', style={'paddingTop': '.3rem'}),
                    ],style={'margin':'10px 50px','width':'300px',
                                    'boxShadow': '#e3e3e3 4px 4px 2px', 'border-radius': '10px', 'backgroundColor': 'white', }
                  ),
                  html.Div(
                    children=[
                      html.H1('28.5%', style={'fontWeight': 'bold','color':'#4169E1'}),
                      html.Label('房價平均漲幅', style={'paddingTop': '.3rem'}),
                    ],style={'margin':'10px 50px','width':'300px',
                                    'boxShadow': '#e3e3e3 4px 4px 2px', 'border-radius': '10px', 'backgroundColor': 'white', }
                  ),
                  html.Div(
                    children=[
                      html.H1('3.3:1', style={'fontWeight': 'bold','color':'#4169E1'}),
                      html.Label('中古屋與預售比例', style={'paddingTop': '.3rem'}),
                    ],style={'margin':'10px 50px','width':'300px',
                                    'boxShadow': '#e3e3e3 4px 4px 2px', 'border-radius': '10px', 'backgroundColor': 'white', }
                  )
                ],
                style={'margin':'30px 100px 30px 100px', 'display': 'flex', 'justify-content': 'space-around',  
                       'flex-wrap': 'wrap','color':'#5F9EA0','backgroundColor':'#5F9EA0','font-family': 'Arial'}
              )
          ],
        ),
        html.Div(
            children=[
              html.H4('移動游標至圓點查看各行政區資料'),
              dcc.Graph(id='scatter', figure=df_city_scatter),
            ],
            style={'margin':'0px 20px','display':'inline-block', 'padding':'0px 20px',
                    'vertical-align':'top', 'border':'1px solid black','font-family': 'Arial','color':'#5F9EA0'}),
        html.Div(
          children=[
            html.H4('移動游標至各年度查看各行政區資料'),
            dcc.Graph(id='major_city'),

            dcc.Graph(id='bar_city'),
            
            dcc.Graph(id='minor_city'),
          ],
          style={'width':'750px', 'height':'650px','display':'inline-block','font-family': 'Arial','color':'#5F9EA0'}
        ),
        
      ]
    ),
  ], 
  style={'text-align':'center', 'display':'inline-block', 'width':'100%','backgroundColor': 'white'}
)

@app.callback(
    [Output('major_city', 'figure'),
     Output('bar_city', 'figure')],
    
    
    [Input('scatter', 'hoverData')])

def update_major_city_hover(hoverData):
    hover_city = '板橋區'
    
    if hoverData:
        hover_city = hoverData['points'][0]['customdata'][0]

    major_city_df = df_resident[df_resident['鄉鎮市區'] == hover_city]
    major_city_agg = major_city_df.groupby(['西元年','交易類型']).agg({'單價元(坪)':lambda x: round(x.mean()/10000,1), '單價元平方公尺':pd.Series.count}).reset_index().rename(columns={'單價元平方公尺':'成交件數', '單價元(坪)':'平均單價（萬/坪）'})

    house_bar_major_city = px.bar(major_city_agg, x='西元年',
                                # Ensure the Major category will be available
                                custom_data=['西元年'],
                                y='成交件數',height=275, 
                                color='交易類型',
                                title=f'{hover_city}歷年預售屋與中古屋成交件數')
    house_bar_major_city.update_layout({'margin':dict(l=10,r=15,t=40,b=0), 'title':{'x':0.5}})

    house_bar_bar_city = px.line(major_city_agg, x='西元年',
                                # Ensure the Major category will be available
                                custom_data=['西元年'],
                                y='平均單價（萬/坪）',height=275, markers=True,
                                color='交易類型',
                                title=f'{hover_city}歷年預售屋與中古屋成交均價')
    house_bar_bar_city.update_xaxes(dtick="M12",tickformat="%Y")
    house_bar_bar_city.update_layout({'margin':dict(l=10,r=15,t=40,b=0), 'title':{'x':0.5}})

   

    return house_bar_major_city, house_bar_bar_city



# Set up a callback for click data
@app.callback(
    Output('minor_city', 'figure'),

    Input('major_city', 'clickData')
)

def update_major_city_click(clickData):
    click_year = '2023'
    major_city_df = df_resident.copy()
    year_volume = major_city_df.groupby(['西元年','鄉鎮市區'])['交易標的'].count().reset_index(name='成交件數')
    
    # Extract the major category clicked on for usage
    if clickData:
        click_year = (clickData['points'][0]['customdata'][0])
        
        # Undetake a filter using the major category clicked on
    
        major_city_df = df_resident[df_resident['西元年'] == click_year]
      
    city_mj_ct_agg = major_city_df.groupby(['西元年','鄉鎮市區']).agg({'單價元(坪)':lambda x: round(x.mean()/10000,1)}).reset_index()
    #city_mj_ct_agg['Sales %'] = (country_mj_cat_agg['Total Sales ($)'] / total_sales['Total Sales ($)'] * 100).round(1)
    
    house_bar_city_mj_ct = px.bar(city_mj_ct_agg, x='單價元(坪)', y='鄉鎮市區', 
                                orientation='h',width=750, height=600, text='單價元(坪)', 
                                     title=f'新北市{click_year}年度各區成交平均價')
    house_bar_city_mj_ct.update_layout({'yaxis':{'categoryorder':'total ascending'}, 'title':{'x':0.5}})

    return house_bar_city_mj_ct  
    

 

  
if __name__ == '__main__':
    app.run_server(debug=True)
