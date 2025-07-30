// #input (state)
console.log('-Initailize-');
let numberA = 0;
let numberB = 0;
// display Initail state.
console.log(`numberA= ${numberA} | numberB= ${numberB}`);

// #process (calculate)
function numberCalulate(numberA, numberB) {
    console.log('...running function to update state...');
    numberA = 3;
    numberB = 5;
    console.log(`numberA= ${numberA} | numberB= ${numberB}`);
    console.log('C style | numA= %d numB= %i', numberA, numberB);
    return numberA + numberB;
}

// #Out-Put (display terminal)
console.log(`numberA= ${numberA} | numberB= ${numberB}`);
console.log(numberCalulate());
console.log(`numberA= ${numberA} | numberB= ${numberB}`);
