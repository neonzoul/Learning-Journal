package main

import (
	"cs50"
	"fmt"

	"rsc.io/quote"
)

func main() {
	fmt.Println("hello, world")
	fmt.Println(quote.Go())
	
	name := cs50.GetString("Name? : ")
	fmt.Printf("hello, %s \n", name)

	n := cs50.GetInt("number: ")
	fmt.Printf("You entered: %d kub\n", n)

	c := cs50.GetChar("char: ")
	fmt.Printf("You entered: %c 😁\n", c)

	f := cs50.GetFloat("Float Number: ")
	fmt.Printf("You entered: %.2f ☺ \n", f)

	l := cs50.GetLong("Long Number _max 19 digits: ")
	fmt.Printf("You entered: %d 😲🤑 \n", l)
}