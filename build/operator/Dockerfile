# Use official go image
FROM golang:1.25-alpine3.21 AS build

WORKDIR /usr/local/app

COPY operator/go.mod operator/go.sum .

# download all dependencies. Dependencies will be cached if the go.mod and go.sum files are not changed
RUN go mod download

COPY operator/ .

# Build the go app
RUN GO111MODULE=on CGO_ENABLED=0 go build -o flap ./main.go

# Minimal alpine image
FROM alpine:3.21

COPY --from=build /usr/local/app/flap /usr/local/bin/flap

ENTRYPOINT ["/usr/local/bin/flap"]
