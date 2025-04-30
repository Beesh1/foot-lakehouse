# Foot Lakehouse

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/foot-lakehouse)

Foot Lakehouse is a lightweight data ingestion and storage solution designed for real-time data processing and backup. It uses SQLite as the primary database, MinIO for S3-compatible storage, and Litestream for continuous database replication, ensuring data durability. The project is ideal for small-scale applications needing efficient data ingestion with reliable backups.

## Features
- **Real-Time Data Ingestion**: Accepts data via HTTP webhooks and stores it in a SQLite database.
- **Continuous Backup**: Uses Litestream to replicate the SQLite database to MinIO (or any S3-compatible storage) in near real-time.
- **Lightweight**: Minimal resource usage, perfect for local servers or low-traffic applications.
- **Dockerized**: Fully containerized setup using Docker Compose for easy deployment.

## Architecture
The project consists of four services:
1. **Webhook Service**: A Python-based service that listens for HTTP requests and stores data in SQLite.
2. **Litestream Service**: Continuously replicates the SQLite database to MinIO for backup.
3. **MinIO Service**: S3-compatible object storage for storing database backups.
4. **MinIO Initialization Service**: Sets up the MinIO bucket for backups.

## Prerequisites
- **Docker**: Ensure Docker and Docker Compose are installed.
- **Port Availability**: Ports `8000`, `9000`, and `9001` must be free on your host machine.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/foot-lakehouse.git
   cd foot-lakehouse
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=minioadmin123
   ```
   Replace the credentials with secure values for production.

3. **Start the Services**:
   ```bash
   docker-compose up -d
   ```
   This will start all services and initialize the MinIO bucket.

4. **Verify the Setup**:
   - Check service status:
     ```bash
     docker-compose ps
     ```
   - Confirm Litestream replication:
     ```bash
     docker logs foot-lakehouse-litestream-1
     ```
     Look for messages like `snapshot written` and `wal segment written`.
   - Access the MinIO console at `http://localhost:9001` (login: `minioadmin`/`minioadmin123`) to verify backups in the `lakehouse` bucket.

## Usage
### Sending Data
The `webhook` service listens for HTTP POST requests on `http://localhost:8000`. Send data using `curl` or any HTTP client:
```bash
curl -X POST http://localhost:8000 -d '{"key": "value"}'
```
The data will be stored in the SQLite database (`/app/data/foot_sqlite.db`) and replicated to MinIO.

### Monitoring Backups
Litestream replicates the database to MinIO every 1 second. Check the replication logs:
```bash
docker logs -f foot-lakehouse-litestream-1
```

### Accessing Data
- **SQLite Database**: Access the database via the `webhook` container:
  ```bash
  docker exec -it foot-lakehouse-webhook-1 sqlite3 /app/data/foot_sqlite.db
  ```
- **MinIO Backups**: View backups in the MinIO console (`http://localhost:9001`) or programmatically via an S3 client.

## Configuration
### Adjusting Backup Frequency
Modify the `sync-interval` in `litestream.yml` to change how often Litestream replicates to MinIO. For example, to sync every 5 minutes:
```yaml
sync-interval: 300s
```

### Using Cloud Storage (e.g., AWS S3)
To back up to AWS S3 instead of MinIO, update `.env` with your S3 credentials:
```env
MINIO_ROOT_USER=<your-aws-access-key>
MINIO_ROOT_PASSWORD=<your-aws-secret-key>
```
Then update `litestream.yml`:
```yaml
dbs:
  - path: /app/data/foot_sqlite.db
    replicas:
      - type: s3
        bucket: <your-s3-bucket-name>
        path: db/foot_sqlite.db
        endpoint: s3.amazonaws.com
        access-key-id: ${MINIO_ROOT_USER}
        secret-access-key: ${MINIO_ROOT_PASSWORD}
        region: us-east-1
        sync-interval: 1s
```

## Troubleshooting
- **Litestream Fails to Replicate**:
  - Check logs: `docker logs foot-lakehouse-litestream-1`.
  - Ensure MinIO is running and credentials are correct in `.env`.
- **Webhook Not Responding**:
  - Check logs: `docker logs foot-lakehouse-webhook-1`.
  - Verify the health endpoint: `curl http://localhost:8000/health`.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or support, please open an issue or reach out to [your email or contact info].