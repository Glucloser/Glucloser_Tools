package main

import (
	"crypto/tls"
	"fmt"
	"golang.org/x/net/publicsuffix"
	"io"
	"log"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"strconv"
	"strings"
	"time"
)

const (
	userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/601.3.9 (KHTML, like Gecko)     Version/9.0.2 Safari/601.3.9"
	loginURL  = "https://carelink.minimed.com/patient/j_security_check"
	csvURL    = "https://carelink.minimed.com/patient/main/selectCSV.do?t=11"
	cgmURL    = "https://carelink.minimed.com/patient/connect/ConnectViewerServlet"
)

// CarelinkSession holds state for interacting with Carelink
type CarelinkSession struct {
	client http.Client
}

func NewCarelinkSession() (CarelinkSession, error) {
	defaultTransport := http.DefaultTransport.(*http.Transport)

	// Create new Transport that ignores self-signed SSL
	tr := &http.Transport{
		Proxy:                 defaultTransport.Proxy,
		DialContext:           defaultTransport.DialContext,
		MaxIdleConns:          defaultTransport.MaxIdleConns,
		IdleConnTimeout:       defaultTransport.IdleConnTimeout,
		ExpectContinueTimeout: defaultTransport.ExpectContinueTimeout,
		TLSHandshakeTimeout:   defaultTransport.TLSHandshakeTimeout,
		TLSClientConfig:       &tls.Config{InsecureSkipVerify: true},
	}
	jar, err := cookiejar.New(&cookiejar.Options{PublicSuffixList: publicsuffix.List})
	if err != nil {
		return CarelinkSession{}, err
	}
	return CarelinkSession{http.Client{Transport: tr, Jar: jar}}, nil
}

func (sess CarelinkSession) Login(username, password string) error {

	values := url.Values{}
	values.Add("j_username", username)
	values.Add("j_password", password)
	values.Add("j_character_encoding", "UTF-8")

	reader := strings.NewReader(values.Encode())

	req, err := http.NewRequest("POST", loginURL, reader)
	if err != nil {
		return err
	}

	req.Header.Add("User-Agent", userAgent)
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
	resp, err := sess.client.Do(req)
	if err != nil {
		return err
	}

	if resp.StatusCode > 400 {
		log.Printf("%s response from Carelink Login\n", resp.Status)
		return fmt.Errorf("%s response from Carelink Login", resp.Status)
	}

	return nil
}

func (sess CarelinkSession) CSVExport(start, end string) (io.ReadCloser, error) {
	values := url.Values{}
	values.Add("datePicker2", start)
	values.Add("listSeparator", ",")
	values.Add("datePicker1", end)
	values.Add("report", "11")
	values.Add("customerID", "553090")

	reader := strings.NewReader(values.Encode())

	req, err := http.NewRequest("POST", csvURL, reader)
	if err != nil {
		return nil, err
	}

	req.Header.Add("User-Agent", userAgent)
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded; charset=utf-8")
	resp, err := sess.client.Do(req)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode > 400 {
		log.Printf("%s response from Carelink CSVExport\n", resp.Status)
		return nil, fmt.Errorf("%s response from Carelink CSVExport", resp.Status)
	}

	return resp.Body, nil
}

func (sess CarelinkSession) CGMExport() (io.ReadCloser, error) {
	urlParams := url.Values{}
	urlParams.Add("cpSerialNumber", "NONE")
	urlParams.Add("msgType", "last24hours")
	now := time.Now().Unix()
	urlParams.Add("requestTime", strconv.FormatInt(now, 10))
	url := cgmURL + "?" + urlParams.Encode()

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Add("User-Agent", userAgent)
	resp, err := sess.client.Do(req)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode > 400 {
		log.Printf("%s response from Carelink CGMExport\n", resp.Status)
		return nil, fmt.Errorf("%s response from Carelink CGMExport", resp.Status)
	}

	return resp.Body, nil
}
