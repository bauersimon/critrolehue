package model

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFromJSON(t *testing.T) {
	type testCase struct {
		Name string

		Data string

		ExpectedUrl     string
		ExpectedUpdates []*ColorUpdate
	}

	validate := func(t *testing.T, tc *testCase) {
		t.Run(tc.Name, func(t *testing.T) {
			actualUrl, actualUpdates, actualErr := FromJSON([]byte(tc.Data))
			assert.NoError(t, actualErr)

			assert.Equal(t, tc.ExpectedUrl, actualUrl)
			assert.Equal(t, tc.ExpectedUpdates, actualUpdates)
		})
	}

	validate(t, &testCase{
		Name: "Empty",
		Data: `{}`,
	})

	validate(t, &testCase{
		Name: "Only URL",
		Data: `{"url": "http://example.com"}`,

		ExpectedUrl:     "http://example.com",
		ExpectedUpdates: nil,
	})

	validate(t, &testCase{
		Name: "Simple",
		Data: `
			{
				"url": "https://www.youtube.com/watch?v=P8pLvV3FjPc",
				"updates": [
					{
						"time": 1012.5,
						"hue": [
							[
								0.09217337072706536,
								0.484069595758863,
								0.7591754650578171
							],
							[
								0.6560941940554528,
								0.5368648066902687,
								0.5346874119525348
							]
						],
						"temp": [
							3947.7972626686096
						]
					}
				]
			}
		`,

		ExpectedUrl: "https://www.youtube.com/watch?v=P8pLvV3FjPc",
		ExpectedUpdates: []*ColorUpdate{
			{
				Timestamp: 1012.5,
				Hues: []HSV{
					{
						Hue:        0.09217337072706536,
						Saturation: 0.484069595758863,
						Value:      0.7591754650578171,
					},
					{
						Hue:        0.6560941940554528,
						Saturation: 0.5368648066902687,
						Value:      0.5346874119525348,
					},
				},
				Temperatures: []float64{
					3947.7972626686096,
				},
			},
		},
	})

}
