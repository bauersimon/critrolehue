package main

import (
	"flag"
	"fmt"
	"strings"

	"golang.org/x/exp/maps"
)

var commands = map[string]func([]string){
	"setup": nil,
	"run":   nil,
}

func main() {
	help := flag.Bool("help", false, "Show help")
	flag.Parse()
	if help != nil && *help {
		fmt.Printf("Available commands:\n\t%s\nGlobal options:\n", strings.Join(maps.Keys(commands), ", "))
		flag.PrintDefaults()
		return
	}

	remaining := flag.Args()
	if len(remaining) == 0 {
		fmt.Println("No command specified")
		return
	} else if command, ok := commands[remaining[0]]; !ok {
		fmt.Println("Unknown command:", remaining[0])
		return
	} else {
		command(remaining[1:])
	}
}
