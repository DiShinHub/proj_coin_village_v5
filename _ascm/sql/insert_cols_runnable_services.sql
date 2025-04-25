DELETE FROM runnable_services;

INSERT INTO runnable_services (execution_type,execution_path,execution_class,execution_method,product_name,reg_dt,reg_member_seq,mod_dt,mod_member_seq,use_yn) VALUES
	 ('task_worker','task_worker.test.cv_test','Test','run','Doctor Fish','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('task_worker','task_worker.service.cv_messenger_s1_gen01','CvMessengerS1Gen01','run','Baby Chick','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('task_worker','task_worker.service.cv_auto_trader_s1_gen01','CvAutoTraderS1Gen01','run','Orderbook Woodpecker','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('task_worker','task_worker.service.cv_auto_trader_s2_gen01','CvAutoTraderS2Gen01','run','Night Owl','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('task_worker','task_worker.service.cv_auto_trader_s3_gen01','CvAutoTraderS3Gen01','run','Highnoon Eagle','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('scheduler','scheduler.service.cv_data_collector_s1_gen01','CvDataCollectorS1Gen01','regist','Honey Bee','2025-04-14 14:10:41.973619+09',0,'2025-04-14 14:10:41.973619+09',0,'N'),
	 ('scheduler','scheduler.service.cv_ai_trainer_s1_gen01','CvAiTrainerS1Gen01','regist','King Bee','2025-04-14 14:10:41.973+09',0,'2025-04-14 14:10:41.973+09',0,'N');
