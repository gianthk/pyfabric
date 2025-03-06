function [image,metadata]=readISQ(filename,slicerange,window,progress)

% [image]=readISQ(filename) reads the image in the file
% [image,metadata]=readISQ(filename) also provides some metadata
% [image,metadata]=readISQ(filename,slice_nr) reads one slice at a time. slice_nr=0
% means read only metadata.
% [image]=readISQ(filename,[first_slice_nr,last_slice_nr]) reads a range of
% slices. [] means read all slices.
% [image]=readISQ(filename,slicerange,window) reads the
%   window from each slice defined by the vector
%   window=[minx,maxx,miny,maxy]. [] means read the full slice.
% [image]=readISQ(filename,slicerange,window,progress)
%   progress=1 displays progress bar (0 no bar)
%
% Johan Karlsson, AstraZeneca, 2017
% 
% See also http://www.scanco.ch/en/support/customer-login/faq-customers/faq-customers-general.html

fid=fopen(filename);
%h=fread(fid,128,'int'); % header
h=fread(fid,32,'int'); % header
metadata.dimx_p=h(12);
metadata.dimy_p=h(13);
metadata.dimz_p=h(14);
metadata.dimx_um=h(15);
metadata.dimy_um=h(16);
metadata.dimz_um=h(17);
metadata.slice_thickness_um=h(18);
metadata.slice_increment_um=h(19);
metadata.slice_1_pos_um=h(20);
metadata.min_data_value=h(21);
metadata.max_data_value=h(22);
metadata.mu_scaling=h(23);

metadata.name=char(fread(fid,40,'char*1')'); % header

if nargin<2 | isempty(slicerange)
    first_slice=1;
    last_slice=metadata.dimz_p;
elseif length(slicerange)==1 & slicerange==0
    first_slice=0;
    last_slice=-1;
    image=[];
elseif length(slicerange)==1
    first_slice=slicerange;
    last_slice=slicerange;
else
    first_slice=slicerange(1);
    last_slice=slicerange(2);
end
if nargin<3 | isempty(window)
    window=[1,metadata.dimx_p,1,metadata.dimy_p];
end
if nargin<4
    progress=0;
end

%image=zeros(window(2)-window(1)+1,window(4)-window(3)+1,last_slice-first_slice+1);
if progress 
    wb=waitbar(0,'Loading image data');
end
for slice=first_slice:last_slice
    if progress
        waitbar((slice-first_slice)/(last_slice-first_slice),wb);
    end
    fseek(fid,512*(h(end)+1)+metadata.dimx_p*metadata.dimy_p*2*(slice-1),'bof');
    I=permute(reshape(fread(fid,metadata.dimx_p*metadata.dimy_p,'short'),[metadata.dimx_p,metadata.dimy_p]),[2,1]);
    image(:,:,slice-first_slice+1)=I(window(1):window(2),window(3):window(4));
end
if progress
    close(wb);
end
fclose(fid);
   