lkhd_bsc = function(B, S, a, d, mu, eb, es){
  
  # B is NO. of buys
  # S is NO. of sells
  # a is prob. of an event
  # d is prob. of an event being negative
  # mu is the event driven arrival rate
  # eb is the noise buy arrival rate
  # es is the noise sell arrival rate
  
  (1-a)*dpois(B, eb)*dpois(S, es) + a*(d*dpois(B, eb)*dpois(S, es + mu) + (1-d)*dpois(B, eb + mu)*dpois(S, es)) 
}

PIN_bsc = function(a, mu, eb, es){
  
  a * mu / (a * mu + eb + es)
}

simu_bsc = function(a, d, mu, eb, es){
  
  Event = runif(1)
  if(Event < a){
    Bad = runif(1)
    if(Bad < d){
      B = rpois(1, eb)
      S = rpois(1, es + mu)
    }else{
      B = rpois(1, eb + mu)
      S = rpois(1, es)
    }
  }else{
    B = rpois(1, eb)
    S = rpois(1, es)
  }
  return (c(B,S))
}


## Simulation of test data ##

set.seed(2018)
out = replicate(100, simu_bsc(0.1, 0.5, 50, 100, 120))
BS = data.frame(B = out[1,], S = out[2,])

## Estimate paras. by JAGS ##

library(R2WinBUGS)
library(rjags)
model_bsc = function(){
  for(i in 1:100){
    E[i] ~ dbern(a)
    N[i] ~ dbern(d)
    B[i] ~ dpois(eb + mu * E[i] * (1-N[i]))
    S[i] ~ dpois(es + mu * E[i] * N[i])
  }
  a ~ dunif(0,1)
  d ~ dunif(0,1)
  eb ~ dunif(0,1000)
  es ~ dunif(0,1000)
  mu ~ dunif(0,1000)
}
write.model(model_bsc, "PIN_model_bsc.jags")
mod.init = list(a = runif(1), d = runif(1), eb = runif(1,0,1000), es = runif(1,0,1000), mu = runif(1,0,1000))
mod.jags = jags.model("PIN_model_bsc.jags", data = BS, inits = mod.init, n.chains = 3)
mod.vars = c("a", "d", "eb", "es", "mu")
mod.sim = coda.samples(mod.jags, mod.vars, n.iter = 10000)
summary(mod.sim)
plot(mod.sim)

## Estimate paras. by EM ##

iter = 10000

# initialize

set.seed(409)
a = 0.1
d = 0.5
Z = rbinom(100, 1, a)
N = rbinom(100, 1, d)
mu = runif(0,100)
eb = runif(0,200)
es = runif(0,200)

for(i in 1:iter){
  
  # P(E|theta, X) = P(theta, X|E) * P(E) / P(theta, X)
  # hence P(E = j|theta, X) = P(E = j) * P(theta, X|E = j) / Sum 
  # Sum = P(E = 0) * P(theta, X|E = 0) + P(E = 1) * P(theta, X|E = 1)
  # P(theta, X|E = 1) = P(theta, X|N = 0) + P(theta, X|N = 1)
  
  p = 0
  for(j in 1:100){
    
    p = p + l * (a * Z[i] + (1-a) * (1-Z[i])) * (d * N[i] + (1-d)*(1-N[i]))
  }
}
