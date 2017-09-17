package main

import (
	"os"
	"testing"
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
