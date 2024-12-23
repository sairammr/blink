use rusqlite::{params, Connection};
use r2d2::Pool;
use r2d2_sqlite::SqliteConnectionManager;
use chrono::NaiveDateTime;

#[derive(Debug)]
pub struct LogEntry {
    pub message: String,
    pub timestamp: NaiveDateTime,
}

#[derive(Debug)]
pub struct IntervalEntry {
    pub timestamp: NaiveDateTime,
    pub blink_count: i32,
}

#[derive(Debug)]
pub struct AvgEntry {
    pub timestamp: NaiveDateTime,
    pub avg_value: i32,
}

pub struct DBHandler {
    pool: Pool<SqliteConnectionManager>,
}

impl DBHandler {
    pub fn new(db_path: &str) -> Self {
        let manager = SqliteConnectionManager::file(db_path);
        let pool = Pool::builder()
            .max_size(15) // Adjust pool size as needed
            .build(manager)
            .expect("Failed to create SQLite connection pool");

        {
            // Initialize tables using a pooled connection
            let conn = pool.get().expect("Failed to get connection from pool");
            conn.execute(
                "CREATE TABLE IF NOT EXISTS log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )",
                [],
            )
            .expect("Failed to create log table");

            conn.execute(
                "CREATE TABLE IF NOT EXISTS interval (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    blink_count INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )",
                [],
            )
            .expect("Failed to create interval table");

            conn.execute(
                "CREATE TABLE IF NOT EXISTS avg (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    avg_value INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )",
                [],
            )
            .expect("Failed to create avg table");
        }

        DBHandler { pool }
    }

    pub fn insert_interval(&self, interval: IntervalEntry) -> Result<(), String> {
        let timestamp_str = interval.timestamp.format("%Y-%m-%d %H:%M:%S").to_string();
        let conn = self.pool.get().map_err(|e| e.to_string())?;
        conn.execute(
            "INSERT INTO interval (blink_count, timestamp) VALUES (?1, ?2)",
            params![interval.blink_count, timestamp_str],
        )
        .map_err(|e| e.to_string())?;

        Ok(())
    }

    // Add similar insert methods for LogEntry and AvgEntry if needed
}
