package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

var activeBenchmark Benchmark
var iBeacon bool

func (ah appHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Updated to pass ah.appContext as a parameter to our handler type.
	status, err := ah.h(ah.appContext, w, r)
	if err != nil {
		log.Printf("HTTP %d: %q", status, err)
		switch status {
		case http.StatusNotFound:
			http.NotFound(w, r)
			// And if we wanted a friendlier error page:
			// err := ah.renderTemplate(w, "http_404.tmpl", nil)
		case http.StatusInternalServerError:
			http.Error(w, http.StatusText(status), status)
		default:
			http.Error(w, http.StatusText(status), status)
		}
	}
}

// HTTP handler that maps on / a function that takes the HTTP server response (w)
// and the client HTTP request (r) as its arguments. We then write to the response
// of the server, which then leads to HTTP data being send to the client.
func IndexHandler(a *appContext, w http.ResponseWriter, r *http.Request) (int, error) {
	if _, err := fmt.Fprintf(w, "Welcome to BLEva Server"); err != nil {
		return -1, err
	}

	return 200, nil
}

// provides the benchmarks
func BenchmarksHandler(a *appContext, w http.ResponseWriter, r *http.Request) (int, error) {
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	j, err := json.MarshalIndent(a.Benchmarks, "", " ")
	if err != nil {
		return http.StatusInternalServerError, err
	}
	w.Write(j)
	//if err := json.NewEncoder(w).Encode(a.Benchmarks); err != nil {
	//fmt.Println(err)
	//return -1, err
	//}
	return 200, nil
}

// set active benchmark
func PostBenchmarkHandler(a *appContext, w http.ResponseWriter, r *http.Request) (int, error) {
	// parse json, get config for dongle and notify dongle process
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 104800567)) //limit size FIXME how big?
	if err != nil {
		return -1, err
	}
	if err := r.Body.Close(); err != nil {
		return -1, err
	}
	fmt.Printf("Body:\n%s\n\n", body)
	if err := json.Unmarshal(body, &activeBenchmark); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422)                                             // not possible to process
		if err := json.NewEncoder(w).Encode(err.Error()); err != nil { //we need err.Error() to access the error string
			return -1, err
		}
	}
	// 1. Collect benchmarks from all phones
	a.Active_benchmark = append(a.Active_benchmark, activeBenchmark)

	var res Result
	res.Result = "Success"
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(res); err != nil {
		return -1, err
	}
	return 200, nil
}

// phone post here the benchmark they need to run
func RunBenchmarkHandler(a *appContext, w http.ResponseWriter, r *http.Request) (int, error) {
	// parse json, get config for dongle and notify dongle process
	var b Benchmark
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 104800567)) //limit size FIXME how big?
	if err != nil {
		return -1, err
	}
	if err := r.Body.Close(); err != nil {
		return -1, err
	}
	if err := json.Unmarshal(body, &b); err != nil {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(422)                                             // not possible to process
		if err := json.NewEncoder(w).Encode(err.Error()); err != nil { //we need err.Error() to access the error string
			return -1, err
		}
	}
	fmt.Println(b.Name)
	// 2. Tell dongle and phones to start

	// send to GET queue //TODO make more robust!
	var res Result
	var s = 0
	//if !iBeacon {
	// try to add benchmark to queue
	select {
	case queue <- b:
		fmt.Println("posted to queue :-)")
		s = 1
		// a read from syncPhone has occurred
	case <-time.After(time.Second * 90):
		fmt.Println("timeout sync1")
		s = 2
		// the read from ch has timed out
	}

	// after we have posted to queue, wait for the dongle to be ready
	// this is signaled by dongle calling SyncBenchmarkDongleHandler
	fmt.Println("waiting for dongle ready signal")
	if s == 1 {
		select {
		case <-syncDongle:
			fmt.Println("synced :-)")
			// a read from syncDongle has occurred
		case <-time.After(time.Second * 90):
			fmt.Println("timeout sync2")
			s = 2
			// the read from ch has timed out
		}
	}
	//} else {
	//s = 1
	//}
	if s == 1 {
		res.Result = "Success"
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(http.StatusOK)
		if err := json.NewEncoder(w).Encode(res); err != nil {
			return -1, err
		}
	} else {
		w.Header().Set("Content-Type", "application/json; charset=UTF-8")
		w.WriteHeader(http.StatusNotFound)
		res.Result = "error"
		if err := json.NewEncoder(w).Encode(res); err != nil {
			return -1, err
		}
	}
	return 200, nil
}

// queue of to be run benchmarks, gets called by dongle and returns when benchmark is posted by a phone
func GetBenchmarkHandler(a *appContext, w http.ResponseWriter, r *http.Request) (int, error) {
	var q Benchmark
	q = <-queue
	for i := 0; i < q.Phone.Replicas-1; i++ {
		q = <-queue
	}
	if q.Name != activeBenchmark.Name {
		fmt.Println("received old benchmark from queue, going to throw it away...")
		err := fmt.Errorf("Active Benchmark does not fit with Benchmark in Queue")
		return http.StatusInternalServerError, err
	}
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	//j, err := json.MarshalIndent(q, "", " ")
	j, err := json.Marshal(activeBenchmark)
	if err != nil {
		return http.StatusInternalServerError, err
	}
	w.Write(j)
	return 200, nil
}

// gets called when by dongle when it is ready
func SyncBenchmarkDongleHandler(a *appContext, w http.ResponseWriter, r *http.Request) (int, error) {
	// signal all phones that we are ready to start
	for i := 0; i < activeBenchmark.Phone.Replicas; i++ {
		syncDongle <- 1

	}
	fmt.Println(r.UserAgent)
	return 200, nil
}

func PostBenchmarkResultHandler(a *appContext, w http.ResponseWriter, r *http.Request) (int, error) {
	body, err := ioutil.ReadAll(io.LimitReader(r.Body, 104800567)) //limit size FIXME how big?
	if err != nil {
		return -1, err
	}
	if err := r.Body.Close(); err != nil {
		return -1, err
	}
	fmt.Println("received benchmark result")
	t := time.Now()
	s := a.Results_path + "/" + t.Format("20060102150405")
	for i := 0; ; i++ {
		if !pathExists(s + "_" + strconv.Itoa(i) + ".json") {
			s = s + "_" + strconv.Itoa(i) + ".json"
			break
		}
	}
	f, err := os.Create(s)
	if err != nil {
		return 500, err
	}
	if _, err = f.Write(body); err != nil {
		return 500, err
	}
	var res Result
	res.Result = "Success"
	w.Header().Set("Content-Type", "application/json; charset=UTF-8")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(res); err != nil {
		return -1, err
	}
	return 200, nil
}
