package main

import (
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/bauersimon/critrolehue/connector/config"
	"github.com/bauersimon/critrolehue/connector/data"
	"github.com/bauersimon/critrolehue/connector/lights"
	"github.com/bauersimon/critrolehue/connector/model"
	"github.com/bauersimon/critrolehue/connector/pipeline"
	"github.com/bauersimon/critrolehue/connector/pulse"
	"golang.org/x/exp/maps"
)

func setup([]string) error {
	provider, err := lights.NewPhilipsHueProvider()
	if err != nil {
		return err
	}

	return pipeline.Setup(provider)
}

func run(args []string) error {
	flagSet := flag.NewFlagSet("run", flag.ExitOnError)
	offset := flagSet.Duration("offset", 0.0, "Time offset in seconds")
	delay := flagSet.Int("delay", 1, "Update delay in seconds")
	transition := flagSet.Float64("transition", 10.0, "Transition time in seconds")
	url := flagSet.String("url", "", "Video URL")
	dataURL := flagSet.String("data", "https://bauersimon.github.io/critrolehue/data/v1/c3/", "Data URL")
	if err := flagSet.Parse(args); err != nil {
		if err == flag.ErrHelp {
			flagSet.PrintDefaults()
			return nil
		}
		return err
	}

	provider, err := lights.NewPhilipsHueProvider()
	if err != nil {
		return err
	}
	timestamper := pulse.NewClock((*offset).Seconds())
	http := data.NewHTTP(*dataURL)
	data, err := http.Get(*url)
	if err != nil {
		return err
	}
	_, updates, err := model.FromJSON(data)
	if err != nil {
		return err
	}

	return pipeline.Once(provider, timestamper, updates, *delay, *transition)
}

var commands = map[string]func([]string) error{
	"setup": setup,
	"run":   run,
}

func main() {
	flagSet := flag.NewFlagSet("global", flag.ExitOnError)
	configPath := flagSet.String("config", "config.json", "Path to config file")
	if err := flagSet.Parse(os.Args[1:]); err != nil {
		if err == flag.ErrHelp {
			fmt.Printf("Available commands:\n\t%s\nGlobal options:\n", strings.Join(maps.Keys(commands), ", "))
			flagSet.PrintDefaults()
			return
		}
		panic(err)
	}

	if err := config.Init(*configPath); err != nil {
		panic(err)
	}

	remaining := flagSet.Args()
	if len(remaining) == 0 {
		fmt.Println("No command specified")
		return
	} else if command, ok := commands[remaining[0]]; !ok {
		fmt.Println("Unknown command:", remaining[0])
		return
	} else {
		if err := command(remaining[1:]); err != nil {
			panic(err)
		}
	}
}
