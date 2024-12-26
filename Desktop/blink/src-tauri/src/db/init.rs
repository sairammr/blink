use rusqlite::{params, Result};
use r2d2::{Pool};
use r2d2_sqlite::SqliteConnectionManager;
use chrono::NaiveDateTime;
use std::time::Duration;
use tauri::async_runtime;

#[derive(Debug)]
pub struct IntervalEntry {
    pub start_time: NaiveDateTime,
    pub end_time: NaiveDateTime,
    pub blink_count: i32,
    pub presence_duration: Duration,
}
#[derive(Debug)]
pub struct LogEntry {
    pub message: String,
    pub timestamp: NaiveDateTime,
}

#[derive(Debug)]
pub struct AvgEntry {
    pub start_time: NaiveDateTime,
    pub end_time: NaiveDateTime,
    pub avg_value: i32,
}


pub struct DBHandler {
    pool: Pool<SqliteConnectionManager>,
}

impl DBHandler {
    pub fn new(db_path: &str) -> Self {
        let manager = SqliteConnectionManager::file(db_path);
        let pool = Pool::builder()
            .max_size(15)
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
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    avg_value INTEGER NOT NULL
                )",
                [],
            )
            .expect("Failed to create avg table");
        }

        DBHandler { pool }
    }

    pub fn insert_interval(&self, interval: IntervalEntry) -> Result<()> {
        let start_time_str = interval.start_time.format("%Y-%m-%d %H:%M:%S").to_string();
        let end_time_str = interval.end_time.format("%Y-%m-%d %H:%M:%S").to_string();
        let duration_ms = interval.presence_duration.as_millis() as i64;

        let conn = self.pool.get().map_err(|e| rusqlite::Error::QueryReturnedNoRows)?;
        conn.execute(
            "INSERT INTO interval (start_time, end_time, blink_count, presence_duration) 
             VALUES (?1, ?2, ?3, ?4)",
            params![start_time_str, end_time_str, interval.blink_count, duration_ms],
        )?;

        let pool = self.pool.clone();
        async_runtime::spawn(async move {
            if let Err(_) = DBHandler::validate(&pool).await {
                eprintln!("Validation failed");
            }
        });

        Ok(())
    }

    async fn validate(pool: &Pool<SqliteConnectionManager>) -> Result<()> {
        let conn = pool.get().map_err(|_| rusqlite::Error::QueryReturnedNoRows)?;
        
        let mut stmt = conn.prepare(
            "SELECT id, start_time, end_time, blink_count 
             FROM interval ORDER BY id DESC LIMIT 20;"
        )?;
        
        let rows = stmt.query_map([], |row| {
            Ok((
                row.get::<_, String>(1)?,
                row.get::<_, String>(2)?,
                row.get::<_, i64>(3)?,
            ))
        })?;
    
        let entries: Vec<(String, String, i64)> = rows.collect::<Result<Vec<_>>>()?;
        
        if entries.len() < 20 {
            println!("Not enough entries for validation");
            return Ok(());
        }
    
        let avg_blink_count = (entries.iter().map(|(_, _, bc)| bc).sum::<i64>() / 20) as i32;
        let first_start_time = entries.last().unwrap().0.clone();
        let last_end_time = entries.first().unwrap().1.clone();
    
        conn.execute(
            "INSERT INTO avg (start_time, end_time, avg_value) VALUES (?1, ?2, ?3)",
            params![first_start_time, last_end_time, avg_blink_count],
        )?;
    
        println!("Inserted summary: Start: {}, End: {}, Avg Blinks: {}", 
                 first_start_time, last_end_time, avg_blink_count);
        conn.execute("
            DELETE FROM interval 
            WHERE id IN (
            SELECT id 
            FROM interval 
            ORDER BY id DESC 
            LIMIT 20
        );");
        Ok(())
    }
}