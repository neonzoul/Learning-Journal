package main

import (
	"cs50"
	"fmt"
	"math"
	"unicode"
)

////////////////////////////////////////////////////////////

func main() {
	///----Display----///
	/// (Input) ask text to user and hold it.
	text := cs50.GetString("Text: ")

	/// (ProCess) hold colmanIndex Call func name text_counter(text) round them
	colemanIndex := int(math.Round(text_counter(text)))
	fmt.Printf("colmanIndex = %d\n", colemanIndex)


	/// (outuT)Print The grade level // use colenamIndex make condition and print grade
		// if < 1 "Before Grade 1" | else if >= 16 "Grade 16++" | else "Grade %d\n" colemanIndex
	if colemanIndex < 1 {
		fmt.Println("Before Grade 1")
	} else if colemanIndex >= 16 {
		fmt.Println("Grade 16++")
	} else {
		fmt.Printf("Grade %d\n", colemanIndex)
	}

}
////////////////////////////////////////////////////////////
// Count ther number of letters, word and sentences in the text
// ---Tool- {Count} the number of letterCount, wordCount, and sentenceCount send text to Compute
func text_counter(text string) float64 {
	
	//products holder
	var letterCount int = 0
	var wordCount int = 1
	var sentenceCount int = 0

	// use Go tool -> for..range(text)  ] {if .... = ... _++ | else if .... _++ | else if ... _++ } 
	for _, ch := range text {
		if unicode.IsLetter(ch) {
			letterCount++
		} else if unicode.IsSpace(ch) {
			wordCount++
		} else if ch == '.' || ch == '!' || ch == '?' {
			sentenceCount++
		}
	}
	// return product
	return computeColeman(letterCount, wordCount, sentenceCount)

}	

// Compute Coleman-Liau index
//input Product from text_counter as int (float64)
func computeColeman(letterCount, wordCount, sentenceCount int) float64 {
	// l = letter / wordCount * 100.0 | s = sentence / word * 100.0 (don't forget use fload64) 
	l := float64(letterCount) / float64(wordCount) * 100.00
	s := float64(sentenceCount) / float64(wordCount) * 100.0
	// compute 0.0588*l - 0.296*s - 15.8 return
	return 0.0588*l - 0.296*s - 15.8
}