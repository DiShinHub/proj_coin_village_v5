from shares.modules.postgres import *

class ResultDao():
    
    def __init__(self):
        self.postgres = Postgres()
    
    def insert_trade_result(self, 
            trade_exchange,
            trade_ticker,
            uuid,
            ord_side,
            ord_type,
            price,
            reserved_fee,
            remaining_fee,
            paid_fee,
            state,
            locked,
            executed_volume,
            order_dt,
            trade_dt,
            runnable_services_seq
        ):
        """
        https://docs.upbit.com/kr/reference/%EC%A3%BC%EB%AC%B8%ED%95%98%EA%B8%B0
        """
    
        query = f"""
        INSERT INTO public.trade_result
        (trade_exchange, trade_ticker, "uuid", ord_side, ord_type, price, reserved_fee, remaining_fee, paid_fee, state, "locked", executed_volume, order_dt, trade_dt, runnable_services_seq)
        VALUES('{trade_exchange}', '{trade_ticker}', '{uuid}', '{ord_side}','{ord_type}', '{price}', {reserved_fee}, '{remaining_fee}', '{paid_fee}', '{state}', '{locked}', '{executed_volume}', '{order_dt}', '{trade_dt}', {runnable_services_seq});
        """
        return self.postgres.execute_query_with_commit(query) 

    def ai_train_result(self, 
            experiment_id,
            run_id,
            minio_path,
            train_start_dt,
            train_end_dt,
            runnable_services_seq
        ):
        binds = [experiment_id, run_id, minio_path, train_start_dt, train_end_dt, runnable_services_seq]
    
        query = f"""
        INSERT INTO public.ai_train_result
        (experiment_id, run_id, minio_path, train_start_dt, train_end_dt, runnable_services_seq)
        VALUES(%s, %s, %s, %s, %s, %s);
        """
        res = self.postgres.execute_query_with_commit(query=query, binds=binds)
        return res

    def insert_ai_back_test_result(self, 
            ticker,
            model_path,
            result_row,
            hit_yn,
            runnable_services_seq,
            reg_member_seq
        ):
        binds = [ticker, model_path, result_row, hit_yn, runnable_services_seq]
    
        query = f"""
        INSERT INTO public.ai_back_test_result
        (ticker, model_path, result_row, hit_yn, runnable_services_seq, reg_dt, reg_member_seq)
        VALUES(%s, %s, %s, %s, %s, now(), {reg_member_seq});
        """
        res = self.postgres.execute_query_with_commit(query=query, binds=binds)
        return res