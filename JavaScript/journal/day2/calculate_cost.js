// --- == calculate_cost.js ==
console.log('==calculate_cost Node==');
const pricePerItem = 250;
const numberOfItems = 10;

function calculate_cost(itemPrice, quantity) {
    let calculateTotalCost = 0;

    console.log(`   Price: ${pricePerItem} 🥈`);
    console.log(`   Quantiy: ${numberOfItems} ea`);
    calculateTotalCost = itemPrice * quantity;
    return calculateTotalCost;
}

console.log(
    'Total Cost: ' + calculate_cost(pricePerItem, numberOfItems) + ' 🥈'
);
console.log('calcualte_cost finished [/]');
