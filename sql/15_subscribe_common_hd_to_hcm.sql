DROP SUBSCRIPTION IF EXISTS sub_common_data_hd_to_hcm;

CREATE SUBSCRIPTION sub_common_data_hd_to_hcm
CONNECTION 'host=postgres_hadong port=5432 dbname=site_hadong user=replicator password=replica123'
PUBLICATION pub_common_data
WITH (copy_data = false);
