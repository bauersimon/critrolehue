test:
	go test ./...
.PHONY: test

build:
	rm -rf build
	go build -o build/connector main.go

.PHONY: build

release:
	rm -rf build
	GOOS=windows GOARCH=amd64 go build -o build/connector_win.exe main.go
	GOOS=darwin GOARCH=amd64 go build -o build/connector_mac_intel main.go
	GOOS=darwin GOARCH=arm64 go build -o build/connector_mac_arm main.go
	GOOS=linux GOARCH=amd64 go build -o build/connector_unix main.go
.PHONY: release