package main

import (
	"log"
	"net/http"
	"time"
)

// Logger is wrapped around handlers
func Logger(inner http.Handler, name string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf(
			"%s\t%s\t%s\t%v",
			r.Method,
			r.RequestURI,
			name,
			time.Since(start).Nanoseconds(),
		)
		inner.ServeHTTP(w, r)
		log.Printf(
			"%s\t%s\t%s\t%v",
			r.Method,
			r.RequestURI,
			name,
			time.Since(start).Nanoseconds(),
		)
	})
}
