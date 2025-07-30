package main

import (
	"cs50"
	"fmt"
)

func main (){
	
	// prompt for input
	creditNumber := cs50.GetLong("creditnumber: ")
	fmt.Printf("Credit Number = %d \n", creditNumber)
	
	// calculate checksum
	sumCheck := 0
	workingNumber := creditNumber
	digits := 0
	position := 1

	// loop umtil working_number > 0
	for workingNumber > 0 {
		lastDigit := int(workingNumber % 10)

		if position%2 == 0 {
			product := lastDigit * 2
			sumOfDigits := (product / 10) + (product % 10)
			fmt.Printf("Position %d (from right) has value: %d | product =%d \n | sum of digit = %d -> Adding to sum\n", position, lastDigit, product, sumOfDigits)
			sumCheck += sumOfDigits
		} else {
			fmt.Printf("Position %d | value: %d -> Adding to sum\n", position, lastDigit)
			sumCheck += lastDigit
		}

        workingNumber = workingNumber / 10
        digits++
        position++
    }
    fmt.Println("endloop---")
    fmt.Printf("Total digits = %d\n", digits)
    fmt.Printf("Final Checksum = %d\n\n", sumCheck)

    // Check invalid
    if sumCheck%10 == 0 {
        fmt.Println("Yee! that's credit card for sure now let me see what is your card ^_^, Pls wait a second.")

        // ----Define start 2 digit----
        startDigitsDivisor := int64(1)
        for i := 0; i < digits-2; i++ {
            startDigitsDivisor *= 10
        }
        startDigits := int(creditNumber / startDigitsDivisor)

        // ----start check card----
        // AMEX : 15 digits, start 34 || 37
        if digits == 15 && (startDigits == 34 || startDigits == 37) {
            fmt.Println("AMEX")
        } else if digits == 16 && (startDigits >= 51 && startDigits <= 55) {
            // MasterCard: 16 digits, start 51-55
            fmt.Println("MASTERCARD")
        } else if (digits == 13 || digits == 16) && (startDigits/10 == 4) {
            // Visa: 13 || 16 digit, start 4
            fmt.Println("VISA")
        } else {
            // not match any, should be another card, say "INVALID"
            fmt.Println("INVALID")
        }
    } else {
        fmt.Println("INVALID")
    }
}
