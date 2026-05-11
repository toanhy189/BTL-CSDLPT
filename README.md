# BTL CSDLPT - Dang Ky Hoc Phan

## Mo hinh PostgreSQL phan tan

Project dung 5 container PostgreSQL rieng, moi container la mot server/site:

| Site | Container | Database | Port |
| --- | --- | --- | --- |
| Hoa Lac | `postgres_hoalac` | `site_hoalac` | `5440` |
| Ngoc Truc | `postgres_ngoctruc` | `site_ngoctruc` | `5441` |
| Ha Dong | `postgres_hadong` | `site_hadong` | `5442` |
| Cau Giay | `postgres_caugiay` | `site_caugiay` | `5443` |
| HCM | `postgres_hcm` | `site_hcm` | `5444` |

Username: `postgres`

Password: `toantk178@`

## Chay Docker

```powershell
docker compose up -d
docker ps
```

## Thu tu chay SQL

Moi server/site deu chay:

1. `sql/01_create_tables.sql`
2. `sql/02_insert_common_data.sql`
3. File insert rieng cua site do:

| Site | File SQL rieng |
| --- | --- |
| Hoa Lac | `sql/03_insert_site_hoalac.sql` |
| Ngoc Truc | `sql/04_insert_site_ngoctruc.sql` |
| Ha Dong | `sql/05_insert_site_hadong.sql` |
| Cau Giay | `sql/06_insert_site_caugiay.sql` |
| HCM | `sql/07_insert_site_hcm.sql` |

Khong can `sql/init.sql` nua vi Docker Compose da tu tao database chinh qua `POSTGRES_DB`.
