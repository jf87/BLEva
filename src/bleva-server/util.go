package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
)

var template string

func generateBenchmarks(template string) []Benchmark {
	var adv_intervals []string
	var scan_modes []string
	var wifi_states []string
	var replicas []int
	var bs []Benchmark
	adv_intervals = []string{"0x100"}
	scan_modes = []string{"low_latency", "balanced", "low_power"}
	wifi_states = []string{"active", "on"}
	replicas = []int{1}

	file, err := ioutil.ReadFile(template)
	if err != nil {
		fmt.Printf("File error: %v\n", err)
		os.Exit(1)
	}
	for _, r := range replicas {
		for _, sm := range scan_modes {
			for _, ai := range adv_intervals {
				for _, ws := range wifi_states {
					var b Benchmark
					json.Unmarshal(file, &b)
					b.Dongles[0].Replicas = r
					b.Phone.Steps[0].Scan_mode = sm
					b.Dongles[0].Steps[0].Adv_interval_min = ai
					b.Dongles[0].Steps[0].Adv_interval_max = ai
					b.Phone.Steps[0].Wifi_state = ws
					b.Name = "scanning-30s-" + sm + "-wifi" + ws + "-" + ai + "-" + strconv.Itoa(r) + "dongle"
					b.Description = b.Name
					b.Repetitions = 20
					bs = append(bs, b)
				}
			}
		}
	}
	return bs
}

func generateConnectedBenchmarks(template string) []Benchmark {
	var bs []Benchmark
	var connection_interval_min []float64

	file, err := ioutil.ReadFile(template)
	if err != nil {
		fmt.Printf("File error: %v\n", err)
		os.Exit(1)
	}

	connection_interval_min = []float64{320}
	//connection_interval_min = []float64{480, 640, 800, 960, 1120, 1280, 1600, 2000}

	for _, v := range connection_interval_min {
		var b Benchmark
		json.Unmarshal(file, &b)
		b.Dongles[0].Steps[0].Connection_interval_min = v
		b.Dongles[0].Steps[0].Connection_interval_max = v
		b.Dongles[0].Steps[0].Supervision_timeout = v * 6
		b.Dongles[0].Steps[0].Time = 40000 + (v * 6)
		b.Time = 40000 + (v * 6)
		b.Name = "read-write-" + strconv.Itoa(int(v)) + "ms-connection-interval"
		b.Description = b.Name
		bs = append(bs, b)
	}
	return bs
}

func generateBlueMorphoBenchmarks(template string) []Benchmark {
	var adv_intervals []string
	var scan_modes []string
	var wifi_states []string
	var replicas []int
	var bs []Benchmark
	adv_intervals = []string{"0x100", "0x400", "0x800"}
	scan_modes = []string{"low_latency", "bluemorpho"}
	wifi_states = []string{"on"}
	replicas = []int{1}

	file, err := ioutil.ReadFile(template)
	if err != nil {
		fmt.Printf("File error: %v\n", err)
		os.Exit(1)
	}
	for _, r := range replicas {
		for _, sm := range scan_modes {
			for _, ai := range adv_intervals {
				for _, ws := range wifi_states {
					var b Benchmark
					json.Unmarshal(file, &b)
					b.Time = 60000
					b.Phone.Steps[0].Time = 60000
					b.Dongles[0].Steps[0].Time = 60000
					b.Dongles[0].Replicas = r
					b.Phone.Steps[0].Scan_mode = sm
					b.Dongles[0].Steps[0].Adv_interval_min = ai
					b.Dongles[0].Steps[0].Adv_interval_max = ai
					b.Phone.Steps[0].Wifi_state = ws
					b.Name = "bluemorpho-scanning-60s-" + sm + "-wifi" + ws + "-" + ai + "-" + strconv.Itoa(r) + "dongle"
					b.Description = b.Name
					b.Repetitions = 1
					bs = append(bs, b)
				}
			}
		}
	}
	return bs
}

func pathExists(s string) bool {
	if _, err := os.Stat(s); os.IsNotExist(err) {
		return false
	} else {
		return true
	}
}
