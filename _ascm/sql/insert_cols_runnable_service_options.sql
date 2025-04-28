DELETE FROM runnable_service_options;

INSERT INTO runnable_service_options (option_key,option_val,runnable_service_seq,use_yn) VALUES
	 ('ttl_orderbook','1',3,'Y'),
	 ('ticker_list','["KRW-BTC", "KRW-ETH", "KRW-SOL"]',3,'Y'),
	 ('order_max','10000000',4,'Y'),
	 ('order_intensities','[{"ticker":"KRW-BTC","order_percent_iv":1,"order_percent_ir":2,"order_hurdle_iv":1,"order_hurdle_ir":2},{"ticker":"KRW-ETH","order_percent_iv":1,"order_percent_ir":2,"order_hurdle_iv":1,"order_hurdle_ir":2},{"ticker":"KRW-SOL","order_percent_iv":1,"order_percent_ir":2,"order_hurdle_iv":1,"order_hurdle_ir":2}]',4,'Y'),
	 ('dataset_generate_term','90',6,'Y'),
	 ('scheduler_start_hour','1',6,'Y'),
	 ('scheduler_start_min','0',6,'Y'),
	 ('ticker_list','["KRW-BTC", "KRW-ETH", "KRW-SOL"]',6,'Y'),
	 ('ticker_list','["KRW-BTC"]',7,'Y'),
	 ('dataset_load_term',90,7,'Y'),
	 ('time_steps',40,7,'Y'),
	 ('batch_size',32,7,'Y'),
	 ('epochs',20,7,'Y'),
	 ('early_stop',1,7,'Y'),
	 ('model_folder_path','',8,'Y')
	 ;
