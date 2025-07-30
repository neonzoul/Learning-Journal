// Select HTML elements and store them in variables
const serverSelect = document.getElementById('server-select');
const itemIdsInput = document.getElementById('item-ids-input');
const searchButton = document.getElementById('search-button');
const resultsContainer = document.getElementById('results-container');

// Log elements to console to verify they are accessible
console.log('Server Select Element:', serverSelect);
console.log('Item IDs Input Element:', itemIdsInput);
console.log('Search Button Element:', searchButton);
console.log('Results Container Element:', resultsContainer);

// City list - same as in the Node.js version
const cityList =
    'Lymhurst,Bridgewatch,Caerleon,Martlock,Thetford,Fort Sterling';

// Function to process price data (adapted from Node.js version)
function processPriceData(priceDataArray) {
    const itemData = {};
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

// Function to display price report in HTML (replaces console.log version)
function displayPriceReport(itemData) {
    const allCities = cityList.split(',');
    let htmlContent = '';

    // Loop through each item
    for (const itemId in itemData) {
        htmlContent += `<div class="item-report">`;
        htmlContent += `<h3>Price Report for ${itemId}</h3>`;
        htmlContent += `<div class="city-grid">`;

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

            htmlContent += `
                <div class="city-data">
                    <strong>${city}</strong><br>
                    Price: ${priceDisplay}<br>
                    Resets in: ${timeDisplay}
                </div>
            `;
        }

        htmlContent += `</div></div>`;
    }

    resultsContainer.innerHTML = htmlContent;
}

// Function to fetch and process price data
async function fetchPriceData() {
    const server = serverSelect.value;
    const itemIDs = itemIdsInput.value.trim();

    // Validate inputs
    if (!itemIDs) {
        resultsContainer.innerHTML =
            '<p style="color: red;">Please enter item IDs</p>';
        return;
    }

    // Show loading message
    resultsContainer.innerHTML = '<p>Loading price data...</p>';

    // Construct API URL
    const apiUrl = `https://${server}.albion-online-data.com/api/v2/stats/prices/${itemIDs}?locations=${cityList}`;

    console.log('Fetching from:', apiUrl);

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        console.log('Raw API Response:', data);

        // Process the data
        const processedData = processPriceData(data);

        // Display the results
        displayPriceReport(processedData);
    } catch (error) {
        console.error('Error fetching data:', error);
        resultsContainer.innerHTML =
            '<p style="color: red;">Error fetching price data. Please try again.</p>';
    }
}

// Add event listener to the search button
searchButton.addEventListener('click', fetchPriceData);

// Add event listener for Enter key in the input field
itemIdsInput.addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        fetchPriceData();
    }
});

// Set default value in the input field
itemIdsInput.value = 'T6_FIBER,T7_FIBER,T8_FIBER';
