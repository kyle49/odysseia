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
