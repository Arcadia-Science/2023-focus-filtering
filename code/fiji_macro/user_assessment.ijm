
// Allow the user to scroll through slices
waitForUser("Scroll through the slices and press OK when ready to begin the in-focus check. Please do not change settings.");

// Generate a random 6-digit ID
randomID = floor(random * 1000000);
while (randomID < 100000) {
    randomID = floor(random * 1000000);
}

// Open a file with the generated ID in the filename
filename = "/Users/galogarciaiii/projects/edge-detection/focus_results_" + randomID + ".csv";
f = File.open(filename);

// Write the header to the file
print(f, "Frame,InFocus");

// Loop through each slice in the stack
for (i = 1; i <= nSlices; i++) {
    // Show the ith slice
    setSlice(i);

    // Draw the frame number on the top-left corner of the image
    setColor(255, 255, 255); // White color
    setFont("Arial", 16, "Bold");
    drawString("" + i, 10, 20); // Draw number at position (10,20)

    // Update display
    updateDisplay();

    // Ask the user if the slice is in focus
    result = getBoolean("Is this slice(" + i + ") in focus?");

    // Record the result in the CSV file
    print(f, i + "," + result);
}

// File will be automatically closed when the macro exits
