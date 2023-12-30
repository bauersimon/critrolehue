package lights

import (
	"fmt"

	"github.com/amimof/huego"
	"github.com/bauersimon/critrolehue/connector/config"
	"github.com/bauersimon/critrolehue/connector/model"
)

type PhilipsHueProvider struct {
	bridge *huego.Bridge
}

var validTypes = map[string]bool{
	"Color temperature light": true,
	"Extended color light":    true,
}

// Lights returns all lights.
func (p *PhilipsHueProvider) Lights() ([]Light, error) {
	lights, err := p.bridge.GetLights()
	if err != nil {
		return nil, err
	}

	var result []Light
	for _, light := range lights {
		if !validTypes[light.Type] {
			continue
		}

		result = append(result, &PhilipsHueLight{
			light: light,
		})
	}

	return result, nil
}

func setup() error {
	fmt.Println("Setting up Philips Hue bridge...")

	var host string
	bridge, err := huego.Discover()
	if err != nil {
		return err
	} else if bridge == nil || bridge.Host == "" {
		fmt.Print("No bridge found in network. Please enter the IP address of your bridge: ")
		fmt.Scanln(&host)
	} else {
		host = bridge.Host
	}

	fmt.Println("Press link button on bridge and press enter to continue.")
	fmt.Scanln()
	user, err := bridge.CreateUser("critrolehue")
	if err != nil {
		return err
	}

	if err := config.Global.Set("lights.philips.ip", host); err != nil {
		return err
	}
	if err := config.Global.Set("lights.philips.username", user); err != nil {
		return err
	}

	return config.Save()
}

func NewPhilipsHueProvider() (Provider, error) {
	if !config.Global.Exists("lights.philips") {
		if err := setup(); err != nil {
			return nil, err
		}
	}

	ip := config.Global.String("lights.philips.ip")
	username := config.Global.String("lights.philips.username")
	bridge := huego.New(ip, username)

	// Check if the bridge is reachable.
	_, err := bridge.GetLights()
	if err != nil {
		return nil, err
	}

	return &PhilipsHueProvider{
		bridge: bridge,
	}, nil
}

// Light represents a light.
type PhilipsHueLight struct {
	light huego.Light
}

// SetColor sets the color of the light.
func (l *PhilipsHueLight) SetColor(color *model.HSV, transition int) error {
	return l.light.SetState(huego.State{
		On:             true,
		Hue:            uint16(color.Hue * 65535),
		Sat:            uint8(color.Saturation * 254),
		Bri:            uint8(color.Value * 254),
		TransitionTime: uint16(transition * 10),
	})
}

// SetColor sets the color of the light.
func (l *PhilipsHueLight) SetTemperature(temperature float64, transition int) error {
	// Roughly approximate Mired value https://en.wikipedia.org/wiki/Mired.
	temp := 250 // 4000K
	if temperature > 4600 {
		temp = 153 // 6500K cold
	} else if temperature > 3600 {
		temp = 500 // 2000K warm
	}

	return l.light.SetState(huego.State{
		On:             true,
		Ct:             uint16(temp),
		Bri:            uint8(254),
		TransitionTime: uint16(transition * 10),
	})
}

// Alert flashes the light briefly.
func (l *PhilipsHueLight) Alert() (stop func() error, err error) {
	stop = func() error {
		return l.light.Alert("none")
	}
	return stop, l.light.Alert("lselect")
}

// ID returns the unique ID of the light.
func (l *PhilipsHueLight) ID() string {
	return l.light.UniqueID
}

// Name returns the name of the light.
func (l *PhilipsHueLight) Name() string {
	return l.light.Name
}
