package main

import (
	"fmt"
	"io"
	"log"
	"os"
)

func main() {
//--|-- Gate keeper
	if len(os.Args) != 2 {
		log.Fatal("| Usage: go run recover.go card.raw |")
	}
//--> Get in
	fmt.Println("hello, world")

	// appear checker
	// ##Open file
	cardFile, err := os.Open(os.Args[1])
	if err != nil {
		log.Fatal(err)
	}
	defer cardFile.Close()
	// ##close file
	
//-- Main Loop and Recovery Logic
	buffer := make([]byte, 512)
	
	// Prepare output file variables
	fileCounter := 0
	var outputFile *os.File = nil

	for {
		n, err := cardFile.Read(buffer)
		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatal (err)
		}
		if n == 0 {
			break
		}

		// Check for JPEG signature
		if buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3]&0xf0) == 0xe0 {
			// If a previous JPEG file is open, close it
			if outputFile != nil {
				outputFile.Close()
			}
			// Create new fileman
			filename := fmt.Sprintf("%03d.jpg", fileCounter)
			outputFile, err = os.Create(filename)
			if err != nil {
				log.Fatal(err)
			}
			fileCounter++
		}

		// If a JPEG file is open, write the buffer to it
		if outputFile != nil {
			_, err := outputFile.Write(buffer[:n])
			if err != nil {
				log.Fatal(err)
			}
		}
	}
//--Final Cleanup
	//## close the last file After loop.
	if outputFile != nil {
			outputFile.Close()
		}
// close the input File
defer cardFile.Close()
}
//--> Out door