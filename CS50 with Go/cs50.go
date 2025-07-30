package cs50

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// GetChar prompts the user and returns a single character
func GetChar(prompt string) rune {
    reader := bufio.NewReader(os.Stdin)
    for {
        fmt.Print(prompt)
        input, _ := reader.ReadString('\n')
        input = strings.TrimSpace(input)
        if len(input) == 1 {
            return rune(input[0])
        }
        fmt.Println("Invalid input. Please enter a single character.")
    }
}

// GetDouble prompts the user and returns a double (float64)
func GetDouble(prompt string) float64 {
    reader := bufio.NewReader(os.Stdin)
    for {
        fmt.Print(prompt)
        input, _ := reader.ReadString('\n')
        input = strings.TrimSpace(input)
        num, err := strconv.ParseFloat(input, 64)
        if err == nil {
            return num
        }
        fmt.Println("Invalid input. Please enter a number (double).")
    }
}

// GetFloat prompts the user and returns a float32
func GetFloat(prompt string) float32 {
    reader := bufio.NewReader(os.Stdin)
    for {
        fmt.Print(prompt)
        input, _ := reader.ReadString('\n')
        input = strings.TrimSpace(input)
        num, err := strconv.ParseFloat(input, 32)
        if err == nil {
            return float32(num)
        }
        fmt.Println("Invalid input. Please enter a number (float).")
    }
}

// GetInt prompts the user and returns an integer
func GetInt(prompt string) int {
    reader := bufio.NewReader(os.Stdin)
    for {
        fmt.Print(prompt)
        input, _ := reader.ReadString('\n')
        input = strings.TrimSpace(input)
        num, err := strconv.Atoi(input)
        if err == nil {
            return num
        }
        fmt.Println("Invalid input. Please enter an integer.")
    }
}

//---generate when need to use---//

// GetLong prompts the user and returns a long
func GetLong(prompt string) int64 {
    reader := bufio.NewReader(os.Stdin)
    for {
        fmt.Print(prompt)
        input, _ := reader.ReadString('\n')
        input = strings.TrimSpace(input)
        num, err := strconv.ParseInt(input, 10, 64)
        if err == nil {
            return num
        }
        fmt.Println("Invalid input. Please enter a long integer.")
    }
}

// GetLongLong prompts the user and returns a long_long [Prompt when need to use.]

// GetString prompts the user and returns a string
func GetString(prompt string) string {
    reader := bufio.NewReader(os.Stdin)
    fmt.Print(prompt)
    input, _ := reader.ReadString('\n')
    return strings.TrimSpace(input)
}
