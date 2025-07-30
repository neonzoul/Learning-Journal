console.log('==crefting_recipe_cost_calculator Node==');
// #input | Declare input value
// meterialList Array
const materialList = [
    { name: 'Iron Bars T4', quantity: 16, unitValue: 250 },
    { name: 'Leather T5', quantity: 8, unitValue: 950 },
    { name: 'Uncommon Glimmer', quantity: 1, unitValue: 12000 },
];

// #process |
function calculateMeterailCost(materials) {
    // State handler Totle Materials count and cost.
    let materialsCount = 0;
    let materialsCost = 0;

    // --Find materailsCount and Cost
    // [[use for loop for scable using maximun time with materials.lenght]]
    for (i = 0; i < materials.length; i++) {
        materialsCount += materials[i].quantity;
        materialsCost += materials[i].unitValue * materials[i].quantity;
    }

    // return single object with the raw data
    return {
        materialsCount: materialsCount, // return all amout of materials
        materialsCost: materialsCost, // return total cost
    };
}

// #outcome |
// call function calculateMeterailCos to get the result with meterialList
const result = calculateMeterailCost(materialList);

console.log('--- Crafting Cost Report ---');
// Display materails and quantity
for (i = 0; i < materialList.length; i++) {
    console.log(`- ${materialList[i].name}: ${materialList[i].quantity} ea`);
}
// Display result. (each object.)
console.log('----------------------------');
console.log(`Total Materials: ${result.materialsCount} ea`);
const formatter = new Intl.NumberFormat('en-US');
console.log(
    `Total Material cost: ${formatter.format(result.materialsCost)} silver`
);

// display finished status
console.log('::crefting_recipe_cost_calculator finished [/]');

// [[expirement-inside funtion calculateMeterailCost- hook each pieces of meterials(object)]]
//--------💡can uncomment after this line.
// // display every array with for loop.
// for (i = 0; i < 3; i++) {
//     // solid i < 3 because materailList have 3 object.

//     console.log(
//         `   ::materails
//     ${materials[i].name} | ${materials[i].quantity} ea | ${materials[i].unitValue} silver `
//     );
// }
