rm(list = ls())
derad = pi/180
radeg = 180/pi
twpi = 2*pi
# set paras 
kelm = 8 # No. sensors
dd = .5 # distance
d = 0 : dd : (kelm - 1) * dd # array of sensors
iwave = 3 # No. source
theta = c(10, 30, 60)
n = 500
A = exp(-(0+1i) * twpi * d %o% sin(theta * derad))
S = matrix(rnorm(iwave * n), iwave, n) # source signals, iid
X = A %*% S
## add white gaussian noise (MATLAB awgn function)
awgn = function(x, snr, cplx = TRUE){
  l = length(x)
  sigPower = sum(abs(x)^2) / l
  noisePower = sqrt(sigPower / snr)
  if(cplx){
    noise = rnorm(l) * noisePower + rnorm(l) * noisePower * 1i
  } else {
    noise = rnorm(l) * noisePower
  }
  return(x + noise)
}
X1 = apply(X, 1, awgn, snr = 10) # received signals

# solver
Rxx = t(X1) %*% X1 / n # corr mat
InvS = solve(Rxx)
R_eigen = eigen(Rxx)
Eva = R_eigen$values
argsort_eigen = rank(Eva)[kelm:1]
Ev= R_eigen$vectors[,argsort_eigen]
angles = numeric(361)
Sp = complex(361)

for(j in 1:361){
  angles[j] = (j - 181)/2
  phim = derad * angles[j]
  a = exp(-1i* twpi * d * sin(phim))
  L = iwave
  En = Ev[, (L+1):kelm]
  Sp[j] = 1 /(t(a) %*% En %*% t(En) %*% a)
}

Sp = abs(Sp)
Spmax = max(Sp)
Sp = 10 * log10(Sp/Spmax)
plot(Sp~angles, type = "l")
