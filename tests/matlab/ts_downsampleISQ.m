%
%   Author:         Gianluca Iori (gianluca.iori@charite.de)
%   BSRT - Charite Berlin
%   Created on:   06/01/2017
%   Last update:  31/07/2018
%   ______________________________________________________

clear all
close all
clc

% ISQfilename = '\\charite.de\centren\#Charite-Central\BCRT\AG-raum-qbam-archiv-read\2015.003.qbam.TaCoSound\data\XtremeCT-II\femur\1977_R\C0001983.ISQ';
ISQfilename = 'E:\iorig\XtremeCT-II\1958_R\C0001799.ISQ';
outputMHDfilename = 'S:\AG\AG-Raum\Daten\Tacosound\XtremeCT-II\femur\00_resampled_data\1958_R\C0001799.mhd';

% ISQdata = sct.sctdata;
resampleddata = ISQdata.resample(ISQfilename, 10);

tmp = sctdata;
tmp.loadISQ(ISQfilename, false);
tmp.setData(resampleddata);
tmp.setVoxelsize(tmp.voxelsize*10);

tmp.save(outputMHDfilename);
