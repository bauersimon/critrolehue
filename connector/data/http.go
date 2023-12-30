package data

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strings"
)

// HTTP is an HTTP data retriever.
type HTTP struct {
	// url is the base URL of the color data.
	url string
}

var reID = regexp.MustCompile(`watch\?v=([a-zA-Z0-9-_]+)`)

// Get retrieves the JSON color data associated with the given URL.
func (r *HTTP) Get(video_url string) ([]byte, error) {
	match := reID.FindStringSubmatch(video_url)
	if len(match) == 0 {
		return nil, fmt.Errorf("invalid URL: %s", video_url)
	}
	idURL, err := url.JoinPath(r.url, match[1]+".json")
	if err != nil {
		return nil, err
	}

	response, err := http.Get(idURL)
	if err != nil {
		return nil, err
	} else if response.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", response.StatusCode)
	} else if !strings.Contains(response.Header.Get("Content-Type"), "application/json") {
		return nil, fmt.Errorf("unexpected content type: %s", response.Header.Get("Content-Type"))
	}

	data, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}

	return data, nil
}

// NewHTTP creates a new HTTP data retriever.
func NewHTTP(dataURL string) Retriever {
	return &HTTP{
		url: dataURL,
	}
}
