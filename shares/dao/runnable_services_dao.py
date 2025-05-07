from shares.modules.postgres import *

class runnableServicesDao():
    
    def __init__(self):
        self.postgres = Postgres()

    def get_runnable_services(self, execution_type):

        query = f"""
            SELECT
                seq,
                execution_type,
                execution_path,
                execution_class,
                execution_method,
                product_name,
                reg_dt,
                reg_member_seq,
                mod_dt,
                mod_member_seq,
                use_yn
            FROM
                runnable_services
            WHERE
                execution_type = '{execution_type}'
                AND use_yn = 'Y'
            ORDER BY
                seq ASC;
        """
        
        return self.postgres.read_all(query) 
    
    def get_runnable_service_options(self, runnable_service_seq):

        query = f"""
            SELECT
                seq,
                option_key,
                option_val,
                runnable_service_seq 
            FROM
                runnable_service_options
            WHERE 
                runnable_service_seq = {runnable_service_seq}
                AND use_yn = 'Y' 
            ORDER BY
                seq ASC;
        """
        
        return self.postgres.read_all(query) 
    
    def update_runnable_services(self, params, seq):
        
        # base query
        query = f"""
            UPDATE runnable_services SET
        """
        
        # set query
        set_cluase = ""
        for key, val in params.items():
            set_cluase = f""" {key} = '{val}',"""
        if not set_cluase:
            raise Exception("no params found")
        
        set_cluase = set_cluase[:-1]
        
        # where query
        where_cluase = f" WHERE seq = {seq}"
        
        # bind
        query += set_cluase
        query += where_cluase
        
        # execute
        res = self.postgres.execute_query_with_commit(query)
        return res