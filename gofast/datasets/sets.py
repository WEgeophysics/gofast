# -*- coding: utf-8 -*-
#   License: BSD-3-Clause
#   Author: LKouadio <etanoyau@gmail.com>

""" 
Set all dataset.  
"""
from warnings import warn 

fi=False

_DTAGS=(
    "bagoue" , 
    "iris", 
    "hlogs",
    "nlogs", 
    "mxs", 

    )

from .dload import (
    load_bagoue , 
    load_iris, 
    load_hlogs,
    load_nlogs, 
    load_mxs, 
    ) 
try : 
    from ._config import _fetch_data
except ImportError: 
    warn ("'fetch_data' seems not respond. Use 'load_<area name>'"
          " instead.")
else: fi=True 
    

__all__=[ 
         "load_bagoue" ,
         "load_iris", 
         "load_hlogs",
         "load_nlogs", 
         "fetch_data",
         "load_mxs", 
         "DATASET"
         ]

def fetch_data (tag, **kws): 
    tag = _parse_tags(tag, multi_kind_dataset='bagoue')
    func= _fetch_data if fi else None 
    funcs= (load_bagoue , load_iris, load_hlogs, load_nlogs, load_mxs ) 
    funcns = list (map(lambda f: f.__name__.replace('load_', ''), funcs))
    if tag in (funcns): 
        func = funcs[funcns.index (tag)] 
    
    return func (tag=tag, data_names=funcns, **kws) if callable (func) else None 


fetch_data.__doc__ ="""\
Fetch dataset from `tag`. 

A tag corresponds to the name area of data collection or each 
level of data processing. 

Parameters 
------------
tag: str, ['bagoue', 'hlogs', 'nlogs', ]
    name of the area of data to fetch. For instance set the tag to ``bagoue`` 
    will load the bagoue datasets. If the `tag` name is following by a suffix, 
    the later specifies the stage of the data processing. As an example, 
    `bagoue original` or `bagoue prepared` will retrieve the original data and 
    the transformed data after applying default transformers respectively. 
    
    There are different options to retrieve data such as:
        
    * ['original'] => original or raw data -& returns a dict of details 
        contex combine with get method to get the dataframe like::
            
            >>> fetch_data ('bagoue original').get ('data=df')
            
    * ['stratified'] => stratification data
    * ['mid' |'semi'|'preprocess'|'fit']=> data cleaned with 
        attributes experience combinaisons.
    * ['pipe']=>  default pipeline created during the data preparing.
    * ['analyses'|'pca'|'reduce dimension']=> data with text attributes
        only encoded using the ordinal encoder +  attributes  combinaisons. 
    * ['test'] => stratified test set data

Returns
-------
dict, X, y : frame of :class:`~gofast.tools.box.Boxspace` object 
    If tag is following by suffix in the case of 'bagoue' area, it returns:
        - `data`: Original data 
        - `X`, `y` : Stratified train set and training target 
        - `X0`, `y0`: data cleaned after dropping useless features and combined 
            numerical attributes combinaisons if ``True``
        - `X_prepared`, `y_prepared`: Data prepared after applying  all the 
            transformation via the transformer (pipeline). 
        - `XT`, `yT` : stratified test set and test label  
        - `_X`: Stratified training set for data analysis. So None sparse
            matrix is contained. The text attributes (categorical) are 
            converted using Ordianal Encoder.  
        - `_pipeline`: the default pipeline. 
Examples 
---------
>>> from gofast.datasets import fetch_data 
>>> b = fetch_data('bagoue' ) # no suffix returns 'Boxspace' object
>>> b.tnames 
... array(['flow'], dtype='<U4')
>>> b.feature_names 
... ['num',
     'name',
     'east',
     'north',
     'power',
     'magnitude',
     'shape',
     'type',
     'sfi',
     'ohmS',
     'lwi',
     'geol']
>>> X, y = fetch_data('bagoue prepared' )
>>> X # is transformed  # ready for prediction 
>>> X[0] 
... <1x18 sparse matrix of type '<class 'numpy.float64'>'
	with 8 stored elements in Compressed Sparse Row format>
>>> y
... array([2, 1, 2, 2, 1, 0, ... , 3, 2, 3, 3, 2], dtype=int64)

"""    

def _parse_tags (tag, multi_kind_dataset ='bagoue'): 
    """ Parse and sanitize tag to match the different type of datasets.
    
    In principle, only the 'Bagoue' datasets is allowed to contain a tag 
    composed of two words i.e. 'Bagoue' + '<kind_of_data>'. For instance 
    ``bagoue pipe`` fetchs only the pipeline used for Bagoue case study  
    data preprocessing and so on. 
    However , for other type of dataset, it a second word <kind_of_data> is 
    passed, it should merely discarded. 
    """ 
    tag = str(tag);  t = tag.strip().split() 
    
    if len(t) ==1 : 
        if t[0].lower() not in _DTAGS: 
            tag = multi_kind_dataset +' ' + t[0]
            
            warn(f"Fetching {multi_kind_dataset.title()!r} data without"
                 " explicitly prefixing the kind of data with the area"
                 " name will raise an error. In future, the argument"
                f" should be '{tag}' instead.", FutureWarning 
                 )
    elif len(t) >1 : 
        # only the multi kind dataset is allowed 
        # to contain two words for fetching data 
        if t[0].lower() !=multi_kind_dataset: 
            tag = t[0].lower() # skip the second word 
    return tag 

from ..tools.funcutils import listing_items_format

_l=[ "{:<7}: {:<7}()".format(s.upper() , 'load_'+s ) for s in _DTAGS ] 
_LST = listing_items_format(
    _l, 
    "Fetch data using 'load_<type_of_data|area_name>'like", 
    " or using ufunc 'fetch_data (<type_of_data|area_name>)'.",
    inline=True , verbose= False, 
)

_DDOC="""\
gofast dataset is composed of different kind of data for software implementation. 
    - NLOGS data found in 'nlogs', for land subsidence data.
    - FLOW RATE FEATURES data computed from Bagoue ERP and VES data. 
      Refer to paper :doi:`https://doi.org/10.1029/2021wr031623`. 
    - COMMON MACHINE LEARNING popular data sets such IRIS. 
    - EDI datasets from huayaun county in China, Hunan Province. 
    - HLOGS and MXS data  hydrogeological engineering logging raw and 
      preprocessed borehole data. 
"""
    
DATASET= type ("DATASET", (), {"KIND": _DTAGS, 
                               "HOW":_LST, 
                               "DOC":_DDOC, 
                               }
)
 