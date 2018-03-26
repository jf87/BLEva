package main

import (
	"net/http"
)

type Route struct {
	Name        string
	Method      string
	Pattern     string
	HandlerFunc func(*appContext, http.ResponseWriter, *http.Request) (int, error)
}

type Routes []Route

var routes = Routes{
	Route{
		"Index",
		"GET",
		"/",
		IndexHandler,
	},
	Route{
		"Benchmarks",
		"GET",
		"/benchmarks",
		BenchmarksHandler,
	},
	Route{
		"PostBenchmark",
		"POST",
		"/benchmark",
		PostBenchmarkHandler,
	},
	Route{
		"RunBenchmark",
		"POST",
		"/benchmark/run",
		RunBenchmarkHandler,
	},
	Route{
		"PostBenchmarkResult",
		"POST",
		"/benchmark/result",
		PostBenchmarkResultHandler,
	},
	Route{
		"GetBenchmark",
		"GET",
		"/benchmark",
		GetBenchmarkHandler,
	},
	Route{
		"Sync",
		"GET",
		"/benchmark/sync/dongle",
		SyncBenchmarkDongleHandler,
	},
}
