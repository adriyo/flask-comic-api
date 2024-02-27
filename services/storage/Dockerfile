FROM golang:alpine

WORKDIR /app

COPY main.go .

COPY Dockerfile .

RUN mkdir -p storages

RUN go mod init storage-service && \
    go mod tidy

RUN go build -o main .

CMD ["./main"]