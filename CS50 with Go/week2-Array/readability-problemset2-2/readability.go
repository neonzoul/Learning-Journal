package main

import (
	"cs50"
	"fmt"
	"math"
	"unicode"
)

func main() {
	//// ------- Greeting ----------
	// fmt.Println("hello, world")
	// name := cs50.GetString("Name : ")
	// fmt.Printf("hello, %s \n", name)	
    // fmt.Println()

	///// -----Readability Display----
	text := cs50.GetString("Book Detail : ")

    colemanIndex := int(math.Round(textCounter(text)))
    fmt.Printf("colemanIndex = %d\n", colemanIndex)
	
    if colemanIndex < 1 {
        fmt.Println("Before Grade 1")
    } else if colemanIndex >= 16 {
        fmt.Println("Grade 16+")
    } else {
        fmt.Printf("Grade %d\n", colemanIndex)
    }
}



// ---Tool- Count the number of letters, words, and sentences in the text
func textCounter(text string) float64 {
    letterCount := 0
    wordCount := 1
    sentenceCount := 0

    for _, ch := range text {
        if unicode.IsLetter(ch) {
            letterCount++
        } else if unicode.IsSpace(ch) {
            wordCount++
        } else if ch == '.' || ch == '!' || ch == '?' {
            sentenceCount++
        }
    }
    return computeColeman(letterCount, wordCount, sentenceCount)
}

// Compute Coleman-Liau index
func computeColeman(letterCount, wordCount, sentenceCount int) float64 {
    l := float64(letterCount) / float64(wordCount) * 100.0
    s := float64(sentenceCount) / float64(wordCount) * 100.0
    return 0.0588*l - 0.296*s - 15.8
}