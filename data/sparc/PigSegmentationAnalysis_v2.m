function [] = PigSegmentationAnalysis_v2(SampleFileName,fpath_prefix_histology, fpath_prefix_outputs)
%{
Description:
Analyze nerve morphology from binary images for single nerve sample.
    - Read in binary images of nerve and of fascicles.
    - Detect edges of nerve and of fascicles (define by x,y coordinates).
    - Calculate metrics (using polyarea to calculate surface areas): 
        - TotalFascArea:                    Total endoneurial cross-sectional area
        - Nerve{1}.area:                    Total nerve cross-sectional area
        - Nerve{1}.diameter:                Effective nerve diameter
        - FascicleIn{<fasc_idx>}.area:      Individual fascicle (i.e.
        endoneurial) cross-sectional areas
        - FascicleIn{<fasc_idx>}.diameter:  Effective fascicle diameters
        - NFasc_NotPeanut:                  Number of [non-peanut] fascicles
        - Other, including best-fit ellipses to fascicle and nerve traces
    - Save data.

Inputs:
    SampleFileName - Excel document with list of nerve samples
    fpath_prefix_histology - Prefix of filepath for location of segmented nerve and fascicle images (binary images)
    fpath_prefix_outputs - Prefix of filepath for saving morphology outputs
%}

%% List of samples to be processed
[Age_all,Sample,~] = xlsread(SampleFileName);

%% Loop through each nerve sample
for sample_ind = 1:length(Sample)
    clearvars -except SampleFileName fpath_prefix_histology fpath_prefix_outputs Age_all Sample sample_ind
    
    tmp = split(Sample{sample_ind},'-');
    sub = str2num(tmp{1}(2:end));
    sam = str2num(tmp{2});
    
%     fname_prefix    = ['sub-' num2str(sub) '/sam-' num2str(sam) ...
%                        '/sub-' num2str(sub) '_sam-' num2str(sam) ...
%                        '_P' num2str(sub) '-' num2str(sam)];
                   
    fpath_suffix    = ['sub-' num2str(sub) '/sam-' num2str(sam)];
                      
    fname_prefix    = ['sub-' num2str(sub) '_sam-' num2str(sam) ...
                       '_P' num2str(sub) '-' num2str(sam)];
    
    FilePathString  = strcat(fpath_prefix_histology, fpath_suffix);
    
    %% Pre-progress report
    disp(['Analyzing ' Sample{sample_ind}])
    
    %% Define filepaths of folder containing binary images of the nerve and perineurium
