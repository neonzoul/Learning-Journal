// TEST key: NQXPOMAFTRHLZGECYJIUWSKDVB

package main

import (
	"cs50"
	"fmt"
	"os"
)

func main() {
	// implement int main(int argc, string argv[]) from C
	argc := len(os.Args)
	argv := os.Args
	
	
	fmt.Println("hello, world")
	// name := cs50.GetString("Name: ")
	// fmt.Printf("hello, %s", name)
	
	if argc != 2 {
		fmt.Println("Usage: ./substitution key")
		os.Exit(1) // return 1; in C that mean exite with status code 1
	}

	// Argument report. 
	fmt.Println("argc:", argc)
	fmt.Printf("arv[0]: %s | argv[1]: %s \n", argv[0], argv[1])

	if !validate_key(argv[1]) {
		// Error messages for invalid key print inside validate_key
		os.Exit(1)
	}

	// validate pass
	plaintext := cs50.GetString("plaintext: ");
	fmt.Println("text = ", plaintext)

}

// --component-- validate key
func validate_key(key string) bool {
	// check 1: lenght must be 26
	if len(key) != 26 {
		fmt.Println("Key must contain 26 characters.")
		return false
	}

	// Frequency array to check for duplicates
	freq := make([]int, 26)

	for i := 0; i < 26; i++ {
		c := key[i]

		// check 2: all must be alphabetic
		if ( c < 'A' || c > 'Z') && (c < 'a' || c > 'z') {
			fmt.Println("Key must only contain alphabetic characters. ")
			return false
		}

		// check 3: No duplicate characters (case-insensitive)
		index := int((c | 0x20) - 'a') // convert to lowercase
		if freq[index] > 0 {
			fmt.Println("Key must not contain repeated characters.")
			return false
		}
		freq[index]++
	}
	return true
}