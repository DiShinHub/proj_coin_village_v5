from shares.modules.postgres import *

class AiBackTestResultDao():
    
    def __init__(self):
        self.postgres = Postgres()

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
    
    