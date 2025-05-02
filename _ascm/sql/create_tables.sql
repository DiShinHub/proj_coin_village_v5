-- public.runnable_services 
DROP TABLE IF EXISTS public.runnable_services;
CREATE TABLE public.runnable_services (
	seq serial4 NOT NULL,
	execution_type varchar(100) NOT NULL,
	execution_path varchar(255) NOT NULL,
	execution_class varchar(255) NOT NULL,
	execution_method varchar(255) NOT NULL,
	product_name varchar(100) NOT NULL,
	reg_dt timestamptz NULL,
	reg_member_seq int4 NOT NULL,
	mod_dt timestamptz NULL,
	mod_member_seq int4 NOT NULL,
	use_yn varchar(1) DEFAULT 'Y'::character varying NOT NULL,
	CONSTRAINT runnable_services_pkey PRIMARY KEY (seq),
	CONSTRAINT ux_runnable_service_execution_path UNIQUE (execution_path)
);
CREATE INDEX ix_runnable_services_execution_type ON public.runnable_services (execution_type);
CREATE INDEX ix_runnable_services_product_name ON public.runnable_services (product_name);

-- public.runnable_service_options 
DROP TABLE IF EXISTS public.runnable_service_options;
CREATE TABLE public.runnable_service_options (
	seq serial4 NOT NULL,
	option_key varchar(100) NOT NULL,
	option_val varchar(1000) NOT NULL,
	runnable_service_seq int4 NOT NULL,
	use_yn varchar(1) DEFAULT 'Y'::character varying NOT NULL,
	CONSTRAINT runnable_service_options_pkey PRIMARY KEY (seq)
);

-- public.reusable_data 
DROP TABLE IF EXISTS public.reusable_data;
CREATE TABLE public.reusable_data (
	seq serial4 NOT NULL,
	"key" varchar(1000) NOT NULL,
	value varchar(1000) NOT NULL,
	reg_dt timestamptz NULL,
	use_dt timestamptz NULL,
	CONSTRAINT reusable_data_pkey PRIMARY KEY (seq),
	CONSTRAINT ux_reusable_data_key UNIQUE (key)
);
CREATE INDEX ix_reusable_data_key ON public.reusable_data USING btree (key);

CREATE FUNCTION remove_old_reusable_data()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM reusable_data WHERE use_dt < NOW() - INTERVAL '6 month';
    RETURN NEW;
END;
$$;

CREATE TRIGGER reusable_data_trigger
AFTER INSERT OR UPDATE ON reusable_data
FOR EACH ROW
EXECUTE FUNCTION remove_old_reusable_data();

-- public.trade_result 
DROP TABLE IF EXISTS public.trade_result;
CREATE TABLE public.trade_result (
	seq serial4 NOT NULL,
	trade_exchange varchar(100) NOT NULL,
	trade_ticker varchar(100) NOT NULL,
	uuid varchar(100) NOT NULL,
	ord_side varchar(100) NOT NULL,
	ord_type varchar(100) NOT NULL,
	price varchar(100) NOT NULL,
	reserved_fee varchar(100) NOT NULL,
	remaining_fee varchar(100) NOT NULL,
	paid_fee varchar(100) NOT NULL,
	state varchar(100) NOT NULL,
	locked varchar(100) NOT NULL,
	executed_volume varchar(100) NOT NULL,
	order_dt timestamptz NULL,
	trade_dt varchar(100) NULL,
	runnable_services_seq int NOT NULL,
	CONSTRAINT trade_result_pkey PRIMARY KEY (seq)
);
CREATE INDEX ix_trade_result_trade_exchange ON public.trade_result (trade_exchange);
CREATE INDEX ix_trade_result_trade_ticker ON public.trade_result (trade_ticker);
CREATE INDEX ix_trade_result_uuid ON public.trade_result (uuid);

CREATE FUNCTION remove_old_trade_result()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM trade_result WHERE order_dt < NOW() - INTERVAL '12 month';
    RETURN NEW;
END;
$$;

CREATE TRIGGER trade_result_trigger
AFTER INSERT OR UPDATE ON trade_result
FOR EACH ROW
EXECUTE FUNCTION remove_old_trade_result();