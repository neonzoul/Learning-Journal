// copilot
console.log('==multi_city_pricechecker Node==');

// #input Construct API URL
// State handler API url
let server = 'east'; // pick one US=west | Asia=east | Europe= europe.
let itemID = 'T6_FIBER,T7_FIBER,T8_FIBER';
const cityList =
    'Lymhurst,Bridgewatch,Caerleon,Martlock,Thetford,Fort Sterling';

const apiUrl = `https://${server}.albion-online-data.com/api/v2/stats/prices/${itemID}?locations=${cityList}`;

//[[test -- construct api url]]
console.log('Construct API URL: ');
console.log(apiUrl);

// #process
// - function processPriceData(data) - processes the raw API response
function processPriceData(priceDataArray) {
    const itemData = {};

    // Get all unique cities from the city list
    const allCities = cityList.split(',');

    for (let i = 0; i < priceDataArray.length; i++) {
        const cityData = priceDataArray[i];

        // Only process quality 1 (normal) items
        if (cityData.quality === 1) {
            const itemId = cityData.item_id;
            const city = cityData.city;

            // Initialize item data if it doesn't exist
            if (!itemData[itemId]) {
                itemData[itemId] = {};
                // Initialize all cities with default "no data" values
                for (let j = 0; j < allCities.length; j++) {
                    itemData[itemId][allCities[j]] = {
                        price: '-',
                        hoursAgo: '-',
                    };
                }
            }

            // If the item has valid price data, update it
            if (cityData.sell_price_min > 0) {
                const price = cityData.sell_price_min;
                const lastUpdatedString = cityData.sell_price_min_date;

                // Calculate how many hours ago the data was updated
                const lastUpdatedDate = new Date(lastUpdatedString);
                const currentDate = new Date();
                const timeDifferenceMs = currentDate - lastUpdatedDate;
                const hoursAgo = Math.floor(
                    timeDifferenceMs / (1000 * 60 * 60)
                );

                itemData[itemId][city] = {
                    price: price,
                    hoursAgo: hoursAgo,
                };
            }
        }
    }

    return itemData;
}

// Function to format and display the report
function displayPriceReport(itemData) {
    // Get all cities from the city list
    const allCities = cityList.split(',');

    // Loop through each item
    for (const itemId in itemData) {
        console.log(`\n--- Price Report for ${itemId} ---`);

        // Loop through all cities for this item
        for (let i = 0; i < allCities.length; i++) {
            const city = allCities[i];
            const cityData = itemData[itemId][city];

            let priceDisplay = cityData.price;
            let timeDisplay = cityData.hoursAgo;

            // Format price if it's a number
            if (typeof cityData.price === 'number') {
                priceDisplay = `${cityData.price.toLocaleString()} silver`;
                const hoursLeft = 24 - cityData.hoursAgo;
                if (hoursLeft > 0) {
                    timeDisplay = `${hoursLeft} hours left`;
                } else {
                    timeDisplay = 'Expired';
                }
            }

            console.log(
                `City: ${city}  | Price: ${priceDisplay}  | Resets in: ${timeDisplay}`
            );
        }
    }
}

// #output - Main execution
// Fetch data and process it
fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
        console.log('\n=== Raw API Response ===');
        console.log(data);

        // Process the data using our function
        const processedData = processPriceData(data);

        // Display the formatted report
        displayPriceReport(processedData);
    })
    .catch((error) => {
        console.error('Error fetching data: ', error);
    });
