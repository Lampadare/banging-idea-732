%{
Author: Gabriel Goldhagen
Written: September 2018

Updated October 2018, NPelot
Updated September 2019, NPelot

Load vagus nerve sample morphology data into cell arrays.
%}

close all
clear
format compact

fpath_home = pwd;

%% Load morphology data for pig anti-fibronectin IF
load('PigIFMorphology.mat')

%% Build filenames (from AnalyzeSamples.m outputs) and compile/analyze morphology metrics

species{1}        = 'Human';     species{2}        = 'Pig';          species{3}        = 'Rat';
species_initials  = 'CPR';
levels{1}         = 'Cervical';  levels{2}         = 'Abdominal';
lateralities{1,1} = 'Left';      lateralities{1,2} = 'Right';        lateralities{2,1} = 'Anterior';      lateralities{2,2} = 'Posterior';
sexes{1}          = 'Male';      sexes{2}          = 'Female';

Nspecies       = numel(species);
Nlevels        = numel(levels);
Nlateralities  = size(lateralities,2);
Nsexes         = numel(sexes);

Ncategories    = Nspecies*Nlevels*Nlateralities*Nsexes;

% sample_metadata_values = ['H' 'H' 'H' 'H' 'H' 'H' 'H' 'H' 'P' 'P' 'P' 'P' 'P' 'P' 'P' 'P' 'R' 'R' 'R' 'R' 'R' 'R' 'R' 'R';  % Species (3)
%                           'C' 'C' 'C' 'C' 'A' 'A' 'A' 'A' 'C' 'C' 'C' 'C' 'A' 'A' 'A' 'A' 'C' 'C' 'C' 'C' 'A' 'A' 'A' 'A';  % Level (2)
%                           'L' 'L' 'R' 'R' 'A' 'A' 'P' 'P' 'L' 'L' 'R' 'R' 'A' 'A' 'P' 'P' 'L' 'L' 'R' 'R' 'A' 'A' 'P' 'P';  % Side (2)
%                           'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F' 'M' 'F']; % Sex (2)

for species_ind = 2 %1:Nspecies
    for level_ind = 1:Nlevels
        for laterality_ind = 1:Nlateralities
            for sex_ind = 1:Nsexes
                % Read Excel document with sample numbers for a particular category
                cd(fpath_home)
                SheetFileName = strcat(species_initials(species_ind),levels{level_ind},lateralities{level_ind,laterality_ind},sexes{sex_ind});
                [cellnumbers,SampleNum,RawDataInCells] = xlsread(SheetFileName);
                Nsamples = numel(SampleNum);
                Nsamples_values{species_ind,level_ind,laterality_ind,sex_ind} = Nsamples;
                
                % File path of sample data
                DataDirectory =  [fpath_home '\' species{species_ind} '\' levels{level_ind} '\' lateralities{level_ind,laterality_ind} '\'  sexes{sex_ind} '\'];
                
                for sample_ind = 1:Nsamples
                    % Cell array of strings with sample identifier:
                    % <C,P,R><Subject #>-<Sample #>
                    SampleInfo{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                                = SampleNum{sample_ind};
                    
                    % Navigate to the directory containing that sample
                    SampleDataDirectory = [DataDirectory SampleNum{sample_ind}];
                    cd(SampleDataDirectory)
                    
                    % Nerve traces
                    load('Nerve.mat')
                    Nerve_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                              = Nerve{1}; % Includes .area and .diameter
                    
                    % Total fascicular (endoneurial) area
                    load('TotalFascicleArea.mat')
                    TotalFascArea_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                      = TotalFascArea;
                    TotalFascArea_Percent_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}              = 100 * TotalFascArea / Nerve{1}.area;
                    
                    % Total perineurial area
                    if (species_initials(species_ind) ~= 'P')
                        load('TotalPeriArea.mat')
                        TotalPeriArea_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                  = TotalPeriArea;
                        TotalPeriArea_Percent_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}          = 100 * TotalPeriArea / Nerve{1}.area;
                    else
                        TotalPeriArea                                                                                   = 0;
                        TotalPeriArea_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                  = 0;
                        TotalPeriArea_Percent_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}          = 0;
                    end
                    
                    % Calculate total epineurial area
                    TotalEpiArea = Nerve{1}.area - TotalFascArea - TotalPeriArea;
                    TotalEpiArea_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                       = TotalEpiArea;
                    TotalEpiArea_Percent_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}               = 100 * TotalEpiArea / Nerve{1}.area;
                    
                    % Inner perineurium traces, including bundles within peanut fascicles
                    load('FascicleIn.mat')
                    NFasc_tmp = numel(FascicleIn);
                    Nfasc_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                              = NFasc_tmp;
                    FascicleIn_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                         = FascicleIn;
                    
                    % Outer perineurium traces
                    if (species_initials(species_ind) ~= 'P')
                        load('FascicleOut.mat')
                        for fascicle_ind = 1:length(FascicleOut)
                            % Traces of outer perineurial boundaries
                            FascicleOut_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}{fascicle_ind}  = FascicleOut{fascicle_ind};
                        end
                    end
                    
                    % Perineurium thickness (only for non-peanut fascicles) and cross-sectional area per fascicle
                    if (species_initials(species_ind) ~= 'P')
                        load('Perineurium.mat')
                        Nperi_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                          = numel(Perineurium);
                        Perineurium_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                    = Perineurium;
                    end
                    
                    % Number of fascicles, counted 3 ways
                    load('NFasc.mat')
                    NFasc_NotPeanut_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                    = NFasc_NotPeanut;
                    if (species_initials(species_ind) ~= 'P')
                        NFasc_Peanut_Outer_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}             = NFasc_Peanut_Outer;
                        NFasc_Peanut_Inner_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}             = NFasc_Peanut_Inner;
                    end
                    
                    % Check number of fascicles (total number of inner perineurial traces, including within peanut fascicles)
%                     if (NFasc_NotPeanut + NFasc_Peanut_Inner) ~= NFasc_tmp
%                         error('Mismatch in expected number of fascicles')
%                     end
                    
                    % Age of subjects/animals
                    % Human values in years, pig values in weeks, rat values in days
                    % Human ages of "90+" entered as "99"
                    load('Age.mat')
                    Age_values{species_ind,level_ind,laterality_ind,sex_ind}{sample_ind}                                = Age;
                end
            end
        end
    end
end
cd(fpath_home)