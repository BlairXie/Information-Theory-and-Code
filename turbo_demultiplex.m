function r = turbo_demultiplex(turbo_code, alpha)
x_r = turbo_code(1:3:end);
y_r = turbo_code(2:3:end);
y2_r = turbo_code(3:3:end);
r1 = [];
r2 = [];
for i = 1:length(turbo_code)/3
    r1 = [r1 x_r(i),y_r(i)];  
    r2 = [r2 x_r(alpha(i)),y2_r(i)];
end 
r = [];
r(1,:) = r1;
r(2,:) = r2;
% size(r)
end 