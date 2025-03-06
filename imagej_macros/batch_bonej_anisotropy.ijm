inputDir = getDirectory('Choose Input Directory'); 
outputDir = getDirectory('Choose Output Directory'); 
// print("Results file: " + outputDir + "bonej_results.csv"); 
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

    // save binary as new sequence
    // print("Saving to: " + outputFolder);
    run("Image Sequence... ", "select=[stackname] dir=["+ outputFolder +"] format=TIFF name=[" + stackname + "]");
    
    // bonej processing
    call("ij3d.ImageJ3DViewer.setCoordinateSystem", "false");
	call("ij3d.ImageJ3DViewer.lock");
	run("Anisotropy", "inputimage=net.imagej.ImgPlus@335efca4 directions=2000 lines=10000 samplingincrement=1.73 recommendedmin=false printradii=true printeigens=true displaymilvectors=true");
    close();
    
}
// save results table
run("Table...  ", "writecolheaders=true writerowheaders=true columndelimiter=, outputfile=["+ outputDir + "bonej_results.csv]");