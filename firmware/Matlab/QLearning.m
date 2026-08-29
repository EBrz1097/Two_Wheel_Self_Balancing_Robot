
clc, clear, close all

%%

Ac = [ 0,     1;
     327,    0];

Bc = [   0;
     -33.33];

C = [1 1];

D = 0;

sys_c = ss(Ac, Bc, C, D);

Ts = 0.01;
sys_d = c2d(sys_c, Ts, 'zoh');

A = sys_d.A;
B = sys_d.B;

n = size(A, 1);

%% Implicit LQR
Q = eye(n);
E = eye(n);
R = 1;
S = zeros(n, 1);

[P_lqr, K_lqr, L] = idare(A, B, Q, R, S, E);

%% Policy Iteration

nP = 100;
K = zeros(nP, n); K(1, :) = place(A, B, [0.4 0.5]);
P = cell(nP, 1);  P{1} = zeros(n);
M = 20;

tic
for i=1:nP
    
    % Policy Evaluation
    PHI = [];
    SAI = [];
    xk = [3, 0.1]';
    for m=1:M
        uk = -K(i, :)*xk + 0.01*randn;
        xk1 = (A + 0.01*randn)*xk + (B + 0.01*randn)*uk;
        uk1 = -K(i, :)*xk1;
        
        zk = [xk; uk];
        zk1 = [xk1; uk1];
        PHI = [PHI; ComputeZbar(zk)-ComputeZbar(zk1)];    %# ok

        rk = xk'*Q*xk + uk'*R*uk;
        SAI = [SAI; rk];    %# ok

        xk = xk1;
    end
    Hbar = PHI\SAI;
    H{i+1} = ConvertHbarToH(Hbar);  %# ok

    Hxx = H{i+1}(1:n, 1:n); 
    Hxu = H{i+1}(1:n, n+1);
    Hux = H{i+1}(n+1, 1:n);
    Huu = H{i+1}(n+1, n+1);


    % Policy Improvement
    K(i+1, :) = inv(Huu)*Hux;       %# ok

    disp(['Iteration: ', num2str(i), '/', num2str(nP)])

    if norm(K(i+1, :) - K(i, :)) < 1e-6
        disp('Convergence!')
        break
    end

end
toc

disp(['K from QLearning: ', num2str(K(i+1, :))])
disp(['K from LQR      : ', num2str(K_lqr)])

%% Plot Convergence 
fig = figure();
fig.Color = [1 1 1];
for j=1:2
    subplot(2, 1, j)
    plot(1:i+1, K(1:i+1, j), 'LineWidth', 2)
    xlabel('Iteration')
    ylabel('Amplitude')
    title(['K', num2str(j)])
end

%% Closed Loop Simulation
T0 = 0;
Tf = 20;
t = T0:Ts:Tf;
Nt = numel(t);

x = zeros(n, Nt);   x(:, 1) = [3, 0.1];
u = zeros(1, Nt);

Cost = x(:, 1)'*Q*x(:, 1);

for k=1:Nt-1

    u(k) = -K(i+1, :)*x(:, k);
    
    x(:, k+1) = A*xk + B*uk;

end

%% Plot Results
fig = figure(2);
fig.Color = [1 1 1];

subplot(2, 1, 1)
plot(t, x, LineWidth=2)
title('TD0 Response')
xlabel('Time(second)')
ylabel('Amplitude')
legend('x1', 'x2')
xlim([0 10])

subplot(2, 1, 2)
plot(t, u, LineWidth=2)
title('Input')
xlabel('Time(second)')
ylabel('Amplitude')
legend('u')
xlim([0 10])





%% Functions
% function to Compute Xbar
function Zbar = ComputeZbar(z)
    z = z(:)';  % reshape X to 1*n
    Zbar = [];
    for i=1:numel(z)
        Zbar = [Zbar z(i)*z(i:end)];   %# ok
    end
end

% function to Convert Pbar to P
function H = ConvertHbarToH(Hbar)
    
    H = [Hbar(1)    Hbar(2)/2   Hbar(3)/2;
         Hbar(2)/2  Hbar(4)     Hbar(5)/2;
         Hbar(3)/2  Hbar(5)/2   Hbar(6)];
end