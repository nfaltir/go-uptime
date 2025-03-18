package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

const (
	targetURL     = "https://test.cofaexpress.com" // Replace with your site
	checkInterval = 10 * time.Minute
	dbFile        = "site_status.db"
	httpTimeout   = 10 * time.Second
	serverPort    = ":8080"
)

type Status struct {
	Timestamp time.Time `json:"timestamp"`
	Online    bool      `json:"online"`
	Latency   int64     `json:"latency"`
}

func initializeDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		return nil, err
	}

	createTableSQL := `
    CREATE TABLE IF NOT EXISTS status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        online BOOLEAN NOT NULL,
        latency INTEGER NOT NULL
    );`
	_, err = db.Exec(createTableSQL)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func checkSite(url string) (bool, int64, error) {
	client := &http.Client{
		Timeout: httpTimeout,
	}

	start := time.Now()
	resp, err := client.Get(url)
	if err != nil {
		return false, 0, err
	}
	defer resp.Body.Close()

	latency := time.Since(start).Milliseconds()
	online := resp.StatusCode >= 200 && resp.StatusCode < 300

	return online, latency, nil
}

func saveStatus(db *sql.DB, status Status) error {
	query := `
    INSERT INTO status (timestamp, online, latency)
    VALUES (?, ?, ?)`
	_, err := db.Exec(query, status.Timestamp, status.Online, status.Latency)
	return err
}

func getAllStatuses(db *sql.DB) ([]Status, error) {
	rows, err := db.Query(`
        SELECT timestamp, online, latency
        FROM status
        ORDER BY timestamp ASC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var statuses []Status
	for rows.Next() {
		var s Status
		if err := rows.Scan(&s.Timestamp, &s.Online, &s.Latency); err != nil {
			log.Printf("Failed to scan row: %v", err)
			continue
		}
		statuses = append(statuses, s)
	}
	return statuses, nil
}

func startHTTPServer(db *sql.DB) {
	// /data endpoint (returns all statuses as JSON)
	http.HandleFunc("/data", func(w http.ResponseWriter, r *http.Request) {
		statuses, err := getAllStatuses(db)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to fetch statuses: %v", err), http.StatusInternalServerError)
			return
		}

		// Format the timestamps explicitly for better JavaScript compatibility
		formattedStatuses := make([]map[string]interface{}, len(statuses))
		for i, s := range statuses {
			formattedStatuses[i] = map[string]interface{}{
				"timestamp": s.Timestamp.Format(time.RFC3339), // ISO8601 format
				"online":    s.Online,
				"latency":   s.Latency,
			}
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(formattedStatuses); err != nil {
			log.Printf("Failed to encode JSON response: %v", err)
		}
	})

	log.Printf("Starting HTTP server on %s", serverPort)
	if err := http.ListenAndServe(serverPort, nil); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}

func main() {
	// Initialize database
	db, err := initializeDB()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	// Start the HTTP server in a goroutine
	go startHTTPServer(db)

	// Set up ticker for periodic checks
	ticker := time.NewTicker(checkInterval)
	defer ticker.Stop()

	log.Printf("Starting site monitoring for %s (checking every %v)", targetURL, checkInterval)

	// Main loop for site monitoring
	for {
		select {
		case t := <-ticker.C:
			online, latency, err := checkSite(targetURL)
			if err != nil {
				log.Printf("Error checking site: %v", err)
				online = false
				latency = 0
			}

			log.Printf("Checked at %v: Online=%v, Latency=%dms", t, online, latency)

			status := Status{
				Timestamp: t,
				Online:    online,
				Latency:   latency,
			}
			if err := saveStatus(db, status); err != nil {
				log.Printf("Failed to save status: %v", err)
			}
		}
	}
}
