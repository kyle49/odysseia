# Some simulations 
Size = 4 * 3600 / 3
set.seed(417)
Steps = rpois(Size, 1) * 0.01 * (2 * rbinom(Size, 1, 0.505) - 1)
Prices = 10 + cumsum(Steps)
Grids = 1:Size / 100
plot(Prices ~ Grids, type = "l")
Vbase = (Grids / 10 - 2.4)^2
Vols = rpois(Size, Vbase) * 100
Amounts = (Prices + 0.01 * runif(Size) - 0.005) * Vols
ticks = data.frame(Prices, Vols, Amounts)

### Basic bars ###

# Time bars
barWide_time = 5 * 20
TimeBar = function(x, wides, func){
  x_ = matrix(x, ncol = wides)
  apply(x_, 2, func)
}

Prices_tb_mean = TimeBar(Prices, Size /barWide_time, mean)
Prices_tb_max = TimeBar(Prices, Size /barWide_time, max)
Prices_tb_min = TimeBar(Prices, Size /barWide_time, min)
points(Prices_tb_mean, type = "l", col = 2, lwd = 2)
points(Prices_tb_max, type = "l", col = 2, lwd = 2, lty = 2)
points(Prices_tb_min, type = "l", col = 2, lwd = 2, lty = 3)

# Volume bars
N_bars = 48
VolBar = function(x, v, n_bars, func = mean){
  V = sum(v)/n_bars
  v_ = ceiling(cumsum(v) / V)
  out = numeric(n_bars)
  for(i in 1:n_bars){
    out[i] = func(x[v_ == i])
  }
  out
}

Prices_vb_mean = VolBar(Prices, Vols, N_bars)
Prices_vb_max = VolBar(Prices, Vols, N_bars, max)
Prices_vb_min = VolBar(Prices, Vols, N_bars, min)
points(Prices_vb_mean, type = "l", col = 3, lwd = 2)
points(Prices_vb_max, type = "l", col = 3, lwd = 2, lty = 2)
points(Prices_vb_min, type = "l", col = 3, lwd = 2, lty = 3)

# Dollar bars
Prices_db_mean = VolBar(Prices, Amounts, N_bars)
Prices_db_max = VolBar(Prices, Amounts, N_bars, max)
Prices_db_min = VolBar(Prices, Amounts, N_bars, min)
points(Prices_db_mean, type = "l", col = 4, lwd = 2)
points(Prices_db_max, type = "l", col = 4, lwd = 2, lty = 2)
points(Prices_db_min, type = "l", col = 4, lwd = 2, lty = 3)

# Moving-average tools
MA = function(x, w = 1, decay = .95){
  
  if(length(x) < w) w = length(x)
  c = sum(decay^(1:w - 1))
  out = numeric(length(x) - w + 1)
  for(i in 1:w){
    out = out + x[i:(length(x) - w + i)]*(decay^(i - 1))
  }
  out / c
}

### Information driven bars ###

## The propose is to sample more frequently when information arrives to the market

# Tick imblance bars

TickImbaBar = function(x, b0, E_imba){
  
  #b0 as boundary condition matching the preceeding data
  
  b = c(b0, sign(diff(x)))
  for(i in 2:length(b)){
    if(b[i] == 0) b[i] = b[i - 1]
  }
  imba = cumsum(b)
  TIB = which(abs(imba) > abs(E_imba))[1]
  if(is.na(TIB)) TIB = length(x)
  out = list(expect = sum(b), tail = b[length(b)], TIB = TIB)
  return(out)
}
TickImbaBar_apply = function(x, segs, w = 5, decay = .95){
  
  l = length(x)/segs
  TIBs = numeric(segs - 1)
  out = list(expect = 0, tail = 0, TIB = 0)
  expects = numeric(0)
  for(i in 1:segs){
    x_ = x[1:l + (i - 1) * l]
    out = TickImbaBar(x = x_, b0 = out$tail, E_imba = out$expect)
    expects = c(out$expect, expects)
    out$expect = MA(expects, w = w, decay = decay)[1]
    if(i < w){
      print("Neglected for Burning-in")
    }else{
      print("Iterations")
      print(out)
      TIBs[i - 1] = out$TIB
    }
  }
  out_ = list(TIBs = TIBs / l, expects = expects)
  return(out_)
}
tickimbas = TickImbaBar_apply(Prices, 48)
plot(tickimbas$TIBs, type = "l", ylim = c(0,1), ylab = "TIBs")

