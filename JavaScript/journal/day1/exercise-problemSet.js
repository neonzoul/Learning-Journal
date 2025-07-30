// ---Loop and if else-FizzBuzz----
console.log();
console.log('====FizzBuzz===');
// #input
const maxPrintNumber = 16;

// #process
// loop print number with Rules
for (let i = 1; i < maxPrintNumber; i++) {
    // number with rules
    // if %3 = "Fizz" | if %5= "Buzz" | if divisible BOTH= "FizzBuzz".
    if (i % 3 === 0 && i % 5 === 0) {
        console.log('FizzBuzz');
    } else if (i % 3 === 0) {
        console.log('Fizz');
    } else if (i % 5 === 0) {
        console.log('Buzz');
    } else {
        console.log(i);
    }
    // #outcome
    // 1 2 Fizz 4 Buzz Fizz....14 FizzBuzz
}

// ----------------

// ---Nest For Loop-Half Pyramid-----
console.log();
console.log('====Half Pyramid===');
const box = '#';
const height = 5;

// how to print box height time
// Outer loop for row
for (let i = 1; i < height; i++) {
    let row = '';
    // Inner loop to build the string for the current row
    for (let j = 1; j <= i; j++) {
        row += box;
    }
    // After inner loop finishes, print the completed row
    console.log(row);
}

// -----Reverse Half-Pyramid
for (let i = height; i < 0; i--) {
    let row = box;
}

// -----Half-Pyramid log
// console.log();
// console.log('====Half Pyramid (log)');

// for (let i = 1; i < height; i++) {
//     let row = '';
//     console.log();
//     console.log('let row = "";', 'i =', i);
//     console.log('row =', row);
//     console.log('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv');
//     for (let j = 1; j <= i; j++) {
//         console.log('---Inner loop j = 1; j <= i { row += box; }');
//         console.log('   j ', j, '| i', i);
//         row += box;
//         console.log('   row =', row);
//     }
//     console.log('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv');
//     console.log('After inside loop row =', row);
// }
