function [headerinfo, fid] = readheader(filename, leaveopen)
    %ISQREADHEADER reads Scanco ISQ file header
    %   [headerinfo] = ISQdata.readheader(filename,leaveopen)
    %   [headerinfo,fid] = ISQdata.readheader(filename,leaveopen)  reads header and leaves file open
    %   ______________________________________________________
    %
    %   Author: Gianluca Iori (gianluca.iori@charite.de)
    %   BSRT - Charite Berlin
    %   Created on:   16/11/2015
    %   Last update:  09/01/2018
    %   ______________________________________________________
    
    if ~exist('leaveopen','var') || isempty(leaveopen)
        leaveopen = false;
    end

    % FOPEN
    fid = fopen(filename,'r');                                          % open file

    if(fid == -1)                                                       % check if opening was successfull
        error(sprintf('Cannot open file %s\n',filename));
    end

    % READ HEADER
    % first bytes
    check = fread(fid,4,'char');                                        % char check[16]
    headerinfo.data_type_id = fread(fid,1,'uint');                      % int data_type
    headerinfo.type = 'int16';                                          % standard for ISQ
    headerinfo.nr_of_bytes = fread(fid,1,'uint');                       % int nr_of_bytes; /* either one of them */

    % dimensions
    fseek(fid,44,-1);                                                   % skip 44 bytes to x_dim
    headerinfo.x_dim = fread(fid,1,'uint');                             % read x_dim [pixels]
    headerinfo.y_dim = fread(fid,1,'uint');                             % read y_dim [pixels]
    headerinfo.z_dim = fread(fid,1,'uint');                             % read z_dim [slice num]
    headerinfo.x_dim_um = fread(fid,1,'uint');                          % read x_dim_um [um]
    headerinfo.y_dim_um = fread(fid,1,'uint');                          % read y_dim_um [um]
    headerinfo.z_dim_um = fread(fid,1,'uint');                          % read z_dim_um [um]
    headerinfo.slice_thickness_um = fread(fid,1,'uint');                % slice_thickness_um
    headerinfo.slice_increment_um = fread(fid,1,'uint');                % slice_increment_um
    headerinfo.slice_1_pos_um = fread(fid,1,'int');                    % slice_1_pos_um
    headerinfo.min_data_value = fread(fid,1,'int');                    % min_data_value
    headerinfo.max_data_value = fread(fid,1,'int');                    % max_data_value
    headerinfo.mu_scaling = fread(fid,1,'int');                        % mu_scaling (p(x,y,z)/mu_scaling = value [1/cm])
    headerinfo.nr_of_samples = fread(fid,1,'uint');                     % nr_of_samples
    headerinfo.nr_of_projections = fread(fid,1,'uint');                 % nr_of_projections
    headerinfo.scandist_um = fread(fid,1,'uint');                       % scandist_um
    headerinfo.scanner_type = fread(fid,1,'int');                      % scanner_type
    headerinfo.sampletime_us = fread(fid,1,'uint');                     % sampletime_us
    headerinfo.index_measurement = fread(fid,1,'int');                 % index_measurement
    headerinfo.site = fread(fid,1,'int');                              % site /* Coded value */
    headerinfo.reference_line_um = fread(fid,1,'int');                 % reference_line_um
    headerinfo.recon_alg = fread(fid,1,'int');                         % recon_alg /* Coded value */
    samplename = fread(fid,40,'*char');                                 % read sample name
    headerinfo.samplename = samplename';
    headerinfo.energy = fread(fid,1,'uint');                            % energy [V]
    headerinfo.intensity = fread(fid,1,'uint');                         % intensity [uA]

    % data offset
    fseek(fid,508,-1);                                                  % fseek to last 4 header bytes
    offset = fread(fid,1,'uint');                                       % data_offset
    headerinfo.offset = offset * 512 + 512;                             % [bits]

    if leaveopen == false
        fclose(fid);
    end
    
end