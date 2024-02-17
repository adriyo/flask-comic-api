FROM golang:alpine

WORKDIR /app

COPY . .

RUN mkdir storages

RUN go mod init storage-service && \
    go mod tidy

RUN go build -o main .

CMD ["./main"]