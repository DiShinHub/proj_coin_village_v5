from shares.modules.postgres import *

class TradeResultDao():
    """
    https://docs.upbit.com/kr/reference/%EC%A3%BC%EB%AC%B8%ED%95%98%EA%B8%B0
    """
    
    def __init__(self):
        self.postgres = Postgres()

    def insert_trade_result(self, 
            trade_exchange,
            trade_ticker,
            uuid,
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
        query = f"""
        INSERT INTO public.trade_result
        (trade_exchange, trade_ticker, "uuid", ord_type, price, reserved_fee, remaining_fee, paid_fee, state, "locked", executed_volume, order_dt, trade_dt, runnable_services_seq)
        VALUES(nextval('{trade_exchange}', '{trade_ticker}', '{uuid}', '{ord_type}', '{price}', {reserved_fee}, '{remaining_fee}', '{paid_fee}', '{state}', '{locked}', '{executed_volume}', '{order_dt}', '{trade_dt}', {runnable_services_seq});
        """
        return self.postgres.execute_query_with_commit(query) 