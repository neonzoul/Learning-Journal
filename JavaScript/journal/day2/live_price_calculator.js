// #API sources  ..\API for Market Price Data_.md
// -- Step 1: Create Fetch Data
// use fetch pattern to request the data exact URL form section1 (API sources)

// Step 3: Create the calculation function
function calculateStackValue(unitPrice, quantity) {
    return unitPrice * quantity;
}

// -State apiUrl to handler
const apiUrl =
    'https://east.albion-online-data.com/api/v2/stats/prices/T8_ORE?locations=Bridgewatch';
//  item "Tier 4 Iron Bars" in the "Caerleon" market on the "Asia" server

console.log('Fetching live price data...');

// -fetch apiUrl
fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
        // [[display raw data]]
        console.log(data);

        // Step 2: Extract the specific price
        const livePrice = data[0].sell_price_min;
        const lastUpdated = data[0].sell_price_min_date;

        console.log('Live price extracted:', livePrice);
        console.log('Last updated:', lastUpdated);

        // Check data age
        const dataAge = new Date() - new Date(lastUpdated);
        const hoursOld = Math.floor(dataAge / (1000 * 60 * 60));
        console.log(`Data is ${hoursOld} hours old`);

        // Step 3: Calculate the value
        const quantity = 250;
        const totalStackValue = calculateStackValue(livePrice, quantity);

        // Step 4: Display the final result
        console.log();
        console.log('===Live price===');
        console.log(
            `Adamantium Ore Tier 8
        City : Lymhurst
        Price : ${livePrice} silver. 
        Last Updated: ${hoursOld} hours ago.
        The total value of a ${quantity} stack is ${totalStackValue} silver`
        );
    })
    .catch((error) => {
        console.error('Error fetching data:', error);
    });

// #outcome
