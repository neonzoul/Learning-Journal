==== Problem Set (Project) ====

# Project 1: The Cost Calculator

```
The Goal
Your goal is to write a simple Node.js script that calculates the total cost of a stack of items. This will require you to create and use a single, reusable function.

The Requirements
Create a new file named calculate_cost.js.

Inside the file, define a function named calculateTotalCost.

This function must accept two parameters: itemPrice and quantity.

Inside the function, multiply the itemPrice by the quantity and use the return keyword to send back the final result.

Outside the function, create two const variables to hold a sample price and quantity (e.g., const pricePerItem = 250; and const numberOfItems = 100;).

Call your calculateTotalCost function, passing your two variables as arguments. Store the value that the function returns in a new constant called totalCost.

Finally, use console.log() to print a descriptive message to the terminal, like: "Total cost for 100 items at 250 silver each is 25000 silver."

How to Run
Save the file and run it from your terminal with the command: node calculate_cost.js.

```

---

# Project 2: Crafting Profit Calculator

```

### The Goal
Write a function that calculates the net profit or loss from crafting an item and selling it on the market, after accounting for the market tax.

### The Requirements
1.  Create a new file named `crafting_profit.js`.
2.  Define a function named `calculateProfit`.
3.  The function must accept three **parameters**: `materialCost`, `marketPrice`, and `marketTaxRate`.

4.  **Inside the function, perform these calculations:**
    * Calculate the amount of silver paid in tax from the sale.
    * Calculate your revenue after the tax is deducted.
    * Calculate your final profit (or loss).

5.  The function must **`return` an object** that contains two pieces of information:
    * `profitValue`: The final calculated profit.
    * `status`: A string that is either `'Profit'`, `'Loss'`, or `'Break Even'`, determined by an `if/else` statement.

6.  **Outside the function:**
    * Create `const` variables for a sample crafting scenario (e.g., `materialCost = 8500`, `marketPrice = 10000`, `marketTaxRate = 0.065`).
    * Call your `calculateProfit` function with these variables and store the returned object in a constant named `result`.
    * Use `console.log` to print a descriptive message using the properties from your `result` object, like: `Status: Profit, Amount: 850 silver`.

```

# Project 3: Crafting Recipe Cost Calculator

````
-----

### The Requirement

We need a script that can process a list of materials required for a crafting recipe and calculate the total cost to acquire all of them.

-----

### What You Are Given (The Input)

You will start with a predefined array of objects. Each object represents a material needed for the recipe.

```
javascript
const materialList = [
{ name: 'T4 Iron Bars', quantity: 16, unitValue: 250 },
{ name: 'T5 Leather', quantity: 8, unitValue: 950 },
{ name: 'Uncommon Glimmer', quantity: 1, unitValue: 12000 }
];
```

---

### What You Must Produce (The Outcome)

Your script must print a formatted report to the terminal that looks exactly like this:

```
--- Crafting Cost Report ---

-   T4 Iron Bars: 16
-   T5 Leather: 8
-   Uncommon Glimmer: 1


Total Materials: 25
Total Material Cost: 23,600 silver
```

---

### The Core Task

Your task is to create a function, `calculateMaterialCost(materials)`, that takes the `materialList` array as its only parameter.

This function must process the array and **`return` an object** containing the calculated totals (e.g., `{ totalMaterialCount: ..., totalCost: ... }`).

The main part of your script will then call this function and use the returned object to print the formatted report shown above.

````

# Priject 4: recipe_list_cost.js

```
// == Pre-Day3 ==
// have array of craft_recipe {item: 'name', city: 'city', price: p; } display each
```

# Project 5 (advance): Live Price Crafting Calculator

Excellent. This research document gives you everything you need. Let's create a project that uses this information to bring your `crafting_profit` calculator to life with real data.

---

### The Goal

Your goal is to use the `fetch` API to get the live market price of "T4 Iron Bars" from Caerleon (Asia server) and then use that price to calculate the total value of a stack of those bars.

This project will combine everything you've learned about functions with the new `fetch` API.

---

### Step-by-Step Guide

#### **Step 1: Create Your File and Fetch the Data**

1.  Create a new file named `live_price_calculator.js`.
2.  Use the exact URL from **Section 1.1** of your research to define a constant.
3.  Use the `fetch` pattern to request the data. For now, just `console.log` the data you get back to see its structure.

<!-- end list -->

```javascript
// The URL from your research document
const apiUrl =
    'https://east.albion-online-data.com/api/v2/stats/prices/T4_METALBAR?locations=Caerleon';

fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
        // For now, just print the raw data to see it
        console.log('--- Raw Data Received ---');
        console.log(data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
```

Run this with `node live_price_calculator.js`. You should see the JSON data from your document printed in the terminal.

#### **Step 2: Extract the Specific Price**

Now, modify your `fetch` code. Inside the `.then(data => { ... })` block:

1.  The data is an array, so access the first element: `data[0]`.
2.  From that object, get the minimum sell price. According to **Section 1.2** of your document, this is the `sell_price_min` property.
3.  Store this price in a constant called `livePrice`.
4.  `console.log` just the `livePrice` to make sure you extracted it correctly.

#### **Step 3: Calculate the Value**

1.  Create a simple function at the top of your file: `function calculateStackValue(unitPrice, quantity) { return unitPrice * quantity; }`.
2.  Back inside your `.then()` block, after you get the `livePrice`, call this function. Use the `livePrice` and a sample quantity (e.g., `250`) as arguments.
3.  Store the result in a constant called `totalStackValue`.

#### **Step 4: Display the Final Result**

Inside the `.then()` block, add a final `console.log` that prints a formatted message, like:
`"Live price for T4 Iron Bars in Caerleon is [livePrice] silver. The total value of a 250 stack is [totalStackValue] silver."`

---

### The Complete Code Structure

Here is a template you can use to assemble the final script.

```javascript
function calculateStackValue(unitPrice, quantity) {
    return unitPrice * quantity;
}

const apiUrl =
    'https://east.albion-online-data.com/api/v2/stats/prices/T4_METALBAR?locations=Caerleon';

console.log('Fetching live price data...');

fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
        // --- Your code for Steps 2, 3, and 4 goes here ---
        // 1. Extract the price from the 'data' object.
        // 2. Call your calculateStackValue function.
        // 3. Print the final, formatted result to the console.
    })
    .catch((error) => {
        console.error('Error fetching data:', error);
    });
```
