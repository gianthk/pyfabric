# Replace HU values below 1000 (air) with 2000 (water)
<value>?<1000=2000</value>

# Convert HU to BMD values
<value>/8192;*$slope;+$intercept;?<-100=-100;?>1400=1400</value>

