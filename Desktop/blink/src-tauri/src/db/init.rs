use rusqlite::{params, Connection};
use r2d2::Pool;
use r2d2_sqlite::SqliteConnectionManager;
use chrono::{NaiveDateTime};
use std::time::Duration;

#[derive(Debug)]
pub struct LogEntry {
    pub message: String,
    pub timestamp: NaiveDateTime,
}

#[derive(Debug)]
pub struct IntervalEntry {
    pub start_time: NaiveDateTime,
    pub end_time: NaiveDateTime,
    pub blink_count: i32,
    pub presence_duration: Duration,
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
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    blink_count INTEGER NOT NULL,
                    presence_duration INTEGER NOT NULL
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
        let start_time_str = interval.start_time.format("%Y-%m-%d %H:%M:%S").to_string();
        let end_time_str = interval.end_time.format("%Y-%m-%d %H:%M:%S").to_string();
        let duration_ms = interval.presence_duration.as_millis() as i64;
        
        let conn = self.pool.get().map_err(|e| e.to_string())?;
        
        conn.execute(
            "INSERT INTO interval (start_time, end_time, blink_count, presence_duration) 
             VALUES (?1, ?2, ?3, ?4)",
            params![
                start_time_str,
                end_time_str,
                interval.blink_count,
                duration_ms
            ],
        )
        .map_err(|e| e.to_string())?;
    
        Ok(())
    }

    // Add similar insert methods for LogEntry and AvgEntry if needed
}
