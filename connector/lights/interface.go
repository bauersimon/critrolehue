package lights

import "github.com/bauersimon/critrolehue/connector/model"

// Provider is a type that makes lights available.
type Provider interface {
	// Lights returns all lights.
	Lights() ([]Light, error)
}

// Light represents a light.
type Light interface {
	// SetColor sets the color of the light.
	SetColor(color *model.HSV, transition int) error
	// SetTemperature sets the color temperature of the light.
	SetTemperature(temperature float64, transition int) error
	// Alert flashes the light briefly .
	Alert() (stop func() error, err error)

	// ID returns the unique ID of the light.
	ID() string
	// Name returns the name of the light.
	Name() string
}
