function stats = summary_stats(morphology_data)

stats = [median(morphology_data);
         mean(morphology_data);
         std(morphology_data);
         min(morphology_data);
         max(morphology_data)]';

% disp(['Median: ' num2str(stats(1))])
% disp(['Mean:   ' num2str(stats(2))])
% disp(['SD:     ' num2str(stats(3))])
% disp(['Min:    ' num2str(stats(4))])
% disp(['Max:    ' num2str(stats(5))])

end
