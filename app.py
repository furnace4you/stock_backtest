from mysql import connect,exec_select
import pandas as pd

conn = connect()

def _select_market(code):
    """
    1- sh
    0 -sz
    2 -新三板
    """
    if '.' in code: return code
    code = str(code)
    if code[0] in ['4', '8']: return '{}.XSHG'.format(code)
    if code[0] in ['5', '6', '9'] or code[:3] in ["009", "126", "110", "201", "202", "203", "204"]:
        return '{}.XSHG'.format(code)
    return '{}.XSHE'.format(code)

def all_securities():
    sql = '''
    select * from t_all_securities
    '''    
    res = exec_select(sql,conn)
    df = pd.DataFrame(res)
    df.columns = ["security","display_name","name","start_date","end_date"]
    return df

def kline_day(code,start_date='1990-01-01',end_date='2900-01-01'):
    code = _select_market(code)

    for i in range(5):
        sql = '''
        select * from t_kline_day_{} where security="{}" and kday>="{}" and kday<="{}"
        '''.format(i,code,start_date,end_date)

        res = exec_select(sql,conn)

        if len(res)>0:
            df = pd.DataFrame(res)
            df.columns = ["security","kday","open","close","low","high","volume","money","factor","high_limit","low_limit","avg","pre_close","paused"]
            return df
    return None

def valuation(code,start_date='1990-01-01',end_date='2900-01-01'):
    code = _select_market(code)

    for i in range(5):
        sql = '''
        select * from t_valuation_{} where code="{}" and day>="{}" and day<="{}"
        '''.format(i,code,start_date,end_date)

        res = exec_select(sql,conn)

        if len(res)>0:
            df = pd.DataFrame(res)
            df.columns = ["code","day","capitalization","circulating_cap","market_cap","circulating_market_cap","turnover_ratio","pe_ratio","pe_ratio_lyr","pb_ratio","ps_ratio","pcf_ratio"]
            return df
    return None

# df = all_securities()
# df = kline_day('000008.XSHE')
df = valuation('000001.XSHE')
print(df)
