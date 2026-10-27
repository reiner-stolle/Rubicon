CREATE OR REPLACE TABLE customer AS
SELECT *
FROM read_csv(
    '/home/stolle/ssb_sf1/customer.tbl',
    delim='|',
    header=false,
    columns={
        'c_custkey':'INTEGER',
        'c_name':'VARCHAR',
        'c_address':'VARCHAR',
        'c_city':'VARCHAR',
        'c_nation':'VARCHAR',
        'c_region':'VARCHAR',
        'c_phone':'VARCHAR',
        'c_mktsegment':'VARCHAR'
    }
);

CREATE OR REPLACE TABLE supplier AS
SELECT *
FROM read_csv(
    '/home/stolle/ssb_sf1/supplier.tbl',
    delim='|',
    header=false,
    columns={
        's_suppkey':'INTEGER',
        's_name':'VARCHAR',
        's_address':'VARCHAR',
        's_city':'VARCHAR',
        's_nation':'VARCHAR',
        's_region':'VARCHAR',
        's_phone':'VARCHAR'
    }
);

CREATE OR REPLACE TABLE part AS
SELECT *
FROM read_csv(
    '/home/stolle/ssb_sf1/part.tbl',
    delim='|',
    header=false,
    columns={
        'p_partkey':'INTEGER',
        'p_name':'VARCHAR',
        'p_mfgr':'VARCHAR',
        'p_category':'VARCHAR',
        'p_brand1':'VARCHAR',
        'p_color':'VARCHAR',
        'p_type':'VARCHAR',
        'p_size':'INTEGER',
        'p_container':'VARCHAR'
    }
);

CREATE OR REPLACE TABLE dim_date AS
SELECT *
FROM read_csv(
    '/home/stolle/ssb_sf1/date.tbl',
    delim='|',
    header=false,
    columns={
        'd_datekey':'INTEGER',
        'd_date':'VARCHAR',
        'd_dayofweek':'VARCHAR',
        'd_month':'VARCHAR',
        'd_year':'INTEGER',
        'd_yearmonthnum':'INTEGER',
        'd_yearmonth':'VARCHAR',
        'd_daynuminweek':'INTEGER',
        'd_daynuminmonth':'INTEGER',
        'd_daynuminyear':'INTEGER',
        'd_monthnuminyear':'INTEGER',
        'd_weeknuminyear':'INTEGER',
        'd_sellingseason':'VARCHAR',
        'd_lastdayinweekfl':'INTEGER',
        'd_lastdayinmonthfl':'INTEGER',
        'd_holidayfl':'INTEGER',
        'd_weekdayfl':'INTEGER'
    }
);

CREATE OR REPLACE TABLE lineorder AS
SELECT *
FROM read_csv(
    '/home/stolle/ssb_sf1/lineorder.tbl',
    delim='|',
    header=false,
    columns={
        'lo_orderkey':'INTEGER',
        'lo_linenumber':'INTEGER',
        'lo_custkey':'INTEGER',
        'lo_partkey':'INTEGER',
        'lo_suppkey':'INTEGER',
        'lo_orderdate':'INTEGER',
        'lo_orderpriority':'VARCHAR',
        'lo_shippriority':'INTEGER',
        'lo_quantity':'INTEGER',
        'lo_extendedprice':'BIGINT',
        'lo_ordtotalprice':'BIGINT',
        'lo_discount':'INTEGER',
        'lo_revenue':'BIGINT',
        'lo_supplycost':'BIGINT',
        'lo_tax':'INTEGER',
        'lo_commitdate':'INTEGER',
        'lo_shipmode':'VARCHAR'
    }
);
