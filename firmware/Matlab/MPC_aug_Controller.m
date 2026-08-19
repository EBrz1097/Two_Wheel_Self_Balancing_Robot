clc, clear, close all

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

t0 = 0;
tf = 15;
ts = 0.01;
t = t0:ts:tf;
nt = numel(t);

A = [ 0,     1;
     327,    0];

B = [   0;
     -33.33];

C = [1 0];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

sysc = ss(A, B, C, 0);
sysd = c2d(sysc, ts, "zoh");

Ad = sysd.A;
Bd = sysd.B;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Np = 10;
Nc = 4;

Aaug = [Ad, Bd;
        0 0 1];

Baug = [Bd;1];

Qz = diag([100 10 0]);
Rdu = 0.5;

nz = size(Aaug, 1);
nu = size(Baug, 2);

Phi = zeros(Np*nz, nz);
Gamma = zeros(Np*nz, Nc*nu);

for i=1:Np
    Phi((i-1)*nz+1:i*nz, :) = Aaug^i;
    for j=1:Nc
    if i>= j
        Gamma((i-1)*nz+1:i*nz, (j-1)*nu+1:j*nu) = Aaug^(i-j)*Baug;
    end
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%e44

Qbar = kron(eye(Np), Qz);
Rbar = kron(eye(Nc), Rdu);

H = Gamma' * Qbar * Gamma + Rbar;
F = Gamma' * Qbar * Phi;

Kall = H \ F;
Kmpc_aug = Kall(1, :);