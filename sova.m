
function L_all = sova(rec_s, g, L_a, ind_dec) 
% This function implememts Soft Output Viterbi Algorithm in trace back mode 
% Input: 
%       rec_s: scaled received bits. rec_s(k) = 0.5 * L_c(k) * y(k) 
%              L_c = 4 * a * Es/No, reliability value of the channel
%              y: received bits
%       g:  encoder generator matrix in binary form, g(1,:) for feedback, g(2,:) for feedforward
%       L_a: a priori information about the info. bits. Extrinsic info. from the previous
%             component decoder
%       ind_dec: index of the component decoder. 
%	          =1: component decoder 1; The trellis is terminated to all zero state
%    	          =2: component decoder 2; The trellis is not perfectly terminated.
% Output:
%       L_all: log ( P(x=1|y) ) / ( P(x=-1|y) )
%
% Copyright: Yufei Wu, Nov. 1998
% MPRG lab, Virginia Tech
% for academic use only

% Frame size, info. + tail bits
L_total = length(L_a);
[n,K] = size(g); 
m = K - 1;
nstates = 2^m;
Infty = 1e10;

% SOVA window size. Make decision after 'delta' delay. Decide bit k when received bits
% for bit (k+delta) are processed. Trace back from (k+delta) to k. 
delta = 30;    

% Set up the trellis defined by g.
[next_out, next_state, last_out, last_state] = trellis(g);

% Initialize path metrics to -Infty
for t=1:L_total+1
   for state=1:nstates
      path_metric(state,t) = -Infty;
   end
end

% Trace forward to compute all the path metrics
path_metric(1,1) = 0;
for t=1:L_total
   y = rec_s(2*t-1:2*t);
   for state=1:nstates
      sym0 = last_out(state,1:2);
      sym1 = last_out(state,3:4);
      state0 = last_state(state,1);
      state1 = last_state(state,2);
      Mk0 = y*sym0' - L_a(t)/2 + path_metric(state0,t);
      Mk1 = y*sym1' + L_a(t)/2 + path_metric(state1,t);
      
      if Mk0>Mk1
         path_metric(state,t+1)=Mk0;
         Mdiff(state,t+1) = Mk0 - Mk1;
         prev_bit(state, t+1) = 0;
      else
         path_metric(state,t+1)=Mk1;
         Mdiff(state,t+1) = Mk1 - Mk0;
         prev_bit(state,t+1) = 1;
      end

   end
end
      
% For decoder 1, trace back from all zero state, 
% for decoder two, trace back from the most likely state
if ind_dec == 1
   mlstate(L_total+1) = 1;
else
   mlstate(L_total+1) = find( path_metric(:,L_total+1)==max(path_metric(:,L_total+1)) );
end

% Trace back to get the estimated bits, and the most likely path
for t=L_total:-1:1
   est(t) = prev_bit(mlstate(t+1),t+1);
   mlstate(t) = last_state(mlstate(t+1), est(t)+1);
end

% Find the minimum delta that corresponds to a compitition path with different info. bit estimation.       
% Give the soft output
for t=1:L_total
   llr = Infty;
   for i=0:delta
      if t+i<L_total+1
         bit = 1-est(t+i);
         temp_state = last_state(mlstate(t+i+1), bit+1);
         for j=i-1:-1:0
            bit = prev_bit(temp_state,t+j+1);
            temp_state = last_state(temp_state, bit+1);
         end
         if bit~=est(t) 
            llr = min( llr,Mdiff(mlstate(t+i+1), t+i+1) );
         end
      end
   end
   L_all(t) = (2*est(t) - 1) * llr;
end    
                  
               
      
        
   
function y = rsc_encode(g, x, terminated)
% Copyright Nov. 1998 Yufei Wu
% MPRG lab, Virginia Tech.
% for academic use only

% encodes a block of data x (0/1)with a recursive systematic
% convolutional code with generator vectors in g, and
% returns the output in y (0/1).
% if terminated>0, the trellis is perfectly terminated
% if terminated<0, it is left unterminated;

% determine the constraint length (K), memory (m), and rate (1/n)
% and number of information bits.
[n,K] = size(g);
m = K - 1;
if terminated>0
  L_info = length(x);
  L_total = L_info + m;
else
  L_total = length(x);
  L_info = L_total - m;
end  


% initialize the state vector
state = zeros(1,m);

% generate the codeword
for i = 1:L_total
   if terminated<0 | (terminated>0 & i<=L_info)
      d_k = x(1,i);
   elseif terminated>0 & i>L_info
      % terminate the trellis
      d_k = rem( g(1,2:K)*state', 2 );
   end
 
   a_k = rem( g(1,:)*[d_k state]', 2 );
   [output_bits, state] = encode_bit(g, a_k, state);
   % since systematic, first output is input bit
   output_bits(1,1) = d_k;
   y(n*(i-1)+1:n*i) = output_bits;
end