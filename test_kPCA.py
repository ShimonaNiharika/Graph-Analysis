#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 14:26:22 2018

@author: niharika-shimona
"""

import sys,os
import numpy as np
import pickle
import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as plt
# plt.ioff()
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error,explained_variance_score,mean_absolute_error,r2_score,make_scorer
from sklearn.model_selection import GridSearchCV, KFold

import scipy.io as sio
from Data_Extraction import Split_class,create_dataset
from sklearn.decomposition import KernelPCA as sklearnKPCA
from sklearn.linear_model import LinearRegression


#df_aut,df_cont = Split_class()
#task  = 'SRS.TotalRaw.Score'
#ds = '1'
#
#x_aut,y_aut,x_cont,y_cont = create_dataset(df_aut,df_cont,task,'/home/niharika-shimona/Documents/Projects/Autism_Network/code/patient_data/')	
#
#if ds == '0':	
# 	x = x_cont
# 	y= np.ravel(y_cont)
# 	fold = 'cont'
# 	
#elif ds == '1':
# 	x = x_aut
# 	y= np.ravel(y_aut)
# 	fold = 'aut'
# 	
#else:
# 	x =np.concatenate((x_cont,x_aut),axis =0)
# 	y = np.ravel(np.concatenate((y_cont,y_aut),axis =0))
# 	fold = 'aut_cont'

pathname = '/media/nsalab/Users/ndsouza4/Schizophrenia/'
task = 'NCC_eig'
cas = 'buf'
filename = pathname + task +'.mat'

data = sio.loadmat(filename)
subtx = 'x_'+ cas
data_eg_corr = data[subtx]

x = data_eg_corr
subty = 'y_'+ cas
y =np.ravel(data[subty])



kpca = sklearnKPCA(kernel="rbf")
cast = 'kernel' 
#pipeline = Pipeline([('kPCA',kpca), ('rf_reg',rf_reg)])
n_comp = [10]
c_range = np.logspace(-3,6,3)
min_samples_split = np.int16(np.linspace(2,16,8))

p_grid = [{'kPCA__n_components': n_comp, 'kPCA__gamma': c_range,'rf_reg__min_samples_split': min_samples_split}]

kf_total = KFold(n_splits=10,shuffle=False, random_state=6)
my_scorer = make_scorer(explained_variance_score)

#lrgs = GridSearchCV(estimator=pipeline, param_grid=p_grid, cv =kf_total, scoring =my_scorer, n_jobs=-1)
#lrgs.fit(x,y)
#param_best = lrgs.best_params_

y_train =[]
y_test = []
y_train_AF =[]
y_test_AF =[]
r2_test = []
mse_test =[]
learnt_models =[]
i = 0

for train,test in kf_total.split(x,y):
    
#    model = pipeline.set_params(**param_best)
#    model.fit(x[train],y[train])
#     x_comp = x
    
    
    #    "Unfair selection of top 5 contributing features"
    rf_reg = RandomForestRegressor(n_estimators=1000,oob_score= True) 	
    rf_reg.fit(x[train],y[train])
    a = rf_reg.feature_importances_
    feat_ind_sort = [b[0] for b in sorted(enumerate(a),key=lambda i:i[1])]

    n_feat =5

    for i in range(np.shape(x)[0]):
    
         b = [x[i][j] for j in feat_ind_sort[-n_feat:]]
         b= np.reshape(b,[1,n_feat])
        
         if(i==0): 
            x_comp =  b
         else:
            x_comp =  np.concatenate((x_comp,b), axis=0)     
      
    model = LinearRegression()
    
    model.fit(x_comp[train],y[train])
    y_pred_train = model.predict(x_comp[train])
    y_pred_test = model.predict(x_comp[test])
    r2_test.append(r2_score(y[test],y_pred_test))
    mse_test.append(mean_squared_error(y[test],y_pred_test))

    y_train_AF = np.concatenate((y_train_AF,y_pred_train),axis =0)
    y_train = np.concatenate((y_train,y[train]),axis =0)
    y_test_AF = np.concatenate((y_test_AF,y_pred_test),axis =0)
    y_test = np.concatenate((y_test,y[test]),axis =0)
	
    learnt_models.append(model)
     
#newpath = r'/home/niharika-shimona/Documents/Projects/Autism_Network/Results/Sanity_Check/Comparative_Analysis/Kernel/'+fold+'/' + cast +'/' + task + '/'
newpath = r'/home/niharika-shimona/Documents/Projects/Autism_Network/Results/Sanity_Check/Comparative_Analysis/Feat_Select/' + task + '/'

if not os.path.exists(newpath):
 	os.makedirs(newpath)
os.chdir(newpath)

fig,ax =plt.subplots()
font = {'family' : 'normal',
         'weight' : 'bold',
         'size'   : 14}
matplotlib.rc('font', **font)

ax.scatter(y_train,y_train_AF,color ='red',label = 'train')
ax.plot([y_test.min(),y_test.max()], [y_test.min(),y_test.max()], 'k--', lw=4)
ax.plot([y_test.min()-2,y_test.max()+2], [y_test.min()-2, y_test.max()+2], 'k--', lw=4)
data_mean = np.mean(y_test)
#ax.plot([y_test.min()-2,y_test.max()+2], [data_mean,data_mean], 'k--', lw=2)
plt.ylim(ymax = y_test.max()+5, ymin = y_test.min()-5)
plt.xlim(xmax =y_test.max()+5, xmin = y_test.min()-5)
# plt.ylim(ymax = 29, ymin = 5)
# plt.xlim(xmax =25, xmin = 5)
ax.scatter(y_test,y_test_AF,color ='green',label = 'test')
ax.legend(loc='best')

ax.set_xlabel('Measured',fontsize =14)
ax.set_ylabel('Predicted',fontsize =14)

ax.legend(loc='upper left')
matplotlib.rc('font', **font)	
plt.show()

figname = 'fig_test_pres_5.png'
fig.savefig(figname)   # save the figure to fil

sio.savemat('Metrics_full.mat',{'r2_test':r2_test,'mse_test':mse_test,'y_pred':y_test_AF,'y_test':y_test,'y_pred_train':y_train_AF,'y_train':y_train})
pickle.dump(learnt_models, open('Models.p', 'wb'))
pickle.dump(kf_total, open('Kfold.p', 'wb')) 