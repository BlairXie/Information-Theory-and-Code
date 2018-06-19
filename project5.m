clear
%%%%%%%%%%%%%%%%%%%%%%%turbo encoder%%%%%%%%%%%%%%%%%%%%%%%
g = [ 1 0 1 1;
       1 1 0 1 ];%generator 
x = randi([0,1],1,1000);
% x = [1 0 1 0 1 1 0 1] %origin message 
L_total = length(x);
[temp, alpha] = sort(rand(1,L_total)); % random interleaver mapping
for i = 1:L_total
    x2(1,i) = x(1,alpha(i));
end
% x2 = interleaver(x);%row to column interleaver
% display(x2);
x2;
turbo_code = [];
y = rsc_check_sequence(x,g);
y2 = rsc_check_sequence(x2,g);
for i = 1:L_total   
    turbo_code = [turbo_code x(i) y(i) y2(i)];
end

turbo_code = 2 * turbo_code - ones(size(turbo_code));
turbo_code;
size(turbo_code);
%%%%%%%%%%%%%%%%%%%%%%%%channel%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% snr = 1;
% turbo_code_r = awgn(turbo_code,snr, 'measured');
%%%%%%%%%%%%%%%%%%%%%%%channel2%%%%%%%%%%%%%%%%%%%%%%%%%%%
pe = 0.05
channel = randsrc(1,L_total*3,[1 0;pe 1-pe]);
sum(channel)
turbo_code_r = turbo_code;
for k = 1:L_total*3
    i = channel(1,k);
    if i == 1
        turbo_code_r(1,k) = -turbo_code_r(1,k);
    end
    
end
channel(1:2:20);
turbo_code(1:2:20);
turbo_code_r(1:2:20);
%%%%%%%%%%%%%%%%%%%%%%%turbo decoder%%%%%%%%%%%%%%%%%%%%%%%
r = turbo_demultiplex(turbo_code_r, alpha);


% Initialize extrinsic information      
L_e(1:L_total) = zeros(1,L_total);

L_a(alpha) = L_e;  %L_a是解交织码
L_all = logmapo(r(1,:),g,L_a,2);

xhat = (sign(L_all)+1)/2;
err_n = sum(xor(xhat, x))
err_rate = err_n/L_total
L_e = L_all- 2*r(1,1:2:2*L_total) - L_a;  % extrinsic info.


L_a = L_e(alpha);  %L_a是交织码
L_all = logmapo(r(2,:), g, L_a, 2);  % complete info.  
L_e = L_all - 2*r(2,1:2:2*L_total) - L_a;  % extrinsic info.
xhat2(alpha) = (sign(L_all)+1)/2;

err_n2 = sum(xor(xhat2, x))
err_rate2 = err_n2/L_total