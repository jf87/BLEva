package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/lib/pq"
)

type Benchmark struct {
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Time        float64  `json:"time"`
	Repetitions int      `json:"repetitions,omitempty"`
	Phone       Phone    `json:"phone"`
	Dongles     []Dongle `json:"dongles"`
}

type Phone struct {
	Gap_role  string      `json:"gap_role"`
	Gatt_role string      `json:"gatt_role"`
	Steps     []PhoneStep `json:"steps"`
	Replicas  int         `json:"replicas"`
}

type Dongle struct {
	Gap_role  string       `json:"gap_role"`
	Gatt_role string       `json:"gatt_role"`
	Replicas  int          `json:"replicas"`
	Steps     []DongleStep `json:"steps"`
}

type DongleStep struct {
	Time                    float64 `json:"time"`
	Ble_operation           string  `json:"ble_operation"`
	Adv_data                string  `json:"adv_data"`
	Short_name              string  `json:"short_name"`
	Sr_data                 string  `json:"sr_data"`
	Long_name               string  `json:"long_name"`
	Major                   string  `json:"major"`
	Minor                   string  `json:"minor"`
	Adv_interval_min        string  `json:"adv_interval_min"`
	Adv_interval_max        string  `json:"adv_interval_max"`
	Adv_channels            string  `json:"adv_channels"`
	Gap_discoverable_mode   string  `json:"gap_discoverable_mode"`
	Gap_connectable_mode    string  `json:"gap_connectable_mode"`
	Connection_interval_min float64 `json:"connection_interval_min,omitempty"`
	Connection_interval_max float64 `json:"connection_interval_max,omitempty"`
	Slave_latency           float64 `json:"slave_latency,omitempty"`
	Supervision_timeout     float64 `json:"supervision_timeout,omitempty"`
}

type PhoneStep struct {
	Time          float64  `json:"time"`
	Ble_operation string   `json:"ble_operation"`
	Callback_type string   `json:"callback_type"`
	Match_mode    string   `json:"match_mode"`
	Match_num     string   `json:"match_num"`
	Scan_mode     string   `json:"scan_mode"`
	Report_delay  float64  `json:"report_delay"`
	Wifi_state    string   `json:"wifi_state"`
	Filters       []string `json:"filters"`
	Repetitions   int      `json:"repetitions,omitempty"`
}

type Result struct {
	Result string `json:"result"`
}

type appContext struct {
	Benchmarks       []Benchmark
	Results_path     string
	Active_benchmark []Benchmark
}

type appHandler struct {
	*appContext
	h func(*appContext, http.ResponseWriter, *http.Request) (int, error)
}

var syncPhone = make(chan int)
var syncDongle = make(chan int)
var queue = make(chan Benchmark)

var done = make(chan bool)

var noPhones int

var files []string
var start time.Time

func main() {
	var (
		port         = flag.String("port", "8888", "Port to listen on (optional)")
		benchmarks   = flag.String("benchmarks", "", "Folder with benchmark files")
		template     = flag.String("template", "", "Path to template for autogenerate")
		results_path = flag.String("results_path", "", "Path to folder for results")
	)

	flag.Parse()
	if *results_path == "" {
		fmt.Fprintln(os.Stderr, "Missing results_path (-results_path)")
		fmt.Fprintln(os.Stderr, `Usage:
      bleva-server [flags]
Flags:`)
		flag.PrintDefaults()
		os.Exit(1)
	}

	//iBeacon = false

	var t []Benchmark
	var b []Benchmark

	if *template != "" {
		//t = generateConnectedBenchmarks(*template)
		t = generateBenchmarks(*template)
	}
	if *benchmarks != "" {
		b = getBenchmarks(*benchmarks)
	} else if *template == "" && *benchmarks == "" {
		fmt.Fprintln(os.Stderr, "Need either template or path to benchmarks")
		os.Exit(1)
	}

	b = append(b, t...)

	context := &appContext{Benchmarks: b, Results_path: *results_path}
	router := NewRouter(context)
	start = time.Now()
	fmt.Println("BLEva-Server has started...")
	log.Fatal(http.ListenAndServe(":"+*port, router))
}

func getBenchmarks(root string) []Benchmark {
	var bs []Benchmark
	err := filepath.Walk(root, addFiles)
	if err != nil {
		log.Fatal(err)
	}

	for _, filename := range files {
		file, err := ioutil.ReadFile(filename)
		if err != nil {
			fmt.Printf("File error: %v\n", err)
			os.Exit(1)
		}
		var b Benchmark
		if err = json.Unmarshal(file, &b); err != nil {
			fmt.Printf("Unmarshal error: %v: %v\n", err, filename)
		} else {
			fmt.Printf("%v\n", b)
			bs = append(bs, b)
		}
	}
	return bs
}

func addFiles(path string, f os.FileInfo, err error) error {
	if strings.Contains(path, "json") {
		files = append(files, path)
	}
	return nil
}
