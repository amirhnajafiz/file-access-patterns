# Use official go image
FROM golang:1.25-alpine3.21 AS build

COPY operator/go.mod operator/go.sum /usr/local/app/

# download all dependencies. Dependencies will be cached if the go.mod and go.sum files are not changed
RUN go mod download

COPY operator/include /usr/local/app
COPY operator/pkg /usr/local/app
COPY operator/main.go /usr/local/app

WORKDIR /usr/local/app

# Build the go app
RUN GO111MODULE=on CGO_ENABLED=0 go build -o flap ./main.go

# Minimal alpine image
FROM alpine:3.21

COPY --from=build /usr/local/app/flap /usr/local/bin/flap

ENTRYPOINT ["/usr/local/bin/flap"]
