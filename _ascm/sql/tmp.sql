PS C:\Users\aizen> docker ps
CONTAINER ID   IMAGE                   COMMAND                   CREATED       STATUS              PORTS                              NAMES
7332a9797e74   minio/minio:latest      "/usr/bin/docker-ent…"   3 weeks ago   Up 6 minutes        0.0.0.0:9000-9001->9000-9001/tcp   CV-object-storage-minio-compose
a77ed30bd4e9   redis:5.0.7             "docker-entrypoint.s…"   3 weeks ago   Up 6 minutes        0.0.0.0:6379->6379/tcp             CV-redis-compose
42ed589b5e9a   ghcr.io/mlflow/mlflow   "mlflow server --bac…"   3 weeks ago   Up About a minute   0.0.0.0:5000->5000/tcp             CV-db-mlflow-compose
4c3a6de1e2fa   postgres:14.6-alpine    "docker-entrypoint.s…"   3 weeks ago   Up 6 minutes        0.0.0.0:5432->5432/tcp             CV-db-postgres-compose
PS C:\Users\aizen> docker exec -it CV-db-postgres-compose psql -U postgres
psql (14.6)
Type "help" for help.

postgres=# CREATE DATABASE mlflow;
CREATE DATABASE
postgres=# CREATE USER mlflow_user WITH PASSWORD 'mlflow_pass';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow_user;
GRANT
postgres=# \q
