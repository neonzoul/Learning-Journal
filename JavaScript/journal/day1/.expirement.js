console.log();

// ##Javascript Modulo
console.log('==Modulo==');

// --component- pizza left calculator.
console.log('---Pizza Left Calculator---');
let pizzaPieces = 10;
let peoples = 3;
console.log(`Pizza= ${pizzaPieces} Piece(s) | People= ${peoples}`);

let pizzaLeft = pizzaPieces % peoples;

console.log('modulo:', pizzaPieces, '%', peoples);
console.log(`= Pizza Left ${pizzaLeft} piece.`);

//---------------------------------------------
// --component- 1. Checking Even || Odd numbers '// Pattern 1: The function returns a result, and the caller handles the display.
console.log();
console.log('--Checking Even || Odd numbers--');

// #input | Declare Number.
let numberForCheck = 1;

// #process | function checking number
function checkingNumber() {
    if (numberForCheck % 2 === 0) {
        return `Number: ${numberForCheck} = Even (eg. 2, 4, 6, 8, 10,...)`;
    } else {
        return `Number: ${numberForCheck} = Odd (eg. 1, 3, 5, 7, 9, 11,...)`;
    }
}
// #output | Display by call function checkingNumber.
console.log(checkingNumber());
// ----

// --component- 2. Cycling Through a Limited Set of Items
// --module- [example use for 0 and 1 to true false]
// --mudule- assigning players to one of two teams(Team A or Team B)
const teams = ['Team A', 'Team B'];
const players = 9;

for (let i = 0; i < players; i++) {
    // i % 2 will always be either 0 or 1
    const assghnedTeam = teams[i % 2];
    console.log(`Player ${i + 1} is on ${assghnedTeam}`);
}
