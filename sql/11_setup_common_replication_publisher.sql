DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'replicator') THEN
        CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'replica123';
    ELSE
        ALTER ROLE replicator WITH LOGIN REPLICATION PASSWORD 'replica123';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE site_hadong TO replicator;
GRANT USAGE ON SCHEMA public TO replicator;
GRANT SELECT ON TABLE coso, khoa, hocphan, chuongtrinhdaotao, dotdangky TO replicator;

DROP PUBLICATION IF EXISTS pub_common_data;

CREATE PUBLICATION pub_common_data
FOR TABLE coso, khoa, hocphan, chuongtrinhdaotao, dotdangky;
