inputDir = getDirectory('Choose Input Directory'); 
outputDir = getDirectory('Choose Output Directory'); 

listdir = getFileList(inputDir);

for(i=0; i< listdir.length; i++) {
    print("Processing: " + inputDir + listdir[i]);
    File.makeDirectory(outputDir +listdir[i]);
    inputFolder = inputDir + listdir[i];
    // outputFolder = outputDir + listdir[i];
    outputFolder = outputDir + listdir[i].substring(0, listdir[i].length() - 1);
    inputFiles = getFileList(inputFolder);
    inputFile = inputFolder + inputFiles[0];
    
    // open image sequence
   //  print("Opening: " + inputFile);
    File.openSequence(inputFolder);
	
	// segment
	setAutoThreshold("Otsu dark");
	setOption("BlackBackground", false);
	run("Convert to Mask", "method=Otsu background=Dark");

	// get stack name
	stackname= getTitle();
    // print("Stack name: " + stackname); 

    // save as new sequence
    // print("Saving to: " + outputFolder);
    run("Image Sequence... ", "select=[stackname] dir=["+ outputFolder +"] format=TIFF name=[" + stackname + "]");
    close();
}