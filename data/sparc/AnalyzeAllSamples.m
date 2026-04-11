%{
Author:     Gabriel B. Goldhagen
Created:    August 2018

Matlab R2018b

Modified by N. Pelot, Sept 2019

Description: 
Analyze nerve morphology based on binary images of nerve and perineurium.
%}

%% Initialize
clear
close all
format compact

fpath_prefix_histology = '../primary/';
fpath_prefix_outputs = '.';

%% Human
%{
% disp('Human samples')
% cervical
HumanRatSegmentationAnalysis_v2('CCervicalLeftMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
HumanRatSegmentationAnalysis_v2('CCervicalLeftFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

HumanRatSegmentationAnalysis_v2('CCervicalRightMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
HumanRatSegmentationAnalysis_v2('CCervicalRightFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

% abdominal
HumanRatSegmentationAnalysis_v2('CAbdominalAnteriorMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
HumanRatSegmentationAnalysis_v2('CAbdominalAnteriorFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

HumanRatSegmentationAnalysis_v2('CAbdominalPosteriorMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
HumanRatSegmentationAnalysis_v2('CAbdominalPosteriorFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
%}

%% Pig

% disp('Pig samples')
% cervical
PigSegmentationAnalysis_v2('PCervicalLeftMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
PigSegmentationAnalysis_v2('PCervicalLeftFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

% PigSegmentationAnalysis_v2('PCervicalRightMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
% PigSegmentationAnalysis_v2('PCervicalRightFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

% abdominal
PigSegmentationAnalysis_v2('PAbdominalAnteriorMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
PigSegmentationAnalysis_v2('PAbdominalAnteriorFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

% PigSegmentationAnalysis_v2('PAbdominalPosteriorMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
% PigSegmentationAnalysis_v2('PAbdominalPosteriorFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)


%% Rat
%{
disp('Rat samples')
% cervical
HumanRatSegmentationAnalysis_v2('RCervicalLeftMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
HumanRatSegmentationAnalysis_v2('RCervicalLeftFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

% HumanRatSegmentationAnalysis_v2('RCervicalRightMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
% HumanRatSegmentationAnalysis_v2('RCervicalRightFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

% abdominal
HumanRatSegmentationAnalysis_v2('RAbdominalAnteriorMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
HumanRatSegmentationAnalysis_v2('RAbdominalAnteriorFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)

% HumanRatSegmentationAnalysis_v2('RAbdominalPosteriorMale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
% HumanRatSegmentationAnalysis_v2('RAbdominalPosteriorFemale.xlsx',fpath_prefix_histology,fpath_prefix_outputs)
%}