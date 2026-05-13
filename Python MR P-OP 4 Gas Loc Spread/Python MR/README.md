# Introduction 
The ojbective of the project is making the CSS option valuation match between Aligne and MO fundamental model 

# Explanation
Aligne bases the daily MtM option valuation on Kirk formula (find Kirk approximation in appendix 2).
CSS prices are mean reverting (yield in T not independent from yield in T-1), the process is not as “explosive” as a random walk and square root of time-influence is partially offset by a reversion to the mean.
The mean reversion of the CSS is implied in the Merit Order simulations.
We account for that mean reversion adjusting the Kirk valuation of Aligne.

# Steps:

1.We calculate the total value, intrinsic and extrinsic value implied in the MO simulations.

2.We do the same with the Kirk fórmula.

3.We apply a factor α to the general Kirk volatility ("σ") such that the 	Kirk extrinsic value matches the MO implied extrinsic value: "α  s.t. EVK =EVMO"

# Notes: 

We want to apply a factor to the general Kirk volatility (σ), but that entails an indetermination on each side’s volatility (infinte solutions for "σ1","σ2"):

σ =√("σ12" +("σ2F2" /"F2 + X" )"2" −"2ρσ1σ2F2" /"F2 + X"  " " )

We solve this indetermination applying the same factor (α) for each side (σ1,σ2), which is equivalent to applying the same factor (α) to the general volatility (σ) (demonstration in appendix 1).

# Appendix 1:

Kirk general volatility:

			 σ =√("{σ12" +("σ2F2" /"F2 + X" )"2" −"2ρσ1σ2F2" /"F2 + X"  " }" )          eq.1

Applying a factor to each side:

			 σα =√("{(ασ1)2" +("ασ2F2" /"F2 + X" )"2" −"2ρασ1ασ2F2" /"F2 + X"  " }" )


Operating:		

σα =√("{α2 σ12" +"α" 2("ασ2F2" /"F2 + X" )2−"α" 2 "2ρσ1σ2F2" /"F2 + X"  " }" )    →
σα =√("α2{σ12" +("ασ2F2" /"F2 + X" )2−"2ρσ1σ2F2" /"F2 + X"  " }"  ) →
→   σα ="α" √( "{σ12" +("ασ2F2" /"F2 + X" )2−"2ρσ1σ2F2" /"F2 + X"  " }" )    →   eq.1    →         σα ="ασ"



