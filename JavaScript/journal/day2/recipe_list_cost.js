// == Pre-Day3 ==
// have array of craft_recipe {item: 'name', city: 'city', price: p; } display each

// #input | Declare Array of Data.
// [[Factory Function Method to create Array]]
// create function for create Array object.
function createMaterial(name, city, price) {
    return { name, city, price };
}

// Array data with call createMaterial funtion input detail as argument.
const materailList = [
    createMaterial('T4_METALBAR', 'Fort Sterling', 850),
    createMaterial('T4_LEATHER', 'Bridgewatch', 620),
    createMaterial('T4_ORE', 'Fort Sterling', 255),
    createMaterial('T4_HIDE', 'Bridgewatch', 180),
    createMaterial('T3_METALBAR', 'Caerleon', 310),
];

console.log(`Use total ${materailList.length} materails`);

// #outcome
// Display loop each pieces of materail loop with materailList.length
for (i = 0; i < materailList.length; i++) {
    console.log(
        `Materail : ${materailList[i].name} | City: ${materailList[i].city} | Price: ${materailList[i].price} silver`
    );
}
