package main

import (
	"cs50"
	"fmt"
)

var h int

func main (){
	// get pyramid's actual height (loop until the number is positive integer)
	//do while loop in C
	for {
		h = cs50.GetInt("Actual Height= ")
		if h >= 1 {
			break
		}
	}

	//print rows
	for r := 0; r < h; r++ {
		printRow(r + 1)
	}
}

// print clumns
func printRow(coll int) {
	for sp := h; sp > coll; sp-- {
		fmt.Print(" ")
	}
	for bri := 0; bri < coll; bri++ {
		fmt.Print("#")
	}
	fmt.Println()
}