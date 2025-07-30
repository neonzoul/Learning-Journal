# ==== Problem Set ===

## Project 1 : Multi-City Price Checker

### The Requirement

We need a script that can check the market price of a single item across multiple cities in one API request. The script must then generate a comparative report showing the price and data freshness for each city.

---

### What You Are Given (The Input)

You will start with two predefined constants:

1.  The unique ID for the item you want to check (e.g., `T8_ORE`).
2.  A string containing a comma-separated list of the cities you want to query (e.g., `'Lymhurst,Bridgewatch,Caerleon,Martlock,Thetford,Fort Sterling'`).

---

### What You Must Produce (The Outcome)

Your script must fetch the data and print a formatted report to the terminal that looks similar to this (the exact prices and times will vary):

```
--- Price Report for T8_ORE ---
City: Lymhurst
  - Price: 9,800 silver
  - Last Updated: 2 hours ago

City: Bridgewatch
  - Price: 10,150 silver
  - Last Updated: 5 hours ago

City: Caerleon
  - Price: 9,990 silver
  - Last Updated: 1 hour ago

...and so on for each city that returns data.
```

---

### The Core Task

1.  Your first task is to **construct the correct API URL**. You will need to combine the item ID and the list of cities into a single URL string that the Albion Online Data Project API can understand.
2.  Create a function, `processPriceData(priceDataArray)`, that takes the array returned by the API as its parameter.
3.  Inside this function, you must loop through the array. For each object in the array, you will:
    -   Extract the city name, the `sell_price_min`, and the `sell_price_min_date`.
    -   Calculate how many hours old the data is.
    -   Store this cleaned-up information in a new, more manageable object.
4.  The function should **`return` a new array** containing your cleaned-up objects.
5.  The main part of your script will call `fetch`, pass the resulting data to your `processPriceData` function, and then loop through the final, cleaned-up array to print the formatted report shown above.

You are absolutely correct. Today is **Day 3: Arrays & Basic DOM Selection**, and your idea is the perfect project to practice this.

We will take the logic from your Node.js script and build a user interface for it in the browser. You'll create the static HTML page and then use JavaScript to select the elements you'll need to make it interactive.

It's great that you're using the `copilot` code as a reference. Even if an AI helps write it, your job as the developer is to understand it, adapt it, and make it work for your goals. Let's do that now.

---

## Project 2 : Price Checker UI Foundation

The Goal
The goal for Day 3 is to build the visual frontend for your multi_city_pricechecker script. You will create the static user interface in HTML and then write the foundational JavaScript to select the interactive elements, preparing for the next step of making them work.

The Bridge: From Node.js to the Browser
Think of your previous multi_city_pricechecker.js file as the "brain" of your application. It contains all the business logic: how to build the URL, how to fetch data, and how to process the results.

Today, you will build the "face" of your application in HTML.

In the coming days, we will copy the logic from your Node.js file into your new browser script.js file. The main difference will be that instead of using console.log to show the final report, we will use JavaScript to create and modify HTML elements to display the report directly on the webpage.

Detailed Requirements

1. The HTML File (index.html)
   Create the structure for the user interface. This file will not contain any price data itself; it is just the template.

Create an <h1> element for the title, e.g., "Albion Online Price Checker".

Create a <form> element to contain your inputs.

Server Selection: Inside the form, create:

A <label> with the text "Server:".

A <select> element with an id like server-select. Inside the <select>, add three <option> elements with the values east, west, and europe.

Item ID Input: Inside the form, create:

A <label> with the text "Item IDs:".

An <input type="text"> with an id like item-ids-input. Give it a placeholder attribute like "e.g., T4_FIBER,T5_HIDE".

Submit Button: Inside the form, create a <button> with an id like search-button. The button text should be "Get Prices".

Results Container: After the <form>, create an empty <div> with an id like results-container. This is where the price report will be displayed later.

Link Your Script: At the bottom of your <body> section, add <script src="script.js" defer></script>.

2. The JavaScript File (script.js)
   For today, the only task in this file is to select the HTML elements you just created and verify that you have access to them.

Using document.querySelector() or document.getElementById(), get a reference to the following four elements and store each one in its own const variable:

The server <select> element.

The item ID <input> element.

The search <button>.

The results <div>.

Use console.log() to print each of these four variables to the browser's developer console. When you open your index.html file in the browser and check the console, you should see the HTML elements logged out. This confirms your JavaScript can see and access your HTML.
