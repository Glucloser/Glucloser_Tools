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
	today := time.Now().Format("01/02/2006")
	tomorrow := time.Now().Add(time.Hour * 24).Format("01/02/2006")
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
	for item := range auditItems {
		models.DB().Create(&item)
		count++
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
	for _, reading := range cgmReadings {
		models.DB().Create(&reading)
	}
	log.Printf("Inserted %d CGM Readings", len(cgmReadings))
}
