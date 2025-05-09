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
        
        query = f"""
            CREATE INDEX ix_{table_name}_ticker ON public.{table_name} (ticker);
            CREATE INDEX ix_{table_name}_tick_datetime ON public.{table_name} (tick_datetime);
        """
        self.postgres.execute_query_with_commit(query)
        
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
    
    def get_upbit_transactions_between(self, table_name_f, table_name_t, ticker, start, end):
        
        query = f"""
            SELECT
            f.seq AS feature_seq,
            f.ticker,
            f.tick_datetime AS "tick_datetime_",
            f.data_row->>'tick_datetime' AS "tick_datetime",
  	        f.data_row->>'timestamp' AS timestamp,
            f.data_row->>'weekday' AS "weekday",
            f.data_row->>'OPEN' AS "OPEN",
            f.data_row->>'HIGH' AS "HIGH",
            f.data_row->>'LOW' AS "LOW",
            f.data_row->>'CLOSE' AS "CLOSE",
            f.data_row->>'VOLUME' AS "VOLUME",
            f.data_row->>'VOLUME_MA5' AS "VOLUME_MA5",
            f.data_row->>'VOLUME_MA20' AS "VOLUME_MA20",
            f.data_row->>'VOLUME_RATIO' AS "VOLUME_RATIO",
            f.data_row->>'OBV' AS "OBV",
            f.data_row->>'VWAP' AS "VWAP",
            f.data_row->>'VOLUME_VOLATILITY' AS "VOLUME_VOLATILITY",
            f.data_row->>'VOLUME_SPIKE' AS "VOLUME_SPIKE",
            f.data_row->>'RSI' AS "RSI",
            f.data_row->>'MACD' AS "MACD",
            f.data_row->>'MACD_SIGNAL' AS "MACD_SIGNAL",
            f.data_row->>'BOLLINGER_PARTITION' AS "BOLLINGER_PARTITION",
            f.data_row->>'CLOSE_LIST' AS "CLOSE_LIST",

            t.data_row->'by_prev'->>'price_after_15min' AS "by_prev_price_after_15min",
            t.data_row->'by_prev'->>'price_after_30min' AS "by_prev_price_after_30min",
            t.data_row->'by_prev'->>'price_after_1hour' AS "by_prev_price_after_1hour",
            t.data_row->'by_prev'->>'price_after_4hour' AS "by_prev_price_after_4hour",
            t.data_row->'by_prev'->>'price_after_12hour' AS "by_prev_price_after_12hour",
            t.data_row->'by_prev'->>'price_after_1day' AS "by_prev_price_after_1day",
            t.data_row->'by_prev'->>'price_after_2day' AS "by_prev_price_after_2day",
            t.data_row->'by_prev'->>'price_after_3day' AS "by_prev_price_after_3day",
            t.data_row->'by_prev'->>'price_after_4day' AS "by_prev_price_after_4day",
            t.data_row->'by_prev'->>'price_after_5day' AS "by_prev_price_after_5day",
            t.data_row->'by_prev'->>'price_after_6day' AS "by_prev_price_after_6day",
            t.data_row->'by_prev'->>'change_after_15min' AS "by_prev_change_after_15min",
            t.data_row->'by_prev'->>'change_after_30min' AS "by_prev_change_after_30min",
            t.data_row->'by_prev'->>'change_after_1hour' AS "by_prev_change_after_1hour",
            t.data_row->'by_prev'->>'change_after_4hour' AS "by_prev_change_after_4hour",
            t.data_row->'by_prev'->>'change_after_12hour' AS "by_prev_change_after_12hour",
            t.data_row->'by_prev'->>'change_after_1day' AS "by_prev_change_after_1day",
            t.data_row->'by_prev'->>'change_after_2day' AS "by_prev_change_after_2day",
            t.data_row->'by_prev'->>'change_after_3day' AS "by_prev_change_after_3day",
            t.data_row->'by_prev'->>'change_after_4day' AS "by_prev_change_after_4day",
            t.data_row->'by_prev'->>'change_after_5day' AS "by_prev_change_after_5day",
            t.data_row->'by_prev'->>'change_after_6day' AS "by_prev_change_after_6day",

            t.data_row->'by_ontime'->>'price_after_15min' AS "by_ontime_price_after_15min",
            t.data_row->'by_ontime'->>'price_after_30min' AS "by_ontime_price_after_30min",
            t.data_row->'by_ontime'->>'price_after_1hour' AS "by_ontime_price_after_1hour",
            t.data_row->'by_ontime'->>'price_after_4hour' AS "by_ontime_price_after_4hour",
            t.data_row->'by_ontime'->>'price_after_12hour' AS "by_ontime_price_after_12hour",
            t.data_row->'by_ontime'->>'price_after_1day' AS "by_ontime_price_after_1day",
            t.data_row->'by_ontime'->>'price_after_2day' AS "by_ontime_price_after_2day",
            t.data_row->'by_ontime'->>'price_after_3day' AS "by_ontime_price_after_3day",
            t.data_row->'by_ontime'->>'price_after_4day' AS "by_ontime_price_after_4day",
            t.data_row->'by_ontime'->>'price_after_5day' AS "by_ontime_price_after_5day",
            t.data_row->'by_ontime'->>'price_after_6day' AS "by_ontime_price_after_6day",
            t.data_row->'by_ontime'->>'change_after_15min' AS "by_ontime_change_after_15min",
            t.data_row->'by_ontime'->>'change_after_30min' AS "by_ontime_change_after_30min",
            t.data_row->'by_ontime'->>'change_after_1hour' AS "by_ontime_change_after_1hour",
            t.data_row->'by_ontime'->>'change_after_4hour' AS "by_ontime_change_after_4hour",
            t.data_row->'by_ontime'->>'change_after_12hour' AS "by_ontime_change_after_12hour",
            t.data_row->'by_ontime'->>'change_after_1day' AS "by_ontime_change_after_1day",
            t.data_row->'by_ontime'->>'change_after_2day' AS "by_ontime_change_after_2day",
            t.data_row->'by_ontime'->>'change_after_3day' AS "by_ontime_change_after_3day",
            t.data_row->'by_ontime'->>'change_after_4day' AS "by_ontime_change_after_4day",
            t.data_row->'by_ontime'->>'change_after_5day' AS "by_ontime_change_after_5day",
            t.data_row->'by_ontime'->>'change_after_6day' AS "by_ontime_change_after_6day"

            FROM
                {table_name_f} f
            JOIN
                {table_name_t} t
            ON
                f.ticker = t.ticker AND f.tick_datetime = t.tick_datetime
            WHERE f.ticker = '{ticker}' 
                AND f.tick_datetime BETWEEN '{start}' AND '{end}'
            ORDER BY
            f.tick_datetime DESC
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