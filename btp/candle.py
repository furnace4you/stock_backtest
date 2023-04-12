from typing import List, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class _Factory:
    def __init__(self):
        self._creators = {}

    def register(self, code: str):
        def _decorator(callback: type):
            self._creators[code] = callback
            return callback
        return _decorator

    def apply(self, data: pd.DataFrame, code: str):
        return self._creators[code](data)


_Creators = _Factory()

def register(code: str) -> type:
    return _Creators.register(code)


@register('Candlestick')
def candlestick_figure_creator(data: pd.DataFrame):
    return go.Candlestick(
        **{
            'x': data.index,
            'open': data.open,
            'high': data['high'],
            'low': data['low'],
            'close': data['close'],
            'increasing_line_color': 'red',
            'decreasing_line_color': 'green',
            'increasing_fillcolor': 'red',
            'decreasing_fillcolor': 'green',
            'increasing_line_width': 1,
            'decreasing_line_width': 1,
            'whiskerwidth': 0,
            'opacity': 0.8,
            'name': '价格'
        }
    )


@register('Volume')
def volume_figure_creator(data: pd.DataFrame):
    return go.Bar(**{
        'type': 'bar',
        'x': data.index,
        'y': data['volume'],
        'name': '成交量',
        'marker_color': np.where(data['close'] >= data['open'], 'red', 'green'),
        'opacity': 0.7
    })


@register('MACD')
def macd_figure_creator(data: pd.DataFrame):
    return go.Bar(**{
        'type': 'bar',
        'x': data.index,
        'y': data.MACD,
        'name': 'MACD',
        'marker_color': np.where(data.MACD > 0, 'red', 'green'),
        'opacity': 0.7
    })

def extract_dates_breaks(dates: pd.Series, tickformat: str = '%Y-%m-%d') -> List[str]:
    date_range = pd.date_range(
        start=dates[0], end=dates[-1])
    exists = [d.strftime(tickformat) for d in pd.to_datetime(dates)]
    return [d for d in date_range.strftime(tickformat).tolist() if not d in exists]

def CreateCandlestrickPlot(data: pd.DataFrame):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, row_heights=[0.52, 0.22, 0.22])
	
    ##简单的散点图创建
    def _inner_creator(figure_type, code, description):
        return {
            'type': figure_type,
            'x': data.index,
            'y': data[code],
            'name': description,
            'line_width': 1
        }

    # 蜡烛图及其移动均线
    fig.add_traces([
        _Creators.apply(data, 'Candlestick'),
        # _inner_creator('scatter', 'EMA12', 'EMA12'),
        # _inner_creator('scatter', 'EMA26', 'EMA26')
    ])

    # 成交量及其移动均线
    fig.add_traces([
        _Creators.apply(data, 'Volume'),
        # _inner_creator('scatter', 'VOL-MA5', '5日均线'),
        # _inner_creator('scatter', 'VOL-MA10', '10日均线')
    ], rows=2, cols=1)
    # MACD指标
    # fig.add_traces([
    #     _Creators.apply(data, 'MACD'),
    #     _inner_creator('scatter', 'DIF', 'DIF'),
    #     _inner_creator('scatter', 'DEA', 'DEA')
    # ], rows=3, cols=1)

    # 指定空白点
    tickformat = '%Y-%m-%d'
    fig.update_xaxes(
        rangebreaks=[
            dict(values=extract_dates_breaks(data.index, tickformat))],
        tickformat='%Y-%m'
    )
    ## ...TODO
    # 指定大小及边距
    fig.update_layout(
        # margin=dict(l=20, r=20, t=20, b=20),
        width=1680,
        height=720
    )

    ##范围选择处理
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    # dict(count=1,
                    #      label="YTD",
                    #      step="year",
                    #      stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=False
            ),
            type="date"
        )
    )

    ##禁止显示Y方向的网格
    fig.update_xaxes(matches='x',
                     showgrid=False)

    ##时间范围选择条的显示和高度控制
    fig.update_layout(
        xaxis3=dict(
            rangeslider=dict(
                visible=True,
                thickness=0.05
            )
        )
    )

    ##指定图标题和Y轴标题
    fig.update_layout(
        title={
            'text': f'K线图',
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title='股价',
        yaxis2_title='成交量',
        # yaxis3_title='MACD'
    )

    ##调整图例位置为右上角平铺
    fig.update_layout(
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=0.98,
            xanchor='right',
            x=1
        )
    )
    return fig



