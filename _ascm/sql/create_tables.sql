-- public.reusable_data definition

-- Drop table

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

-- Table Triggers

-- CREATE TRIGGER reusable_data_trigger AFTER
-- INSERT
--     OR
-- UPDATE
--     ON
--     public.reusable_data FOR EACH ROW EXECUTE FUNCTION remove_old_reusable_data();

-- public.runnable_service_options definition

-- Drop table

DROP TABLE IF EXISTS public.runnable_service_options;

CREATE TABLE public.runnable_service_options (
	seq serial4 NOT NULL,
	option_key varchar(100) NOT NULL,
	option_val varchar(1000) NOT NULL,
	runnable_service_seq int4 NOT NULL,
	use_yn varchar(1) DEFAULT 'Y'::character varying NOT NULL,
	CONSTRAINT runnable_service_options_pkey PRIMARY KEY (seq)
);


-- public.runnable_services definition

-- Drop table

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
CREATE INDEX ix_runnable_services_execution_type ON public.runnable_services USING btree (execution_type);
CREATE INDEX ix_runnable_services_product_name ON public.runnable_services USING btree (product_name);