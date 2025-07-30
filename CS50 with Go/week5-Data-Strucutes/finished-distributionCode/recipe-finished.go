package main

import (
	"fmt"
	"math/rand"
	"strings"
)

// RecipeComponent defines a node in out recipe's dependency tree.
// Each component can be made of two sub-components, forming a binary tree structure,
// analogous to a person having two parents in the CS50 'Inheritance' problem.
type RecipeComponent struct {
	// SubComponents is a slice of pointers to the child components.
	// This will be nil for base ingredients.
	SubComponents []*RecipeComponent
	// PrimaryIngredient is a human-readable name for the component.
	PrimaryIngredient string
}

// COMPLEXITY determines the total depth of the recipe tree.
// A complexity of 3 means a Final Dish, its Sub-Components, and their base ingredients.
const COMPLEXITY = 3 

// INDENT_LENGTH defines the number of spaces for each level of indentation when printing the tree.
const INDENT_LENGTH = 4 

// main is the entry point of the application.
func main() {
	// [[just say hello.🤙]]
	fmt.Println("hello, world")
	// seed the random number generator to ensure different results on each run.
	// Using the current time is a common practice for getting a unique seed.

	// Generate the entire recipe structure recursively.
	finalDish := CreateRecipe(COMPLEXITY)

	// Traverse the generated structure and print it to the console.
	PrintRecipe(finalDish, 0)
}

// CreateRecipe recursively builds a component and its dependendies based on the
// specified complexity level.
func CreateRecipe(complexity int) *RecipeComponent {
	// Allocate memory for a new component.
	newComponent := &RecipeComponent{}

	// Recursice Step: If the complexity is greater than 1, this component
	// if mad of ther, simpler components.
	if complexity > 1 {
		// Recursively create the two sub-components that make up the current one.
		subComponent0 := CreateRecipe(complexity - 1)
		subComponent1 := CreateRecipe(complexity - 1)
		
		// Assign the newly created children to the current component's SubComponents slice.
		newComponent.SubComponents = append(newComponent.SubComponents, subComponent0, subComponent1)

		// The name of complex component is derived from its children.
		newComponent.PrimaryIngredient = subComponent0.PrimaryIngredient + " & " + subComponent1.PrimaryIngredient
	} else {
		// Base Case: A complexity of 1 or less represents a fundamental ingredient that can't be broken down further.
		//its SubComponent slice remains nil, terminating the recursion for this branch.
		newComponent.SubComponents= nil
		
		// Assign a random base ingredient from out predefined list.
		newComponent.PrimaryIngredient = randomIngredient()
	}

	// Return the pointer to the fully constructed component.
	return newComponent
}


// PrintRecipe traverses the recipe tree depth-first and prints each component's details with appropriate indentation.
func PrintRecipe(component *RecipeComponent, level int) {
	// Base Base for recursion: stop if we encounter a nil pointer.
	// This happens when a component has no more sub-components.
	if component == nil {
		return
	}
	
	// Apply indentation based on the current depth in the tree.
	fmt.Print(strings.Repeat(" ", level*INDENT_LENGTH))

	// Print the component's details.
	if level == 0 {
		fmt.Printf("Final Dish (level %d): made of %s\n", level, component.PrimaryIngredient)
		} else {
			fmt.Printf("Sub-Coomponent (Level %d): made of %s\n", level, component.PrimaryIngredient)
		}

		// If the current component has children, recursively call PrintRecipe for each one.
		if component.SubComponents != nil {
			PrintRecipe(component.SubComponents[0], level+1)
			PrintRecipe(component.SubComponents[1], level+1)
		}
}

// randomIngredient is a utility function that retuerns a random base ingredient.
func randomIngredient() string {
		ingredients := []string{"Flour", "Sugar", "Eggs", "Butter", "Chocolate"}
		return ingredients[rand.Intn(len(ingredients))]
}