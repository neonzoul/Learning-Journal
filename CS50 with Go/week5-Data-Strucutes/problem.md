---
## Go Practice Problem: Recipe Breakdown

This practice problem is designed to help you master the concepts of recursion and tree-like data structures using Go. It mirrors the core logic of the CS50 "Inheritance" problem but in a more tangible context.
---

### 🎯 **Goal**

-   Write a Go program that simulates the creation of a complex recipe by combining "sub-components." This should be done using a tree-like data structure, mirroring the core concept of the CS50 "Inheritance" problem.

### 💡 **Core Concept**

-   A complex dish (like a cake) is made from less complex components (like the cake batter and the frosting). Each of these components can, in turn, be broken down further, until you reach the **"base ingredients"** (like flour, sugar, eggs), which cannot be broken down anymore.
-   This is a **Binary Tree** structure, directly analogous to the Inheritance problem:
    -   `person` -> `RecipeComponent`
    -   `parents[2]` -> `SubComponents[2]` (The two sub-components used to create the current one)
    -   `alleles[2]` -> `PrimaryIngredient` (The main ingredient of that component)
    -   `generations` -> `Complexity` (The complexity level of the recipe)

---

### 📝 **Your Task**

-   In the `recipe.go` file, complete the `CreateRecipe` function to build the recipe's data structure according to a given complexity level.
-   **`CreateRecipe(complexity int)`:** This is the core recursive function.
    -   **Recursive Step (`complexity > 1`):** If the component is still complex, you must:
        1.  Create a new `RecipeComponent`.
        2.  Call `CreateRecipe(complexity - 1)` twice to create two sub-components.
        3.  Assign these two sub-components to the `SubComponents` of the current component.
        4.  Assign a `PrimaryIngredient` to the current component (e.g., by combining the names of its children).
    -   **Base Case (`complexity <= 1`):** If the component is no longer complex (it's a base ingredient), you must:
        1.  Create a new `RecipeComponent`.
        2.  Set its `SubComponents` to `nil` (as it cannot be broken down further).
        3.  Assign it a random `PrimaryIngredient` from a predefined list.
-   You can use the Go distribution code I provided earlier as your starting point.
