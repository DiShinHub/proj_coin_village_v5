from shares.modules.postgres import *

class runnableServicesDao():
    
    def __init__(self):
        self.postgres = Postgres()

    """
    runnable_service
    """
    def get_runnable_services(self):

        query = f"""
            SELECT
                seq,
                execution_path,
                execution_class,
                execution_method,
                product_name,
                reg_dt,
                reg_member_seq,
                mod_dt,
                mod_member_seq,
                activate_yn
            FROM
                runnable_services
            WHERE
                activate_yn = 'Y'
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
    
    """
    runnable_service_option
    """
    def get_runnable_service_option(self, seq=None, option_key=None, option_val=None,runnable_service_seq=None):
        
        where_cluase = f"WHERE activate_yn = 'Y'"
        if seq:
            where_cluase += f" AND seq = {seq}"
        
        if option_key:
            where_cluase += f" AND option_key = '{option_key}'"
        
        if option_val:
            where_cluase += f" AND option_val = '{option_val}'"
        
        if runnable_service_seq:
            where_cluase += f" AND runnable_service_seq = {runnable_service_seq}"
        
        query = f"""
            SELECT
                seq,
                option_key,
                option_val,
                runnable_service_seq 
            FROM
                runnable_service_options
            {where_cluase};
        """
        return self.postgres.read_one(query) 
    
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
                AND activate_yn = 'Y' 
            ORDER BY
                seq ASC;
        """
        return self.postgres.read_all(query) 

    def upsert_runnable_service_options(self, option_key, option_val, runnable_service_seq):
        
        runnable_service_options = self.get_runnable_service_option(
            runnable_service_seq=runnable_service_seq, 
            option_key=option_key
        )
        if not runnable_service_options:
            return self.insert_runnable_service_option(option_key, option_val, runnable_service_seq)
        
        else:
            return self.update_runnable_service_option_val_by_option_key(option_key, option_val, runnable_service_seq)
    
    def insert_runnable_service_option(self, option_key, option_val, runnable_service_seq):
    
        query = f"""
            INSERT INTO public.runnable_service_options
                (seq, option_key, option_val, runnable_service_seq, activate_yn)
                VALUES(nextval('runnable_service_options_seq_seq'::regclass), '{option_key}', '{option_val}', {runnable_service_seq}, 'Y');
        """ 
        
        return self.postgres.execute_query_with_commit(query) 
        
    def update_runnable_service_option_val_by_option_key(self, option_key, option_val, runnable_service_seq):
        
        query = f"""
            UPDATE runnable_service_options SET
        """
        
        # set query
        set_cluase = f""" option_val = '{option_val}'"""
        
        # where query
        where_cluase = f" WHERE option_key = '{option_key}' AND runnable_service_seq = {runnable_service_seq}"
        
        # bind
        query += set_cluase
        query += where_cluase
        
        return self.postgres.execute_query_with_commit(query) 