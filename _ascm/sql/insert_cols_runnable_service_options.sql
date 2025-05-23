DELETE FROM runnable_service_options;

INSERT INTO runnable_service_options (option_key,option_val,runnable_service_seq,use_yn) VALUES
	 ('dataset_table_prefix','dataset_upbit_transaction',11,'Y'),
	 ('model_config_path','/apps/scheduler/model_config/cv_ai_trainer_s1_gen02_config.yaml',11,'Y'),
	 ('ticker','KRW-BTC',11,'Y'),
	 ('dataset_load_term','210',11,'Y'),
	 ('auto_back_test_seq','12',11,'Y'),
	 ('auto_back_test','Y',11,'Y'),
	 ('scheduler_start_min','0',11,'Y'),
	 ('scheduler_start_hour','4',11,'Y'),
	 ('scheduler_start_day','1',11,'Y'),
	 ('dataset_table_prefix','dataset_upbit_transaction',10,'Y');
INSERT INTO runnable_service_options (option_key,option_val,runnable_service_seq,use_yn) VALUES
	 ('ticker_list','["KRW-BTC"]',10,'Y'),
	 ('dataset_generate_term','365',10,'Y'),
	 ('scheduler_start_min','0',10,'Y'),
	 ('scheduler_start_hour','1',10,'Y'),
	 ('ticker_list','["KRW-BTC"]',8,'Y'),
	 ('model_path_list','["models/2025/05/20/KRW-BTC_by_ontime_change_after_1hour_20250520_135740492406.h5", "models/2025/05/20/KRW-BTC_by_ontime_change_after_4hour_20250520_153010221724.h5", "models/2025/05/20/KRW-BTC_by_ontime_change_after_12hour_20250520_163413691088.h5", "models/2025/05/20/KRW-BTC_by_ontime_change_after_1day_20250520_173221533457.h5", "models/2025/05/20/KRW-BTC_by_prev_change_after_1hour_20250520_182558200578.h5", "models/2025/05/20/KRW-BTC_by_prev_change_after_4hour_20250520_202730446853.h5", "models/2025/05/20/KRW-BTC_by_prev_change_after_12hour_20250520_210646440154.h5", "models/2025/05/20/KRW-BTC_by_prev_change_after_1day_20250520_214651452340.h5"]',8,'Y'),
	 ('time_steps','40',8,'Y'),
	 ('col_f','["timestamp", "weekday", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "VOLUME_MA5", "VOLUME_MA20", "VOLUME_RATIO", "OBV", "VWAP", "VOLUME_VOLATILITY", "VOLUME_SPIKE", "RSI", "MACD", "MACD_SIGNAL", "BOLLINGER_PARTITION"]',8,'Y'),
	 ('auto_back_test_seq','8',7,'Y'),
	 ('auto_back_test','Y',7,'Y');
INSERT INTO runnable_service_options (option_key,option_val,runnable_service_seq,use_yn) VALUES
	 ('col_t','["by_ontime_change_after_1hour", "by_ontime_change_after_4hour", "by_ontime_change_after_12hour", "by_ontime_change_after_1day", "by_prev_change_after_1hour", "by_prev_change_after_4hour", "by_prev_change_after_12hour", "by_prev_change_after_1day"]',7,'Y'),
	 ('col_f','["timestamp", "weekday", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "VOLUME_MA5", "VOLUME_MA20", "VOLUME_RATIO", "OBV", "VWAP", "VOLUME_VOLATILITY", "VOLUME_SPIKE","RSI", "MACD", "MACD_SIGNAL", "BOLLINGER_PARTITION"]',7,'Y'),
	 ('scheduler_start_min','0',7,'Y'),
	 ('scheduler_start_hour','4',7,'Y'),
	 ('scheduler_start_day','1',7,'Y'),
	 ('ticker_list','["KRW-BTC"]',7,'Y'),
	 ('ticker_list','["KRW-BTC"]',7,'Y'),
	 ('early_stop','1',7,'Y'),
	 ('epochs','20',7,'Y'),
	 ('batch_size','32',7,'Y');
INSERT INTO runnable_service_options (option_key,option_val,runnable_service_seq,use_yn) VALUES
	 ('time_steps','40',7,'Y'),
	 ('dataset_load_term','730',7,'Y'),
	 ('scheduler_start_min','0',6,'Y'),
	 ('scheduler_start_hour','1',6,'Y'),
	 ('dataset_generate_term','730',6,'Y'),
	 ('ticker_list','["KRW-BTC"]',6,'Y'),
	 ('order_max','10000000',4,'Y'),
	 ('order_intensities','{"KRW-BTC" : {"ticker":"KRW-BTC", "order_percent_iv":1, "order_percent_ir":2, "order_hurdle_iv":1, "order_hurdle_ir":2, "order_reset_hours_if_stable":24}, "KRW-ETH" : {"ticker":"KRW-BTC", "order_percent_iv":1, "order_percent_ir":2, "order_hurdle_iv":1, "order_hurdle_ir":2, "order_reset_hours_if_stable":24}, "KRW-SOL" : {"ticker":"KRW-BTC", "order_percent_iv":1, "order_percent_ir":2, "order_hurdle_iv":1, "order_hurdle_ir":2, "order_reset_hours_if_stable":24}}',4,'Y'),
	 ('ttl_orderbook','1',3,'Y'),
	 ('ticker_list','["KRW-BTC", "KRW-ETH", "KRW-SOL"]',3,'Y');