%     if strcmp(SampleFileName, 'PCervicalLeftMale.xlsx')
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Cervical\Left\Male\', Sample{sample_ind});
%     elseif strcmp(SampleFileName, 'PCervicalLeftFemale.xlsx')
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Cervical\Left\Female\', Sample{sample_ind});
%     elseif strcmp(SampleFileName, 'PCervicalRightMale.xlsx')
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Cervical\Right\Male\', Sample{sample_ind});
%     elseif strcmp(SampleFileName, 'PCervicalRightFemale.xlsx')
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Cervical\Right\Female\', Sample{sample_ind});
%     elseif strcmp(SampleFileName, 'PAbdominalAnteriorMale.xlsx')
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Abdominal\Anterior\Male\', Sample{sample_ind});
%     elseif strcmp(SampleFileName, 'PAbdominalAnteriorFemale.xlsx')
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Abdominal\Anterior\Female\', Sample{sample_ind});
%     elseif strcmp(SampleFileName, 'PAbdominalPosteriorMale.xlsx')
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Anterior\Posterior\Male\', Sample{sample_ind});
%     else
%         FilePathString=strcat(fpath_prefix_histology, '\Pig Samples\Micrographs\Nikon Lab Scope\10x Photos\Anterior\Posterior\Female\', Sample{sample_ind});
%     end
    
    %% Define image filenames
%     fascfilename        = strcat(Sample{sample_ind},'FascMask.tif');
%     nervefilename       = strcat(Sample{sample_ind},'NerveMask.tif');
%     scalefilename       = strcat(Sample{sample_ind},'ScaleMask.tif');
%     scalelengthfilename = strcat(Sample{sample_ind},'ScaleLength'); % Scale bar length [um]

    fascfilename        = strcat(fname_prefix,'FascMask.tif');
    nervefilename       = strcat(fname_prefix,'NerveMask.tif');
    scalefilename       = strcat(fname_prefix,'ScaleMask.tif');
    scalelengthfilename = strcat(fname_prefix,'ScaleLength'); % Scale bar length [um]
    
    %% Read images and detect image edges
    pwd_tmp = pwd;
    cd(FilePathString)
    
    FascicleMask        = imread(fascfilename);
    FascicleMaskEdges   = bwboundaries(FascicleMask);
    
    NerveMask           = imread(nervefilename);
    NerveMaskEdges      = bwboundaries(NerveMask);
    
    ScaleBar            = imread(scalefilename);
    ScaleLength         = 500;%load(scalelengthfilename); % ***** HARD-CODED AS 500 um FOR ALL PIG SAMPLES; could instead add ScaleLength.mat files *****
    
    cd(pwd_tmp);
    
    %% Calculate conversion from pixels to microns
    ScalePixels     = abs(find(max(ScaleBar),1,'last') - find(max(ScaleBar),1,'first')) + 1; % Number of pixels of scale bar
    micperpic       = ScaleLength/ScalePixels; %ScaleLength.slength/ScalePixels;
    
    %% Plot nerve and fascicle traces
    %{
figure()
imshow(perifilename)
hold on
colors=['b' 'g' 'r' 'c' 'm' 'y'];
for k=1:length(FascicleMaskEdges)
  boundary = FascicleMaskEdges{k};
  cidx = mod(k,length(colors))+1;
  %plot(boundary(:,2), -1*boundary(:,1),...
       %colors(cidx),'LineWidth',2);

 %randomize text position for better visibility
  rndRow = ceil(length(boundary)/(mod(rand*k,7)+1));
  col = boundary(rndRow,2); row = boundary(rndRow,1);
  h = text(col+1, row-1, num2str(Labels(row,col)));
  set(h,'Color',colors(cidx),'FontSize',14,'FontWeight','bold');
end

figure()
hold on
for n=1:numel(FascicleMaskEdges)
    plot(FascicleMaskEdges{n,1}(:,2), -1*FascicleMaskEdges{n,1}(:,1), 'k-')
end
plot(NerveMaskEdges{1,1}(:,2), -1*NerveMaskEdges{1,1}(:,1), 'k-')
    %}
    
    %% Analyze the fascicle traces
    TotalFascArea   = 0;
    NFasc_NotPeanut = numel(FascicleMaskEdges);
    
    for fasc_idx = 1:NFasc_NotPeanut
        FascicleIn{fasc_idx}.xpoints    =    FascicleMaskEdges{fasc_idx,1}(:,2);
        FascicleIn{fasc_idx}.ypoints    = -1*FascicleMaskEdges{fasc_idx,1}(:,1);
        FascicleIn{fasc_idx}.zpoints    = zeros((numel(FascicleIn{fasc_idx}.xpoints)), 1);
        
        % Fascicular cross-sectional area (for each fascicle and cumulative
        % sum) and corresponding effective diameter
        FascicleIn{fasc_idx}.area       = polyarea(FascicleIn{fasc_idx}.xpoints,FascicleIn{fasc_idx}.ypoints) * micperpic^2;
        TotalFascArea                   = TotalFascArea + FascicleIn{fasc_idx}.area;
        FascicleIn{fasc_idx}.diameter   = 2 * sqrt(FascicleIn{fasc_idx}.area/pi);
        
        tmp1(fasc_idx) = 2 * sqrt(FascicleIn{fasc_idx}.area/pi);
        tmp2(fasc_idx) = 2 * sqrt(polyarea(FascicleIn{fasc_idx}.xpoints,FascicleIn{fasc_idx}.ypoints)/pi);
        
        % Best-fit ellipse to each fascicle trace
        [FascicleIn{fasc_idx}.ellipse_centroid, FascicleIn{fasc_idx}.ellipse_a, FascicleIn{fasc_idx}.ellipse_b, FascicleIn{fasc_idx}.ellipse_diameter, FascicleIn{fasc_idx}.ellipse_alpha] = ...
            fitellipse([FascicleIn{fasc_idx}.xpoints, FascicleIn{fasc_idx}.ypoints], 'linear', 'constraint', 'trace');
    end
    
    %% Analyze the nerve trace
    Nerve{1}.xpoints  =    NerveMaskEdges{1}(:,2);
    Nerve{1}.ypoints  = -1*NerveMaskEdges{1}(:,1);
    Nerve{1}.zpoints  = zeros(numel(Nerve{1}.xpoints), 1);
    
    Nerve{1}.area     = polyarea(Nerve{1}.xpoints, Nerve{1}.ypoints) * micperpic^2;
    Nerve{1}.diameter = 2*sqrt(Nerve{1}.area/pi);
    Nerve{1}.scaling  = micperpic;
    
    % Best-fit ellipse to nerve trace
    [Nerve{1}.ellipse_centroid, Nerve{1}.ellipse_a, Nerve{1}.ellipse_b, Nerve{1}.ellipse_diameter ,Nerve{1}.ellipse_alpha] = ...
        fitellipse([Nerve{1}.xpoints, Nerve{1}.ypoints], 'linear', 'constraint', 'trace');
    
    %% Save data
    if strcmp(SampleFileName,'PCervicalLeftMale.xlsx')
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Cervical\Left\Male');
    elseif strcmp(SampleFileName,'PCervicalLeftFemale.xlsx')
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Cervical\Left\Female');
    elseif strcmp(SampleFileName, 'PCervicalRightMale.xlsx')
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Cervical\Right\Male');
    elseif strcmp(SampleFileName, 'PCervicalRightFemale.xlsx')
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Cervical\Right\Female');
    elseif strcmp(SampleFileName, 'PAbdominalAnteriorMale.xlsx')
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Abdominal\Anterior\Male');
    elseif strcmp(SampleFileName, 'PAbdominalAnteriorFemale.xlsx')
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Abdominal\Anterior\Female');
    elseif strcmp(SampleFileName, 'PAbdominalPosteriorMale.xlsx')
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Abdominal\Posterior\Male');
    else
        savefilename=strcat(fpath_prefix_outputs, '\Pig\Abdominal\Posterior\Female');
    end
    
    pwd_tmp = pwd;
    if exist(savefilename, 'dir') ~= 7
        mkdir(savefilename)
    end
    cd(savefilename)
    
    dirname = [Sample{sample_ind}];
    if exist(dirname, 'dir') ~= 7
        mkdir(dirname)
    end
    
    TotalFascAreaFileName   = [dirname '/TotalFascicleArea'];
    FascicleInFileName      = [dirname '/FascicleIn.mat'];
    NerveFileName           = [dirname '/Nerve.mat'];
    NFascFileName           = [dirname '/NFasc.mat'];
    AgeFileName             = [dirname '/Age.mat'];
    
    save(TotalFascAreaFileName, 'TotalFascArea');
    save(FascicleInFileName,    'FascicleIn');
    save(NerveFileName,         'Nerve');
    save(NFascFileName,         'NFasc_NotPeanut');
    Age                         = Age_all(sample_ind);
    save(AgeFileName,           'Age');

    cd(pwd_tmp)
    
    %% Progress report
    finalmessage = strcat(Sample{sample_ind},' analysis completed');
    disp(finalmessage)

end
end