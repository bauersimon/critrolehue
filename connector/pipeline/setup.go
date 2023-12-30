package pipeline

import (
	"fmt"

	"github.com/bauersimon/critrolehue/connector/config"
	"github.com/bauersimon/critrolehue/connector/lights"
)

func Setup(provider lights.Provider) error {
	lights, err := provider.Lights()
	if err != nil {
		return err
	}

	for _, light := range lights {
		stop, err := light.Alert()
		if err != nil {
			return err
		}

		var answer string
		fmt.Printf("Would you like to configure light %q? (y/N) ", light.Name())
		if _, err := fmt.Scanln(&answer); err != nil {
			return err
		} else if answer != "y" {
			stop()

			continue
		}

		fmt.Print("Hue or Temperature? (h/t) ")
		if _, err := fmt.Scanln(&answer); err != nil {
			return err
		}
		switch answer {
		case "h":
			config.Global.Set(fmt.Sprintf("lights.%s.type", light.ID()), "hue")
		case "t":
			config.Global.Set(fmt.Sprintf("lights.%s.type", light.ID()), "temp")
		default:
			fmt.Println("Invalid input. Ignoring this light.")
			stop()

			continue
		}

		var index int
		fmt.Print("Which hue/temperature index? ")
		if _, err := fmt.Scanln(&index); err != nil {
			return err
		}
		config.Global.Set(fmt.Sprintf("lights.%s.index", light.ID()), index)
		config.Global.Set(fmt.Sprintf("lights.%s.name", light.Name()), index)

		stop()
	}

	config.Save()

	return nil
}
