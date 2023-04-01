# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 14:01:21 2020
"""
# Product Dims Analysis
# version 6: 
# improve code efficiency from v5
# remove duplicate rack dims if possible

# import libraries
import pandas as pd
import numpy as np
import itertools
import math
import os
import datetime
from itertools import permutations
import ib_fcst

# start to count run time
starttime = datetime.datetime.now()

# read inputs: swith between on hand or inbound products
#prod_dims_data = ib_fcst.prod_dims_data #inbound products
prod_dims_data = pd.read_csv(r'C:\..\prod_dims.csv')
    
#prod_dims_data['units'].sum()


# define model variables
d1 = [42]
width_max = 69
width_st = 8
width_inc = 1

height_max = 60
height_st = 3
height_inc = 1 

# Part 1: Create a list of rack dims
class rack_prod_analysis():
    
    def __init__(self, d1, width_max, width_st, width_inc, height_max, height_st, height_inc, prod_dims_data):
        
        # inputs
#        self.unit_threshold = unit_threshold
#        self.target = target
        self.d1 = d1
        
        self.width_max = width_max
        self.width_st = width_st
        self.width_inc = width_inc
        
        self.height_max = height_max
        self.height_st = height_st
        self.height_inc = height_inc
        
        self.prod_dims_data = prod_dims_data
#        self.path = path
        
        # outputs
        self.rack_dims = self.construc_rack_dims()
        self.prod_dims = self.construc_prod_dims()
        self.df = self.construc_df()
        self.df_new = self.construc_df_new()
#        self.df_final = self.construc_df_final()
#        self.min_loss = self.construc_min_loss()
#        self.df_best = self.construc_df_best()
        
    
    def construc_rack_dims(self):
        
        depth = self.d1

        # width
        width_max = self.width_max
        width_st = self.width_st
        width_inc = self.width_inc 
        width = list(range(width_st, width_max + 1, width_inc)) # from 8 to 60 with 1 inch incremental
        
        #height
        height_max = self.height_max
        height_st = self.height_st
        height_inc = self.height_inc       
        height = list(range(height_st, height_max + 1, height_inc)) # from 3 to 60 with 1 inch incremental
        
        # use Depth x Width x Height as rack dims instead max/mid/min      
        rack_dims = [((str(d) + 'x' + str(w) + 'x' + str(h)), d, w, h) for d, w, h in itertools.product(depth, width, height)]
        rack_dims = pd.DataFrame(rack_dims, columns = ['Rack_Dims', 'Depth', 'Width', 'Height']) 
        
        return rack_dims
      
   
    # Part 2: Product dims data
    def construc_prod_dims(self):
        
#        prod_dims = prod_dims_data
        prod_dims = self.prod_dims_data        
        prod_dims.rename(columns = {'MaxDim': 'Prod_MaxDim','MidDim': 'Prod_MidDim','MinDim':'Prod_MinDim'}, inplace = True)
        prod_dims['Prod_Dims'] = prod_dims['Prod_MaxDim'].astype(str) + 'x'+ prod_dims['Prod_MidDim'].astype(str) +'x' + prod_dims['Prod_MinDim'].astype(str) 

        prod_dims['cube'] = prod_dims['units'] * prod_dims['Prod_MaxDim'] * prod_dims['Prod_MidDim'] * prod_dims['Prod_MinDim'] / 1728
        prod_dims = prod_dims[['Prod_MaxDim','Prod_MidDim','Prod_MinDim','Prod_Dims','units', 'cube']]
          
        return prod_dims

    
    # Part 3: df list
    def construc_df(self):
        
        rack_dims = self.rack_dims
        prod_dims = self.prod_dims
        
        rack_list = rack_dims['Rack_Dims'].unique()
        prod_list = prod_dims['Prod_Dims'].unique()
        
        comb = [(i,j) for i, j in itertools.product(rack_list, prod_list)]
        
        df_comb = pd.DataFrame(comb, columns = ['Rack_Dims','Prod_Dims'])
        
        df = pd.merge(df_comb, rack_dims, on = ['Rack_Dims'] , how = 'outer')
        df = pd.merge(df, prod_dims, on = ['Prod_Dims'] , how = 'outer')
        
        # product cube and rack cube
        df['Prod_cube'] = df['Prod_MaxDim'] * df['Prod_MidDim'] * df['Prod_MinDim'] / 1728
        df['Rack_cube'] = df['Depth'] * df['Width'] * df['Height'] / 1728
       
        return df
    
    
    def construc_df_new(self):
    # num of units per location - no double deep and take all orientation combinations  
    
        df = self.df
    
        def calc(D, W, H, MaxDim, MidDim, MinDim):
            p = list(permutations([MaxDim,MidDim,MinDim],3))    
            #  deep = [math.floor(D / i[0]) for i in p]    
            deep = [min(math.floor(D / i[0]),1) for i in p]
            col = [math.floor(W / i[1]) for i in p]
            level = [math.floor(H/ i[2]) for i in p]
            
            comb = [ d*c*l for d, c, l in zip(deep, col, level)]
            f = np.max(comb)
            
            return f
          
        df['f1'] = np.vectorize(calc, otypes=["O"]) (df['Depth'], df['Width'], df['Height'], df['Prod_MaxDim'], df['Prod_MidDim'], df['Prod_MinDim'])       
        df_new = df
        
        return df_new 
    
r = rack_prod_analysis(d1, width_max, width_st, width_inc, height_max, height_st, height_inc, prod_dims_data)
#r.df_new    


class scenario_runs():
    
    def __init__(self, df_new, target, unit_threshold):
        
        self.df_new = df_new
        self.target = target
        self.unit_threshold = unit_threshold
        self.df_final = self.construc_df_final()
        
    
    def construc_df_final(self):
              
        df_new = self.df_new
        target = self.target
        unit_threshold = self.unit_threshold
        
        df_new['f'] = np.minimum(unit_threshold, df_new['f1'])
        df_new['cube_fill_rate'] = df_new['f'] * df_new['Prod_cube'] / df_new['Rack_cube']  
        
        
        def calc_pct(df_test):
            df_test['units_pct'] = df_test['units'].transform(lambda x: x/x.sum()) # using units, eff_units doesn't have the current sum
            
            df_test['ttl_cube'] = df_test['Prod_cube'] * df_test['units']
            df_test['cube_pct'] = df_test['ttl_cube'].transform(lambda x: x/x.sum())
            
            df_test = df_test[df_test['cube_fill_rate'] >= target].reset_index(drop = True)
            
            # if Rack_Dims show as empty, neaning no product has cubde fill rate > TFR for this rack based on the current unit threshold assumption
        
            Rack_Dims = df_test['Rack_Dims'].unique().tolist()
            cube = df_test['ttl_cube'].sum()
            units = df_test['units'].sum()
            cube_pct = df_test['cube_pct'].sum()
            units_pct = df_test['units_pct'].sum()
            
            output = (Rack_Dims, target, unit_threshold, cube, units, cube_pct, units_pct)
            
            return output
        
        
        # loop over rack dims     
        rows = []
        for group in  df_new.groupby(['Rack_Dims']):
        
            df_group = pd.DataFrame(group[1]).reset_index(drop = True)
            row = list(calc_pct(df_group))     
            rows.append(row)

        df_final = pd.DataFrame(rows, columns = ['Rack_Dims','target', 'unit_threshold', 'cube','unit','cube_pct','units_pct'])
        df_final = df_final.sort_values( by ='units_pct', ascending = False)
        df_final = df_final[df_final['unit'] != 0]
    
        return df_final
   
#m = scenario_runs(df_new, target, unit_threshold)    

# run the code-----------------------------------------------------------------
root_path = r'C:\..\output\onhand'
      
unit_thresholds = [1,2,3,4,5,6,7,8]
targets = [0.75, 0.8, 0.85, 0.9, 0.95]
df_new = r.df_new

ttl_df = pd.DataFrame()

for u, t in itertools.product(unit_thresholds, targets):
    
    unit_threshold = u
    target = t
    m = scenario_runs(df_new, target, unit_threshold)       
#    folder = 'UT-' + str(unit_threshold) + '_' + 'TGF-' + str(target)
#    os.mkdir(os.path.join(root_path, str(folder)))   
#    path = os.path.join(root_path, str(folder)) 
#    m.df_final.to_csv(path + '\\df_final.csv', index = True)    
    tmp_df = m.df_final
    ttl_df = pd.concat([ttl_df, tmp_df])
    
ttl_df.to_csv(root_path + '\\ttl_df.csv', index = True)
r.df_new.to_csv(root_path + '\\df_new.csv', index = True) 
      
## print run time
endtime = datetime.datetime.now()
print (endtime - starttime)
