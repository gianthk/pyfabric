%tacoscript_extract_XCT_neck
%   preprocessing of XCT data:
% 
%       1.  read crop and rotate info from master table; read 3D transformation matrix 
%           that aligns the femoral neck axis with the Z-axis
%       2.  automatic read neck portion of HR-pQCT (.XCT) file 
%       (NO) 3.  apply 3D transformation matrix -> align femoral neck axis with the Z-axis
%       (NO) 4.  crop neck portion
%       5.  writes neck image to meta image data (.mhd)
%   ______________________________________________________
%
%   Author:         Gianluca Iori (gianluca.iori@charite.de)
%   BSRT - Charite Berlin
%   Created on:   23/01/2018
%   Last update:  12/07/2018
%   ______________________________________________________
%
%   See also SPHEREFIT, REGIONPROPS, MHDWRITE
%   ______________________________________________________

clear all
close all
clc

graphics = false;
currentdir = pwd;

filename_master = 'S:\AG\AG-Raum\Daten\Tacosound\tacosound_master_femurneck.csv';

sample = 1;
%% load master table
if isempty(filename_master)
    [FILENAME, PATHNAME] = uigetfile('*.csv;*.CSV', 'Select master table');
    cd(currentdir);
    filename_master = [PATHNAME FILENAME];
end

master = medtooltable.readtable(filename_master);
cd(currentdir);
%% eval all samples
% samples=[25:25];
for sample = 1:length(master.specimen)
% for sample = 1:4
%     for sample = fallleft_ID(1:end)'
%     for sample = stanceleft_ID(2:end)'
% for sample = mechtest_ID(2:end)'
%     for sample = left_ID(1:end)'

    neck_path = 'S:\AG\AG-Raum\Daten\Tacosound\XtremeCT-II\femur\20_HRdata\00_neck\';
    mhd_FILENAME = [neck_path master.specimen{sample}(1:end-2) '.mhd'];
    
%     if exist(mhd_FILENAME)==2
%         fprintf('%s exists already.\n', mhd_FILENAME);
%         continue
%     end
    
    % run flag in mastertable
    if ~master.run(sample), continue; end
    
    fprintf('evaluate specimen: \t%s\n', char(master.fileISQ{sample}));

    txt_FILENAME = char(master.fileMHD{sample});
    txt_FILENAME = [txt_FILENAME(1:end-4) '_neck.txt'];
    %% 1.  read 3D transformation matrix  that aligns the femoral neck axis with the Z-axis
    % load MHD file (only header)
    % rotdata = sctdata;
    % rotdata.load(filename2ussraum([master.neck_rot{sample}]));
    
    % write transformation matrix into affine3D transformation object
    % tform_neck = affine3d(reshape(rotdata.transformmatrix, 4, 4));
    %% 2.  automatic read neck portion of HR-pQCT (.XCT) file
    HRdata = sctdata;
    
    % read ISQ header without loading the data (get voxelsize!)
    HRdata.loadISQ(master.fileISQ{sample}, false); 
    x_0 = double(round(master.neck_crop1x0(sample)/HRdata.voxelsize(1)));     x_d = double(round(master.neck_crop1xd(sample)/HRdata.voxelsize(1)));
    y_0 = double(round(master.neck_crop1y0(sample)/HRdata.voxelsize(2)));     y_d = double(round(master.neck_crop1yd(sample)/HRdata.voxelsize(2)));
    z_0 = double(round(master.neck_crop1z0(sample)/HRdata.voxelsize(3)));     z_d = double(round(master.neck_crop1zd(sample)/HRdata.voxelsize(3)));
    
    HRdata.loadISQ(master.fileISQ{sample}, x_0, y_0, z_0, x_d, y_d, z_d);
    
    % write HR neck data and midplanes
    HRdata.writeMidplanes(mhd_FILENAME);

    HRdata.offset = [x_0 y_0 z_0];
    HRdata.save(mhd_FILENAME);
end