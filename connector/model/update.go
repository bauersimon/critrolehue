package model

import (
	"encoding/json"
	"fmt"
)

var ErrInvalidUpdate = func(data []byte) error {
	return fmt.Errorf("invalid update: %v", data)
}

// ColorUpdate is a color update at a certain time.
type ColorUpdate struct {
	// Timestamp is the time of the update in seconds.
	Timestamp float64
	// Hues is the color hues at the time.
	Hues []HSV
	// Temperatures is the color temperatures in Kelvin at the time.
	Temperatures []float64
}

// UnmarshalJSON implements the json.Unmarshaler interface.
func (c *ColorUpdate) UnmarshalJSON(data []byte) error {
	aux := &struct {
		Time         float64     `json:"time"`
		Hues         [][]float64 `json:"hue"`
		Temperatures []float64   `json:"temp"`
	}{}
	if err := json.Unmarshal(data, aux); err != nil {
		return err
	}

	c.Timestamp = aux.Time
	for _, hue := range aux.Hues {
		if len(hue) != 3 {
			return ErrInvalidUpdate(data)
		}
		for _, value := range hue {
			if value < 0 || value > 1 {
				return ErrInvalidUpdate(data)
			}
		}
		c.Hues = append(c.Hues, HSV{
			Hue:        hue[0],
			Saturation: hue[1],
			Value:      hue[2],
		})
	}
	for _, value := range aux.Temperatures {
		if value < 0 {
			return ErrInvalidUpdate(data)
		}
	}
	c.Temperatures = aux.Temperatures

	return nil
}

// HSV is a color model that describes colors (hue, saturation, value).
type HSV struct {
	// Hue is the color hue in the range [0.0, 1.0].
	Hue float64
	// Saturation is the color saturation in the range [0.0, 1.0].
	Saturation float64
	// Value is the color value in the range [0.0, 1.0].
	Value float64
}

// FromJOSON parses JSON data into a URL and a list of color updates.
func FromJSON(data []byte) (url string, updates []*ColorUpdate, err error) {
	aux := &struct {
		URL     string         `json:"url"`
		Updates []*ColorUpdate `json:"updates"`
	}{}
	if err := json.Unmarshal(data, aux); err != nil {
		return "", nil, err
	}

	return aux.URL, aux.Updates, nil
}
