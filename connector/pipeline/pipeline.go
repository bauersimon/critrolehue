package pipeline

import (
	"fmt"
	"time"

	"github.com/bauersimon/critrolehue/connector/config"
	"github.com/bauersimon/critrolehue/connector/lights"
	"github.com/bauersimon/critrolehue/connector/model"
	"github.com/bauersimon/critrolehue/connector/pulse"
)

func findUpdate(updates []*model.ColorUpdate, timestamp float64, transition float64) *model.ColorUpdate {
	for i := len(updates) - 1; i >= 0; i-- {
		update := updates[i]
		if update.Timestamp-transition <= timestamp {
			return update
		}
	}
	return nil
}

func processUpdate(update *model.ColorUpdate, hueLights [][]lights.Light, tempLights [][]lights.Light, transition float64) {
	for i, hue := range update.Hues {
		for _, lights := range hueLights[i] {
			lights.SetColor(&hue, int(transition))
		}
	}
	for i, temp := range update.Temperatures {
		for _, lights := range tempLights[i] {
			lights.SetTemperature(temp, int(transition))
		}
	}
}

func Once(provider lights.Provider, timestamper pulse.Timestamper, updates []*model.ColorUpdate, delay int, transition float64) error {
	allLights, err := provider.Lights()
	if err != nil {
		return err
	}

	var maxIndex int
	for _, light := range allLights {
		index := config.Global.Int(fmt.Sprintf("lights.%s.index", light.ID()))
		if index > maxIndex {
			maxIndex = index
		}
	}
	maxIndex-- // Indexes are 1-based, but we want to use them as 0-based.

	hueLights := make([][]lights.Light, maxIndex+1)
	tempLights := make([][]lights.Light, maxIndex+1)
	for _, light := range allLights {
		var lightType *[][]lights.Light
		switch config.Global.String(fmt.Sprintf("lights.%s.type", light.ID())) {
		case "hue":
			lightType = &hueLights
		case "temp":
			lightType = &tempLights
		default:
			continue
		}

		index := config.Global.Int(fmt.Sprintf("lights.%s.index", light.ID()))
		index-- // Indexes are 1-based, but we want to use them as 0-based.

		(*lightType)[index] = append((*lightType)[index], light)
	}

	var previousUpdate *model.ColorUpdate
	for !timestamper.Done() {
		timestamp := timestamper.Timestamp()
		update := findUpdate(updates, timestamp, transition)
		if update != nil && update != previousUpdate {
			fmt.Printf("Initiating next update for timestamp %v\n", update.Timestamp)
			processUpdate(update, hueLights, tempLights, transition)
			previousUpdate = update
		}

		time.Sleep(time.Duration(delay) * time.Second)
	}

	return nil
}
