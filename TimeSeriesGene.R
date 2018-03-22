library(MASS)

x = rnorm(100)

ReLU = function(x){
  if(x < 0) x = 0
  x
}

ReLU(x)
