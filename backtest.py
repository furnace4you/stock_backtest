import plotly.io
from datetime import datetime, timedelta

import backtrader as bt
import pandas as pd
import importlib

import streamlit as st
from btp.plotter import BacktraderPlotly
from btp.scheme import PlotScheme


class BackTest():
    def __init__(self, MyEnv, MyStrategy):
        self.env = importlib.import_module(MyEnv)
        self.MyStrategy = getattr(
            importlib.import_module(MyStrategy), 'MyStrategy')

    class Broker(bt.Observer):
        alias = ('CashValue',)
        lines = ('value', 'benchmark',)

        plotinfo = dict(plot=True, subplot=True, plotname=' ')
        plotlines = dict(value=dict(_name='策略总价值', _plotvalue=False),
                         benchmark=dict(_name='基准总价值', _plotvalue=False))
                         

        def __init__(self):
            cash = self._owner.broker.getcash()
            price = 0
            for i in range(len(self.datas)):
                price += self.datas[i].close[1]

            self.benchmark_cash = 0
            self.benchmark_amount = cash/price
            self.benchmark_value = cash

        def next(self):
            price = 0
            for i in range(len(self._owner.datas)):
                price += self._owner.datas[i].close[0]
            self.lines.benchmark[0] = self.benchmark_cash + self.benchmark_amount * price
            self.benchmark_value = self.lines.benchmark[0]
            self.lines.value[0] = self._owner.broker.getvalue()

    class BSObserver(bt.observer.Observer):
        lines = ('buy', 'sell',)

        plotinfo = dict(plot=True, subplot=False,
                        plotlinelabels=True, plotname=' ')

        plotlines = dict(
            buy=dict(marker='^', markersize=8.0, color='lime',
                     fillstyle='full', _name='买入'),
            sell=dict(marker='v', markersize=8.0, color='fuchsia',
                      fillstyle='full', _name=' 卖出')
        )

        def next(self):
            for order in self._owner._orderspending:
                # if order.data is not self.data:
                #     continue

                if order.status in [order.Completed]:
                    print("buy or sell", self.data.datetime.datetime())
                    if order.isbuy():
                        self.lines.buy[0] = order.executed.price
                    else:
                        self.lines.sell[0] = order.executed.price

    def plotIt(self, cerebro):
        scheme = PlotScheme(decimal_places=2, max_legend_text_width=16)
        figs = cerebro.plot(BacktraderPlotly(show=False, scheme=scheme))
        for i, each_run in enumerate(figs):
            for j, each_strategy_fig in enumerate(each_run):
                st.markdown("---")
                st.subheader("可视化结果")
                st.plotly_chart(each_strategy_fig, use_container_width=True)

    def run(self, strat_params):
        print("backtest run")
        cerebro = bt.Cerebro(stdstats=False)
        self.env.set_env(cerebro)
        cerebro.addobserver(self.Broker)
        cerebro.addstrategy(self.MyStrategy)

        cerebro.addobserver(self.BSObserver)
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')

        cash = cerebro.broker.getcash()

        thestrats = cerebro.run()
        thestrat = thestrats[0]

        AnnualReturnAna = thestrat.analyzers.getbyname('AnnualReturn').get_analysis()
        AnnualReturnAnaDf = pd.DataFrame.from_dict(AnnualReturnAna, 'index', columns=['年化收益'])
        AnnualReturnAnaDf.index.name = '年份'
        AnnualReturnAnaDf['年化收益'] = AnnualReturnAnaDf['年化收益'].apply(lambda x: format(x, ".2%"))
        DrawDown = thestrat.analyzers.getbyname('DrawDown').get_analysis()
        SharpeRatio = thestrat.analyzers.getbyname('SharpeRatio').get_analysis()
        TradeAnalyzer = thestrat.analyzers.getbyname('TradeAnalyzer').get_analysis()

        port_value = cerebro.broker.getvalue()  # 获取回测结束后的总资金
        pnl = port_value - cash  # 盈亏统计

        n = len(cerebro.datas[0].close)
        price = 0
        for i in range(len(cerebro.datas)):
            price += cerebro.datas[i].close[-(n-1)]
        amount = cash/price
        price = 0
        for i in range(len(cerebro.datas)):
            price += cerebro.datas[i].close[0]
        end_cash=amount*price

        st.subheader("回测结果")
        st.write(f"初始/最终/收益: *{cash}*/*{round(port_value, 2)}*/*{round(pnl, 2)}*")
        st.write(f"策略收益/基准收益: *{round(pnl * 100 / port_value, 2)}%*/*{round(end_cash * 100 / cash - 100, 2)}%*")
        st.write(f"最大回撤: *{round(DrawDown.max.drawdown, 2)}%*")
        if 'sharperatio' in SharpeRatio and SharpeRatio['sharperatio']:
            st.write(f"夏普比率: *{round(SharpeRatio['sharperatio'], 2)}*")
        try:
            st.write(f"交易次数/胜率: *{TradeAnalyzer.total.total}*/*{round(TradeAnalyzer.won.total * 100.0 / TradeAnalyzer.total.total, 2)}%*")
        except Exception as e:
            pass
        st.write('年化收益:')
        st.dataframe(AnnualReturnAnaDf)

        self.plotIt(cerebro)
