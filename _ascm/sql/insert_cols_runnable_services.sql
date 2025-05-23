DELETE FROM runnable_services;

INSERT INTO runnable_services (execution_type,execution_path,execution_class,execution_method,product_name,reg_dt,reg_member_seq,mod_dt,mod_member_seq,use_yn) VALUES
	 ('scheduler','scheduler.service.cv_ai_trainer_s1_gen02','CvAiTrainerS1Gen02','run','Queen Bee','2025-05-23 09:34:56.467044+09',0,'2025-05-23 09:34:56.467044+09',0,'N'),
	 ('scheduler','scheduler.service.cv_data_collector_s1_gen02','CvDataCollectorS1Gen02','run','Honey Bee','2025-05-22 11:34:13.66111+09',0,'2025-05-22 11:34:13.66111+09',0,'Y'),
	 ('task_worker','task_worker.service.cv_system_s1_gen01','CvSystemS1Gen01','run','Redis Cleaner','2025-05-07 14:58:32.567698+09',0,'2025-05-07 14:58:32.567698+09',0,'N'),
	 ('scheduler','scheduler.service.cv_ai_back_tester_s1_gen01','CvAiBackTesterS1Gen01','regist','Back Test Bee','2025-04-14 14:10:41.973+09',0,'2025-04-14 14:10:41.973+09',0,'N'),
	 ('scheduler','scheduler.service.cv_ai_trainer_s1_gen01','CvAiTrainerS1Gen01','regist','Queen Bee','2025-04-14 14:10:41.973+09',0,'2025-04-14 14:10:41.973+09',0,'N'),
	 ('scheduler','scheduler.service.cv_data_collector_s1_gen01','CvDataCollectorS1Gen01','regist','Honey Bee','2025-04-14 14:10:41.973619+09',0,'2025-04-14 14:10:41.973619+09',0,'N'),
	 ('task_worker','task_worker.service.cv_auto_trader_s3_gen01','CvAutoTraderS3Gen01','run','Highnoon Eagle','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('task_worker','task_worker.service.cv_auto_trader_s2_gen01','CvAutoTraderS2Gen01','run','Night Owl','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('task_worker','task_worker.service.cv_auto_trader_s1_gen01','CvAutoTraderS1Gen01','run','Orderbook Woodpecker','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N'),
	 ('task_worker','task_worker.service.cv_messenger_s1_gen01','CvMessengerS1Gen01','run','Baby Chick','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'Y');
INSERT INTO runnable_services (execution_type,execution_path,execution_class,execution_method,product_name,reg_dt,reg_member_seq,mod_dt,mod_member_seq,use_yn) VALUES
	 ('task_worker','task_worker.test.cv_test','Test','run','Doctor Fish','2025-04-08 13:44:54.629434+09',0,'2025-04-08 13:44:54.629434+09',0,'N');
