package data

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestHTTP(t *testing.T) {
	type testCase struct {
		Name string

		VideoURL string
		Handler  http.HandlerFunc

		ExpectedData []byte
		ExpectedErr  error
	}

	validate := func(t *testing.T, tc *testCase) {
		t.Run(tc.Name, func(t *testing.T) {
			server := httptest.NewServer(tc.Handler)
			defer server.Close()

			actualData, actualErr := NewHTTP(server.URL).Get(tc.VideoURL)
			assert.Equal(t, tc.ExpectedData, actualData)
			assert.Equal(t, tc.ExpectedErr, actualErr)
		})
	}

	validate(t, &testCase{
		Name: "Invalid URL",

		VideoURL: "https://www.youtube.com/watch?v=#########",
		Handler:  func(w http.ResponseWriter, r *http.Request) {},

		ExpectedErr: errors.New("invalid URL: https://www.youtube.com/watch?v=#########"),
	})

	validate(t, &testCase{
		Name: "Simple",

		VideoURL: "https://www.youtube.com/watch?v=abcdefghijk",
		Handler: func(w http.ResponseWriter, r *http.Request) {
			assert.Equal(t, "/abcdefghijk.json", r.URL.Path)
			w.Header().Set("Content-Type", "application/json")
			w.Write([]byte("data"))
		},

		ExpectedData: []byte("data"),
	})
}
