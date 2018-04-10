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
mu = runif(1,0,100)
eb = runif(1,0,200)
es = runif(1,0,200)
out_ = data.frame(BS, a = Z, d = N, mu, eb, es)
tau0 = 0 # the case there is no event
tau1 = 0 # the case there is an negative event
tau2 = 0 # the case there is an postive event
lkhd_ = sum((log(a) + dpois(BS$B, eb,log = TRUE) + dpois(BS$S, es, log = TRUE)) +
              (log(1-a) + log(d) + dpois(BS$B, eb,log = TRUE) + dpois(BS$S, es + mu, log = TRUE)) + 
              (log(1-a) + log(1-d) + dpois(BS$B, eb + mu,log = TRUE) + dpois(BS$S, es, log = TRUE))) 

for(i in 1:iter){
  
  # P(E|theta, X) = P(theta, X|E) * P(E) / P(theta, X)
  # hence P(E = j|theta, X) = P(E = j) * P(theta, X|E = j) / Sum 
  # Sum = P(E = 0) * P(theta, X|E = 0) + P(E = 1) * P(theta, X|E = 1)
  # P(theta, X|E = 1) = P(theta, X|N = 0) + P(theta, X|N = 1)
  
  # E step
  tau0 = (1 - a) * dpois(BS$B, eb) * dpois(BS$S, es)
  tau1 = a * d  * dpois(BS$B, eb) * dpois(BS$S, es + mu)
  tau2 = a * (1 - d) * dpois(BS$B, eb + mu) * dpois(BS$S, es)
  TAU = tau0 + tau1 + tau2
  tau0 = tau0 / TAU
  tau1 = tau1 / TAU
  tau2 = tau2 / TAU
  
  # M step
  a = 1 - sum(tau0) / 100
  if(a != 0){
    d = sum(tau1) / (100 * a)
  } else {
    d = 0.5
  }
  eb = sum(tau0 * BS$B) / sum(tau0)
  es = sum(tau0 * BS$S) / sum(tau0)
  mu = 0.5 * (sum(tau1 * BS$S) / sum(tau1) - es + sum(tau2 * BS$B) / sum(tau2) - eb)
  lkhd_[i + 1] = sum(tau0 * (log(a) + dpois(BS$B, eb,log = TRUE) + dpois(BS$S, es, log = TRUE)) +
                       tau1 * (log(1-a) + log(d) + dpois(BS$B, eb,log = TRUE) + dpois(BS$S, es + mu, log = TRUE)) + 
                       tau2 * (log(1-a) + log(1-d) + dpois(BS$B, eb + mu,log = TRUE) + dpois(BS$S, es, log = TRUE))) 
  if(lkhd_[i + 1] < -1e49){
    if(a == 1) a = 0.1
  }
  if(abs(lkhd_[i + 1] - lkhd_[i]) < 0.0001) break
}
plot(lkhd_[is.finite(lkhd_)], type = "l")
