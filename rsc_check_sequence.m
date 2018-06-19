function [y] = rsc_check_sequence(x,g)
terminated = -1;
[n,K] = size(g);
m = K - 1;

if terminated>0
    L_info = length(x);
    L_total = L_info + m;
else
    L_total = length(x);
    L_info = L_total - m;
end 

state = zeros(1,m);
y = [];

for i = 1:L_total
   if terminated<0 | (terminated>0 & i<=L_info)
      d_k = x(i);
%    elseif terminated>0 & i>L_info
%       % terminate the trellis结束拖尾
%       d_k = rem( g(1,2:K)*state', 2 );
   end
   
   a_k = rem( g(1,:)*[d_k state]', 2 );%根据生成多项式计算rsc编码
   y = [y rem(g(2,:)*[a_k state]', 2 )];
   state = [a_k, state(1:m-1)];%更新当前编码器状态
end