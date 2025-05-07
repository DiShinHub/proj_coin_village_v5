from shares.modules.postgres import *

class AiBackTestResultDao():
    
    def __init__(self):
        self.postgres = Postgres()

    def insert_ai_back_test_result(self, 
            ticker,
            model_path,
            interval,
            prediction,
            real,
            hit_yn,
            back_test_start_dt,
            back_test_end_dt,
            runnable_services_seq
        ):

        query = f"""
        INSERT INTO public.ai_back_test_result
        (ticker, model_path, "interval", prediction, "real", hit_yn, back_test_start_dt, back_test_end_dt, runnable_services_seq)
        (trade_exchange, trade_ticker, "uuid", ord_side, ord_type, price, reserved_fee, remaining_fee, paid_fee, state, "locked", executed_volume, order_dt, trade_dt, runnable_services_seq)
        VALUES('{ticker}', '{model_path}', '{interval}', '{prediction}', '{real}', '{hit_yn}', '{back_test_start_dt}', '{back_test_end_dt}', {runnable_services_seq});
        """
        return self.postgres.execute_query_with_commit(query) 