# Vol imblance bars

VolImbaBar = function(x, v, b0, E_imba){
  b = c(b0, sign(diff(x)))
  for(i in 2:length(b)){
    if(b[i] == 0) b[i] = b[i - 1]
  }
  imba = cumsum(b * v)
  TIB = which(abs(imba) > abs(E_imba))[1]
  if(is.na(TIB)) TIB = length(x)
  out = list(expect = sum(v * b), tail = b[length(b)], TIB = TIB)
  return(out)
}
VolImbaBar_apply = function(x, v, segs, w = 5, decay = .95){
  
  l = length(x)/segs
  TIBs = numeric(segs - 1)
  out = list(expect = 0, tail = 0, TIB = 0)
  expects = numeric(0)
  for(i in 1:segs){
    x_ = x[1:l + (i - 1) * l]
    v_ = v[1:l + (i - 1) * l]
    out = VolImbaBar(x = x_, v = v_, b0 = out$tail, E_imba = out$expect)
    expects = c(out$expect, expects)
    out$expect = MA(expects, w = w, decay = decay)[1]
    if(i < w){
      print("Neglected for Burning-in")
    }else{
      print("Iterations")
      print(out)
      TIBs[i - 1] = out$TIB
    }
  }
  out_ = list(TIBs = TIBs / l, expects = expects)
  return(out_)
}
volimbas = VolImbaBar_apply(Prices, Vols, 48)
points(volimbas$TIBs, type = "l", col = 2)
amtimbas = VolImbaBar_apply(Prices, Amounts, 48)
points(amtimbas$TIBs, type = "l", col = 3, lty = 2)

# Tick run bars

TickRunBar = function(x, b0, E_run){
  
  #b0 as boundary condition matching the preceeding data
  b = c(b0, sign(diff(x)))
  for(i in 2:length(b)){
    if(b[i] == 0) b[i] = b[i - 1]
  }

  #let p = sum(b|b = 1), q = -sum(b|b = -1) for length T
  #then p + q = T, p - q = sum(b) 
  p = (1:length(b) + cumsum(b)) / 2
  q = (1:length(b) - cumsum(b)) / 2
  run = apply(cbind(p,q), 1, max)
  TRB = which(run > E_run)[1]
  if(is.na(TRB)) TRB = length(x)
  out = list(expect = max(sum(b == 1), sum(b == -1)), tail = b[length(b)], TRB = TRB)
  return(out)
}
TickRunBar_apply = function(x, segs, w = 5, decay = .95){
  
  l = length(x)/segs
  TRBs = numeric(segs - 1)
  out = list(expect = 0, tail = 0, TIB = 0)
  expects = numeric(0)
  for(i in 1:segs){
    x_ = x[1:l + (i - 1) * l]
    out = TickRunBar(x = x_, b0 = out$tail, E_run = out$expect)
    expects = c(out$expect, expects)
    out$expect = MA(expects, w = w, decay = decay)[1]
    if(i < w){
      print("Neglected for Burning-in")
    }else{
      print("Iterations")
      print(out)
      TRBs[i - 1] = out$TRB
    }
  }
  out_ = list(TRBs = TRBs / l, expects = expects)
  return(out_)
}
tickruns = TickRunBar_apply(Prices, 48)
plot(tickruns$TRBs, type = "l", ylim = c(0,1), ylab = "TIBs")
# Not very informative here