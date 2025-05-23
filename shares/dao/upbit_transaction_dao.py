from shares.modules.postgres import *

class UpbitTransactionDao():
    
    def __init__(self):
        self.postgres = Postgres()
    
    def is_exist_table(self, table_name):
        
        query = f"""
            SELECT to_regclass('public.{table_name}');
        """
        res = self.postgres.read_one(query)
        if res.get("to_regclass"):
            return True
        
        else:
            return False
    
    def create_upbit_transaction_table(self, table_name):
        
        query = f"""
            CREATE TABLE public.{table_name} (
                seq serial4 NOT NULL,
                ticker varchar(1000) NOT NULL,
                tick_datetime timestamptz NOT NULL,
                data_row JSONB,        
                reg_dt timestamptz NULL,
                mod_dt timestamptz NULL,
                CONSTRAINT {table_name}_pkey PRIMARY KEY (seq),
                CONSTRAINT {table_name}_ticker_tick_datetime_unique UNIQUE (ticker, tick_datetime)
            );

        """
        res = self.postgres.execute_query_with_commit(query)
        return res
    
    def create_index(self, index_cols, table_name):
        
        query = ""
        for index_col in index_cols:
            query += f"""
                CREATE INDEX ix_{table_name}_{index_col} ON public.{table_name} ({index_col});
            """
            
        res = self.postgres.execute_query_with_commit(query)
        return res
        
    def get_upbit_transaction_with_tick_datetime(self, table_name, tick_datetime):
        
        query = f"""
            SELECT
                seq,
                ticker,
                tick_datetime,
                data_row, 
                reg_dt, 
                mod_dt
            FROM
                {table_name}
            WHERE 
                tick_datetime = '{tick_datetime}'
            LIMIT 1 
        """
        return self.postgres.read_one(query) 
    
    def get_upbit_transaction_with_tick_datetime_list(self, table_name, ticker, tick_datetime_list):
        
        query = f"""
            SELECT
                seq,
                ticker,
                tick_datetime,
                reg_dt, 
                mod_dt
            FROM
                {table_name}
            WHERE ticker = '{ticker}'
        """
        where_clause = " AND tick_datetime IN ({})".format(','.join(f"'{item}'" for item in tick_datetime_list))
        query += where_clause
        
        return self.postgres.read_all(query) 
    
    def get_upbit_transactions_between(self, table_name, ticker, start, end):
        
        query = f"""
            SELECT
                seq,
                ticker,
                tick_datetime as tick_datetime,
                data_row->>'timestamp' as timestamp,
                data_row->>'weekday' as weekday,
                data_row->>'open' as open,
                data_row->>'high' as high,
                data_row->>'low' as low,
                data_row->>'close' as close,
                data_row->>'volume' as volume,
                data_row->>'volume_ma5' as volume_ma5,
                data_row->>'volume_ma20' as volume_ma20,
                data_row->>'volume_ratio' as volume_ratio,
                data_row->>'obv' as obv,
                data_row->>'vwap'  as vwap,
                data_row->>'volume_volatility' as volume_volatility,
                data_row->>'volume_spike' as volume_spike,
                data_row->>'rsi' as rsi,
                data_row->>'macd' as macd,
                data_row->>'macd_signal' as macd_signal,
                data_row->>'bollinger_partition' as bollinger_partition,
                data_row->>'bollinger_partition_prev' as bollinger_partition_prev,
                data_row->>'atr' as atr,
                data_row->>'cci' as cci,
                data_row->>'stochastic_k' as stochastic_k,
                data_row->>'stochastic_d' as stochastic_d,
                data_row->>'roc' as roc,
                data_row->>'momentum' as momentum,
                data_row->>'ema_cross_up' as ema_cross_up,
                data_row->>'cdl2crows' as cdl2crows,
                data_row->>'cdl3blackcrows' as cdl3blackcrows,
                data_row->>'cdl3inside' as cdl3inside,
                data_row->>'cdl3linestrike' as cdl3linestrike,
                data_row->>'cdl3outside' as cdl3outside,
                data_row->>'cdl3starsinsouth' as cdl3starsinsouth,
                data_row->>'cdl3whitesoldiers' as cdl3whitesoldiers,
                data_row->>'cdlabandonedbaby' as cdlabandonedbaby,
                data_row->>'cdladvanceblock' as cdladvanceblock,
                data_row->>'cdlbelthold' as cdlbelthold,
                data_row->>'cdlbreakaway' as cdlbreakaway,
                data_row->>'cdlclosingmarubozu' as cdlclosingmarubozu,
                data_row->>'cdlconcealbabyswall' as cdlconcealbabyswall,
                data_row->>'cdlcounterattack' as cdlcounterattack,
                data_row->>'cdldarkcloudcover' as cdldarkcloudcover,
                data_row->>'cdldoji' as cdldoji,
                data_row->>'cdldojistar' as cdldojistar,
                data_row->>'cdldragonflydoji' as cdldragonflydoji,
                data_row->>'cdlengulfing' as cdlengulfing,
                data_row->>'cdleveningdojistar' as cdleveningdojistar,
                data_row->>'cdleveningstar' as cdleveningstar,
                data_row->>'cdlgapsidesidewhite' as cdlgapsidesidewhite,
                data_row->>'cdlgravestonedoji' as cdlgravestonedoji,
                data_row->>'cdlhammer' as cdlhammer,
                data_row->>'cdlhangingman' as cdlhangingman,
                data_row->>'cdlharami' as cdlharami,
                data_row->>'cdlharamicross' as cdlharamicross,
                data_row->>'cdlhighwave' as cdlhighwave,
                data_row->>'cdlhikkake' as cdlhikkake,
                data_row->>'cdlhikkakemod' as cdlhikkakemod,
                data_row->>'cdlhomingpigeon' as cdlhomingpigeon,
                data_row->>'cdlidentical3crows' as cdlidentical3crows,
                data_row->>'cdlinneck' as cdlinneck,
                data_row->>'cdlinvertedhammer' as cdlinvertedhammer,
                data_row->>'cdlkicking' as cdlkicking,
                data_row->>'cdlkickingbylength' as cdlkickingbylength,
                data_row->>'cdlladderbottom' as cdlladderbottom,
                data_row->>'cdllongleggeddoji' as cdllongleggeddoji,
                data_row->>'cdllongline' as cdllongline,
                data_row->>'cdlmarubozu' as cdlmarubozu,
                data_row->>'cdlshortline' as cdlshortline,
                data_row->>'cdlspinningtop' as cdlspinningtop,
                data_row->>'cdlstalledpattern' as cdlstalledpattern,
                data_row->>'cdlsticksandwich' as cdlsticksandwich,
                data_row->>'cdltakuri' as cdltakuri,
                data_row->>'cdltasukigap' as cdltasukigap,
                data_row->>'cdlthrusting' as cdlthrusting,
                data_row->>'cdltristar' as cdltristar,
                data_row->>'cdlunique3river' as cdlunique3river,
                data_row->>'cdlupsidegap2crows' as cdlupsidegap2crows,
                data_row->>'cdlxsidegap3methods' as cdlxsidegap3methods,
                data_row->>'price_on_time' AS price_on_time,
                data_row->>'price_after_15min' AS price_after_15min,
                data_row->>'price_after_30min' AS price_after_30min,
                data_row->>'price_after_1hour' AS price_after_1hour,
                data_row->>'price_after_4hour' AS price_after_4hour,
                data_row->>'price_after_12hour' AS price_after_12hour,
                data_row->>'price_after_1day' AS price_after_1day,
                data_row->>'price_after_2day' AS price_after_2day,
                data_row->>'price_after_3day' AS price_after_3day,
                data_row->>'price_after_4day' AS price_after_4day,
                data_row->>'price_after_5day' AS price_after_5day,
                data_row->>'price_after_6day' AS price_after_6day
            FROM
                {table_name} 
            WHERE ticker = '{ticker}' 
                AND tick_datetime BETWEEN '{start}' AND '{end}'
            ORDER BY
            tick_datetime DESC
            ;
        """
        return self.postgres.read_all(query) 
    
    def insert_upbit_transaction(self, table_name, ticker, tick_datetime, data_row):
        
        binds = [ticker, tick_datetime, data_row]
    
        query = f"""
        INSERT INTO public.{table_name}
            (seq, ticker, tick_datetime, data_row, reg_dt, mod_dt)
            VALUES(nextval('virtual_currency_upbit_transactions_2025_feature_seq_seq'::regclass), %s, %s, %s, now(), now());
        """ 
        res = self.postgres.execute_query_with_commit(query=query, binds=binds)
        
        return res
    
    def delete_upbit_transaction(self, table_name, ticker, tick_datetime):
        
        query = f"""
        DELETE FROM public.{table_name}
            WHERE ticker = '{ticker}'
            AND tick_datetime = '{tick_datetime}'
        """
        res = self.postgres.execute_query_with_commit(query)
        
        return res
    
    def delete_upbit_transaction_with_tick_datetime_list(self, table_name, ticker, tick_datetime_list):
        
        query = f"""
        DELETE FROM public.{table_name}
            WHERE ticker = '{ticker}'
        """
        where_clause = " AND tick_datetime IN ({})".format(','.join(f"'{item}'" for item in tick_datetime_list))
        query += where_clause
        
        res = self.postgres.execute_query_with_commit(query)
        
        return res
    
    """"""
    
    def create_yearly_table(self, year_list):
        """
        def description : 수집구간에 해당하는 연도별 테이블이 없으면 생성
        """
        
        for year in year_list:
            table_name_f, table_name_t = self.get_yearly_table_name(year)
            
            if self.is_exist_table(table_name_f) == False:
                self.create_upbit_transaction_table(table_name=table_name_f)
            
            if self.is_exist_table(table_name_t) == False:
                self.create_upbit_transaction_table(table_name=table_name_t)           
                
    def get_yearly_table_name(self, year):
        """
        def description : 피쳐, 타겟 테이블 명 조회
        """
        
        table_name_f = f"dataset_upbit_transaction_feature_{year}"
        table_name_t = f"dataset_upbit_transaction_target_{year}"
        
        return table_name_f, table_name_t
    