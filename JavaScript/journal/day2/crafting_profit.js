// // --- == crafting_profit function. format.1 (myself without AI)==
// console.log('==crafting_profit Node==');
// // Declare input value
// let marketPrice = 100;
// let marketTaxRate = 0.0;
// let materialCost = 100;

// function calculateProfit(materialCost, marketPrice, marketTaxRate) {
//     // Declare result for store outcome.
//     let result = ``;

//     // --display input value.
//     console.log(`Market Price: ${marketPrice} silver`);
//     console.log(`Market Tax: ${marketTaxRate * 100} %`);
//     console.log(`Meterial Cost: ${materialCost} silver`);

//     // calculate Profit, Loss store in netPnl (Net Profit n Loss)
//     const taxAmount = marketPrice * marketTaxRate; // find tax amount for decude sale amount
//     const saleAmount = marketPrice - taxAmount;
//     const profitValue = saleAmount - materialCost;

//     // [[--display calculation process--]]
//     console.log(`::Sale Amout= ${saleAmount} silver`); //[[Sale Amout]]
//     console.log(`::profitValue= ${profitValue} silver`); //[[log profit]]
//     console.log('::calculate finished');

//     // condition sort by situation that hard to find [Break Even, Profit, Loss]
//     // result = ` Status: "message" , Amout: ${profitValue} ` else break even just say text.
//     if (profitValue == 0) {
//         result = `Status: Break Even ￣へ￣ `;
//         console.log(`::result = 'Status: Break Even'`); // [[log]]
//     } else if (profitValue > 0) {
//         result = `Status: Profit ψ(｀∇´)ψ | Amout: ${profitValue} silver`;
//         console.log(`::result = 'Status: Profit and Profit amout'`); // [[log]]
//     } else {
//         result = `Status: Loss (¬_¬") | Amout: ${profitValue} silver`;
//         console.log(`::result = 'Status: Loss and Loss amout'`); // [[log]]
//     }

//     // return result (`result message`) to caller;
//     console.log(':: return result'); // [log]
//     console.log();
//     return result;
// }
// console.log(calculateProfit(materialCost, marketPrice, marketTaxRate));

// // [[log report finished work]]
// console.log('::crafting_profit finished [/]');

// ===============================================================================================
// ================================#Areas for Refinement#===========================================
// == 1. Separation of Concerns : (Calculating vs. Displaying)
// == 2. Returning Data (Object) vs. a Formatted String :
// ==    implement:
// ==      - | call | using const result = calculateProfit(materialCost, marketPrice, marketTaxRate);
// ==      - | function return | array profitValue: profitValue,status: status,
// ==      - | outcome display|  console.log(`Status: ${result.status}`);
// ==                            console.log(`Amount: ${result.profitValue} silver`);
// ===============================================================================================

// [[💡uncomment after this line]]
// --- == crafting_profit function.  format 2implement ==
console.log('==crafting_profit Node==');
// Declare input value
const marketPrice = 10000;
const marketTaxRate = 0.065;
const materialCost = 8500;

function calculateProfit(materialCost, marketPrice, marketTaxRate) {
    // 1. Perform the calculations
    const taxAmount = marketPrice * marketTaxRate;
    const saleAmount = marketPrice - taxAmount;
    const profitValue = saleAmount - materialCost;

    let status = '';

    // 2. Determine the status
    if (profitValue > 0) {
        status = 'Profit';
    } else if (profitValue < 0) {
        status = 'Loss';
    } else {
        status = 'Break Even';
    }

    // 3. Return a single object with the raw data
    return {
        profitValue: profitValue,
        status: status,
    };
}

// Call the function to get the result object
const result = calculateProfit(materialCost, marketPrice, marketTaxRate);

// Now, the outside code handles all the displaying
console.log('--- Input ---');
console.log(`Market Price: ${marketPrice} silver`);
console.log(`Market Tax: ${marketTaxRate * 100}%`);
console.log(`Material Cost: ${materialCost} silver`);
console.log('--- Result ---');
console.log(`Status: ${result.status}`);
console.log(`Amount: ${result.profitValue} silver`);
console.log('::crafting_profit finished [/]');
