package main

import (
	"cs50"
	"fmt"
)

func main() {
	fmt.Println("hello, world")
	name := cs50.GetString("Name: ")
	fmt.Println("hello, ", name)
}