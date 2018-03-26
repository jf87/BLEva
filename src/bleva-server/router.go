package main

import (
	"github.com/gorilla/mux"
)

func NewRouter(context *appContext) *mux.Router {

	router := mux.NewRouter().StrictSlash(true)
	for _, route := range routes {
		router.
			Methods(route.Method).
			Path(route.Pattern).
			Name(route.Name).
			Handler(Logger(appHandler{context, route.HandlerFunc}, route.Name))
	}

	return router
}

