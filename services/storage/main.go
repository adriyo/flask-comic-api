package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

func uploadFile(w http.ResponseWriter, r *http.Request) {
	r.ParseMultipartForm(10 << 20)

	file, handler, err := r.FormFile("file")
	if err != nil {
		fmt.Println(err)
		http.Error(w, "Failed to retrieve the file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	filename := handler.Filename
	if filename == "" {
		http.Error(w, "File name is empty", http.StatusBadRequest)
		return
	}

	storageDir := "./storages"
	if _, err := os.Stat(storageDir); os.IsNotExist(err) {
		os.Mkdir(storageDir, os.ModePerm)
	}

	f, err := os.OpenFile(storageDir+"/"+filename, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		fmt.Println(err)
		http.Error(w, "Failed to create file on server", http.StatusInternalServerError)
		return
	}
	defer f.Close()

	_, err = io.Copy(f, file)
	if err != nil {
		fmt.Println(err)
		http.Error(w, "Failed to copy file to server", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "File Uploaded Successfully: %s", filename)
}

func serveFile(w http.ResponseWriter, r *http.Request) {
	filename := strings.TrimPrefix(r.URL.Path, "/files/")

	cwd, err := os.Getwd()
	if err != nil {
		http.Error(w, "error getting files", http.StatusNotFound)
		return
	}

	filepath := cwd + "/storages/" + filename

	file, err := os.Open(filepath)
	if err != nil {
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}
	defer file.Close()

	_, err = io.Copy(w, file)
	if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
}

func downloadFile(url string) (string, error) {
	response, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer response.Body.Close()

	if response.StatusCode != 200 {
		fmt.Printf("failed to download file, status code: %d", response.StatusCode)
		return "", fmt.Errorf("failed to download file, status code: %d", response.StatusCode)
	}

	fileName := filepath.Base(url)
	file, err := os.Create("./storages/" + fileName)
	if err != nil {
		fmt.Println("err: ", err)
		return "", err
	}
	defer file.Close()

	_, err = io.Copy(file, response.Body)
	if err != nil {
		return "", err
	}

	return fileName, nil
}

func saveHandler(w http.ResponseWriter, r *http.Request) {
	var data struct {
		URL string `json:"url"`
	}
	err := json.NewDecoder(r.Body).Decode(&data)
	if err != nil {
		fmt.Println("Invalid request body", err)
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	filename, err := downloadFile(data.URL)
	if err != nil {
		fmt.Println("Failed to download file", err)
		http.Error(w, "Failed to download file", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]string{"filename": filename})
}

func setupRoutes() {
	http.HandleFunc("/save", saveHandler)
	http.HandleFunc("/upload", uploadFile)
	http.HandleFunc("/files/", serveFile)
	http.ListenAndServe(":8080", nil)
}

func main() {
	fmt.Println("Starting Storage Service...")
	setupRoutes()
}
