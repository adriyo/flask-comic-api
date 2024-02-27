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
	userId := r.FormValue("user_id")
	comicId := r.FormValue("comic_id")
	chapterId := r.FormValue("chapter_id")
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

	storageDir := "./storages/" + userId + "/" + comicId + "/" + chapterId
	if _, err := os.Stat(storageDir); os.IsNotExist(err) {
		if err := os.MkdirAll(storageDir, os.ModePerm); os.IsNotExist(err) {
			fmt.Println(err)
			http.Error(w, "Failed to create directory on server", http.StatusInternalServerError)
			return
		}
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
	parts := strings.Split(strings.TrimPrefix(r.URL.Path, "/files/"), "/")
	fmt.Print("parts: ", len(parts))
	if len(parts) < 3 {
		http.Error(w, "Invalid file path", http.StatusBadRequest)
		return
	}

	userID := parts[0]
	comicID := parts[1]

	filename := parts[len(parts)-1]

	var chapterID string
	if len(parts) == 4 {
		chapterID = parts[2]
	}

	cwd, err := os.Getwd()
	if err != nil {
		http.Error(w, "error getting files", http.StatusNotFound)
		return
	}

	var filePath string
	if chapterID == "" {
		filePath = filepath.Join(cwd, "storages", userID, comicID, filename)
	} else {
		filePath = filepath.Join(cwd, "storages", userID, comicID, chapterID, filename)
	}

	file, err := os.Open(filePath)
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

type DownloadPayload struct {
	URL     string `json:"url"`
	UserID  string `json:"user_id"`
	ComicID string `json:"comic_id"`
}

func downloadFile(data DownloadPayload) (string, error) {
	response, err := http.Get(data.URL)
	if err != nil {
		return "", err
	}
	defer response.Body.Close()

	if response.StatusCode != 200 {
		fmt.Printf("failed to download file, status code: %d", response.StatusCode)
		return "", fmt.Errorf("failed to download file, status code: %d", response.StatusCode)
	}

	fileName := filepath.Base(data.URL)
	userId := data.UserID
	comicId := data.ComicID
	storageDir := "./storages/" + userId + "/" + comicId + "/"
	if _, err := os.Stat(storageDir); os.IsNotExist(err) {
		if err := os.MkdirAll(storageDir, os.ModePerm); os.IsNotExist(err) {
			fmt.Println(err)
			return "", err
		}
	}

	file, err := os.Create(storageDir + fileName)
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
	var data DownloadPayload
	err := json.NewDecoder(r.Body).Decode(&data)
	if err != nil {
		fmt.Println("Invalid request body", err)
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	filename, err := downloadFile(data)
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
