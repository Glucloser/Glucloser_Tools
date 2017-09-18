package main

import (
	"os"
	"testing"
	"time"
)

func login(t *testing.T) (CarelinkSession, error) {
	sess, err := NewCarelinkSession()
	if err != nil {
		t.Fatalf("Couldn't create session: %v", err)
	}

	username := os.Getenv("CARELINK_USERNAME")
	if username == "" {
		t.Fatal("CARELINK_USERNAME not set")
	}
	password := os.Getenv("CARELINK_PASSWORD")
	if password == "" {
		t.Fatal("CARELINK_PASSWORD not set")
	}

	err = sess.Login(username, password)
	if err != nil {
		t.Fatalf("Login failed: %v", err)
	}

	return sess, err
}

func TestLogin(t *testing.T) {
	_, _ = login(t)
}

func TestCSVExport(t *testing.T) {
	sess, _ := login(t)
	reader, err := sess.CSVExport("09/16/2017", "09/17/2017")
	if err != nil {
		t.Fatalf("CSVExport failed: %v", err)
	}
	b := make([]byte, 100)
	n, err := reader.Read(b)
	if err != nil {
		t.Logf("Error reading CSVExport response: %v", err)
		t.Fail()
	}
	if n == 0 {
		t.Log("Read zero bytes from CSVExport response")
		t.Fail()
	}
}

func TestCGMExport(t *testing.T) {
	sess, _ := login(t)
	reader, err := sess.CGMExport()
	if err != nil {
		t.Fatalf("CGMExport failed: %v", err)
	}

	b := make([]byte, 100)
	n, err := reader.Read(b)
	if err != nil {
		t.Logf("Error reading CGMExport response: %v", err)
		t.Fail()
	}
	if n == 0 {
		t.Log("Read zero bytes from CGMExport response")
		t.Fail()
	}
}

func TestParseCSV(t *testing.T) {
	sess, _ := login(t)
	reader, err := sess.CSVExport("09/16/2017", "09/17/2017")
	if err != nil {
		t.Fatalf("CSVExport failed %v", err)
	}

	items, err := ParseCSVExport(reader)
	if err != nil {
		t.Fatalf("ParseCSVExport failed: %v", err)
	}

	select {
	case item := <-items:
		if item.RawType == "" {
			t.Logf("Item has no RawType: %v\n", item)
			t.Fail()
		}
	case _ = <-time.NewTicker(time.Second).C:
		t.Log("No items")
		t.Fail()
	}
}

func TestParseCGM(t *testing.T) {
	sess, _ := login(t)
	reader, err := sess.CGMExport()
	if err != nil {
		t.Fatalf("CGMExport failed: %v", err)
	}
	items, err := ParseCGMExport(reader)
	if err != nil {
		t.Fatalf("ParseCGMExport failed: %v", err)
	}

	if len(items) == 0 {
		t.Fatal("No sugars parsed")
	}
	sugar := items[0]
	if sugar.Value == 0 {
		t.Log("No sugar value")
		t.Fail()
	}
	var emptyTime time.Time
	if sugar.OccurredAt == emptyTime {
		t.Log("No occurredAt time")
		t.Fail()
	}
}
