package main

import (
	"github.com/Glucloser/models"
	"log"
	"os"
	"time"
)

func main() {
	sess, err := NewCarelinkSession()
	if err != nil {
		log.Fatal(err)
	}

	err = sess.Login(os.Getenv("CARELINK_USERNAME"), os.Getenv("CARELINK_PASSWORD"))
	if err != nil {
		log.Fatal(err)
	}

	processCSVExport(sess)
	processCGMExport(sess)

}

func processCSVExport(sess CarelinkSession) {
	today := time.Now().Add(-48 * time.Hour).Format("01/02/2006")
	tomorrow := time.Now().Format("01/02/2006")
	log.Printf("Fetching audit items from %s to %s", today, tomorrow)
	reader, err := sess.CSVExport(today, tomorrow)
	if err != nil {
		log.Println(err)
		return
	}
	auditItems, err := ParseCSVExport(reader)
	if err != nil {
		log.Println(err)
		return
	}

	count := 0
	db := models.DB().Begin()
	for item := range auditItems {
		var existing models.AuditItem
		db.Where(models.AuditItem{RawID: item.RawID}).First(&existing)
		if db.NewRecord(existing) {
			item.Occurred.OccurredAt = addEasternTZ(item.Occurred.OccurredAt)
			models.DB().Create(&item)
			count++
		}
	}
	db.Commit()
	if db.Error != nil {
		log.Printf("Audit Items error %v", db.Error)
	}
	log.Printf("Inserted %d Audit Items", count)

}

func processCGMExport(sess CarelinkSession) {
	reader, err := sess.CGMExport()
	if err != nil {
		log.Println(err)
		return
	}

	cgmReadings, err := ParseCGMExport(reader)
	if err != nil {
		log.Println(err)
		return
	}
	db := models.DB().Begin()
	inserted := 0
	for _, reading := range cgmReadings {
		var existing models.Sugar
		db.Where(&models.Sugar{Occurred: models.Occurred{reading.OccurredAt}}).First(&existing)
		if db.NewRecord(existing) {
			reading.OccurredAt = addEasternTZ(reading.OccurredAt)
			_ = db.Create(&reading)
			inserted++
		}
	}
	db.Commit()
	log.Printf("Inserted %d CGM Readings", inserted)
}

var (
	eastern *time.Location
)

func addEasternTZ(t time.Time) time.Time {
	if eastern == nil {
		var err error
		eastern, err = time.LoadLocation("America/New_York")
		if err != nil {
			log.Printf("Eastern err %v", err)
			return t
		}
	}
	year, month, day := t.Date()
	hour, minute, second := t.Clock()
	return time.Date(year, month, day, hour, minute, second, 0, eastern)

}
