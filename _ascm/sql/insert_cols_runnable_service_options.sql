DELETE FROM runnable_service_options;

INSERT INTO runnable_service_options (option_key,option_val,runnable_service_seq,use_yn) VALUES
	 ('ttl_orderbook','1',3,'Y'),
	 ('ticker_list','["KRW-BTC"]',3,'Y'),
	 ('order_max','10000000',4,'Y'),
	 ('order_intensities','{"KRW-BTC" : {"ticker":"KRW-BTC", "order_percent_iv":1, "order_percent_ir":2, "order_hurdle_iv":1, "order_hurdle_ir":2, "order_reset_hours_if_stable":24}, "KRW-ETH" : {"ticker":"KRW-BTC", "order_percent_iv":1, "order_percent_ir":2, "order_hurdle_iv":1, "order_hurdle_ir":2, "order_reset_hours_if_stable":24}, "KRW-SOL" : {"ticker":"KRW-BTC", "order_percent_iv":1, "order_percent_ir":2, "order_hurdle_iv":1, "order_hurdle_ir":2, "order_reset_hours_if_stable":24}}',4,'Y'),
	 ('scheduler_start_hour','1',6,'Y'),
	 ('scheduler_start_min','0',6,'Y'),
	 ('dataset_generate_term','90',6,'Y'),
	 ('ticker_list','["KRW-BTC"]',6,'Y'),
	 ('scheduler_start_day','1',7,'Y'),
	 ('scheduler_start_hour','4',7,'Y'),
	 ('scheduler_start_min','0',7,'Y'),
	 ('auth_back_test','Y',7,'Y'),
	 ('auth_back_test_seq',8,7,'Y'),
	 ('dataset_load_term',90,7,'Y'),
	 ('ticker_list','["KRW-BTC"]',7,'Y'),
	 ('col_f','["timestamp", "weekday", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "VOLUME_MA5", "VOLUME_MA20", "VOLUME_RATIO", "OBV", "VWAP", "VOLUME_VOLATILITY", "VOLUME_SPIKE","RSI", "MACD", "MACD_SIGNAL", "BOLLINGER_PARTITION"]',7,'Y'),
	 ('col_t','["by_ontime_change_after_15min", "by_ontime_change_after_30min", "by_ontime_change_after_1hour", "by_ontime_change_after_4hour", "by_ontime_change_after_12hour", "by_ontime_change_after_1day", "by_prev_change_after_15min", "by_prev_change_after_30min", "by_prev_change_after_1hour", "by_prev_change_after_4hour", "by_prev_change_after_12hour", "by_prev_change_after_1day"]',7,'Y')
	 ('time_steps',40,7,'Y'),
	 ('batch_size',32,7,'Y'),
	 ('epochs',20,7,'Y'),
	 ('early_stop',1,7,'Y');


