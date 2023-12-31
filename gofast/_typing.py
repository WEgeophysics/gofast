# -*- coding: utf-8 -*-
#   Licence:BSD 3-Clause
#   Author: LKouadio <etanoyau@gmail.com>
#   Created date: Fri Apr 10 08:46:56 2022 

""" 
`GoFast`_ Type variables
======================== 

.. _pandas DataFrame: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
.. _Series: https://pandas.pydata.org/docs/reference/api/pandas.Series.html

Some customized type variables  need to be explained for easy understanding 
in the whole package. Indeed, customized type hints is used to define the 
type of arguments. 

**M**: Suppose to be the interger variable `IntVar` to denote the number of 
    rows in the ``Array``. 
    
**N**: Like the ``M``, *N* means the number of column in the ``Array``. It 
    is bound with  integer variable. 
    
**_T**: Is known as generic type standing for `Any` type of variable. We keep 
    it unchanged. 

**U**: Unlike `_T`, `U` stands for nothing. Use to sepcify the one dimentional 
    array. For instance:: 
        
        >>> import numpy as np 
        >>> array = np.arange(4).shape 
        ... (4, )
        
**S**: Indicates the `Shape` status. It is bound by `M`, `U`, `N`. 'U' stands
    for nothing for one dimensional array. While, the common shape expects 
    for one of two dimensional arrays, it is possible to extend array for 
    more than one dimensional. The class object :class:`AddShape` is 
    created to grand all the remaining value of integers shape. 
    
**D**: Stands for  dtype object. It is bound with  :class:`DType`.

**Array**: Defined for  one dimensional array and `DType` can be specify. For 
    instance, we generated two arrays (`arr1`and `arr2`) for different types:: 
        
        >>> import numpy as np
        >>> from gofast.typing import TypeVar, Array, DType
        >>> _T = TypeVar ('_T', float) 
        >>> A = TypeVar ('A', str, bytes )
        >>> arr1:Array[_T, DType[_T]] = np.arange(21) # dtype ='float'
        >>> arr2: Array[A, DType[A]] = arr1.astype ('str') # dtype ='str'
        
**NDArray**: Stands for multi-dimensional arrays i.e more than two. Here, the 
    difference between the one dimensional type variable ``Array`` is that 
    while the latter accepts the ``DType`` argument  as the second parameter. 
    It could be turn to the number of multidimentional rows including the 
    `Array as first argument and specify the DType as the second argument 
    like this:: 
        
        >>> import numpy as np 
        >>> from gofast.typing import TypeVar, Array, NDarray, DType 
        >>> _T =TypeVar ('_T', int)
        >>> U = TypeVar ('U')
        >>> multidarray = np.arange(7, 7).astype (np.int32)
        >>> def accept_multid(
                arrays: NDArray[Array[_T, U], DType [_T]]= multidarray
                ):
            ''' asserted with MyPy and work-fine.'''
                ...
                
**_Sub**: Stands for subset. Indeed, the class is created to define the 
    conductive zone. It is a subset ``_Sub`` of ``Array``. For example, we first 
    build an array secondly extract the conductive zone from |ERP| line.
    Finally, we checked the type hint to assert whether the extracted zone 
    is a subset of the whole |ERP| line. The demo is given below:: 
        
        >>> import numpy as np 
        >>> from gofast.typing import TypeVar, DType, Array , _Sub
        >>> from gofast.tools.exmath import _define_conductive_zone
        >>> _T= TypeVar ('_T', float)
        >>> erp_array: Array[_T, DType[_T]] = np.random.randn (21) # whole line 
        >>> select_zone, _ = _define_conductive_zone (erp = erp_array , auto =True)
        >>> select_zone: Array[_T, DType[_T]]
        >>> def check_cz (select_zone: _Sub[Array]): 
                ''' assert with MyPy and return ``True`` as it works fine. '''
                ... 
                
**_SP**: Stands for Station positions. The unit of position may vary, however, 
    we keep for :mod:`gofast.method.electrical.ElectricalResistivityProfiling`
    the default unit in ``meters`` by starting at position 0. Typically,
    positions are recording according to the dipole length. For the example, 
    we can generated a position values for ``121 stations`` with dipole 
    length equals to ``50m`` i.e the length of the survey line is ``6 km``. 
    Here we go: 
        
        * Import required modules and generate the whole survey line::
            
            >>> import numpy as np 
            >>> from gofast.typing import TypeVar, DType, _SP, _Sub 
            >>> _T =TypeVar ('_T', bound =int)
            >>> surveyL:_SP = np.arange(0, 50 *121 , 50.).astype (np.int32)
            ... (work fine with MyPy )
            
        * Let's verify whether the extract data from surveyL is also a subset 
            of station positions:
                
            -  We use the following fonction to to extract the specific
                part of whole survey line `surveyL`:: 
                    
                    >>> from gofast.tools.mathex import define_conductive_zone
                    >>> subpos,_ = define_conductive_zone (surveyL, s='S10') 
                    
            -  Now, we check the instance value `subpos` as subset array of 
                of `_SP`. Note that the station 'S10' is included in the 
                extracted locations and is extented for seven points. For 
                further details, refer to `define_conductive_zone.__doc__`:: 
                
                    >>> def checksup_type (sp: _Sub[_SP[_T, DType[_T]]] = subpos ): 
                            ''' _SP is an array of positions argument `sp`  
                            shoud be asserted as a subestof the whole line.'''
                            ... 
                    ... (test verified. subpos is a subset of `_SP`) 
                    
**Series**: Stands for `pandas Series`_ object rather than using the specific 
    ``pandas.Series`` everywhere in the package. 
    
**DataFrame**: Likewise the ``Series`` generic type hint, it stands for 
    ``pandas DataFrame`_ object. It used to replace ``pandas.DataFrame`` object
    to identify the callable arguments in the whole packages. 
    Both can be instanciated as below:: 
        
        >>> import numpy as np 
        >>> import pandas pd 
        >>> from gofast.typing import TypeVar , Any, DType , Series, DataFrame
        >>> _T  =TypeVar('_T')
        >>> seriesStr = pd.Series ([f'obx{s}' for s in range(21)],
                                 name ='stringobj')
        >>> seriesFloat = pd.Series (np.arange(7).astype(np.float32),
                                 name =floatobj)
        >>> SERs = Series [DType[str]] # pass 
        >>> SERf =Series [DType [float]] # pass 
    
        ..
    
        >>> dfStr= pd.DataFrame {'ser1':seriesStr , 
                            'obj2': [f'none' for i in range (21)]}
        >>> dfFloat= pd.DataFrame {'ser1':seriesFloat , 
                            'obj2': np.linspace (3, 28 , 7)}
        >>> dfAny= pd.DataFrame {'ser1':seriesStr, 
                            'ser2':seriesFloat}
        >>> DFs  = DataFrame [SERs] | DataFrame [DType[str]]
        >>> DFf  = DataFrame [SERf] | DataFrame [DType[float]]
        >>> DFa =  DataFrame [Series[Any]] | DataFrame [DType[_T]]
       
"""
from __future__ import annotations 
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from typing import (
    List,
    Tuple,
    Sequence, 
    Dict, 
    Iterable, 
    Callable, 
    Union, 
    Any , 
    Generic,
    Optional,
    Type , 
    Mapping,
    Text,
    TypeVar, 
    Iterator,
    SupportsInt,

)

__all__=[ 
    "List",
    "Tuple",
    "Sequence", 
    "Dict", 
    "Iterable", 
    "Callable", 
    "Any" , 
    "Generic",
    "Optional",
    "Union",
    "Type" , 
    "Mapping",
    "Text",
    "Shape", 
    "DType", 
    "NDArray", 
    "ArrayLike", 
    "_Sub", 
    "_SP", 
    "_F",
    "_T", 
    "_V", 
    "Series", 
    "Iterator",
    "SupportsInt",
    ]

_T = TypeVar('_T')
_V = TypeVar('_V')
K = TypeVar('K')
M =TypeVar ('M', bound= int ) 
N= TypeVar('N',  bound =int )
U= TypeVar('U')
D =TypeVar ('D', bound ='DType')
S = TypeVar('S', bound='Shape')

class AddShape (Generic [S]): 
    """ Suppose to be an extra bound to top the `Shape` for dimensional 
    more than two. 
    
    Example 
    ------- 
    >>> import numpy as np 
    >>> np.random.randn(7, 3, 3) 
    >>> def check_valid_type (
        array: NDArray [Array[float], Shape[M, AddShape[N]]]): 
        ... 
    
    """
class Shape (Generic[M, S], AddShape[S]): 
    """ Generic to construct a tuple shape for NDarray. `Shape` has is 
    written wait for two dimensional arrays with M-row and N-columns. However 
    for three dimensional,`Optional` Type could be: 
        
    :Example: 
        >>> import numpy as np 
        >>> # For 1D array 
        >>> np
        >>> np.random.rand(7)
        >>> def check_array1d( 
            array: Array[float, Shape[M, None]])
        >>> np.random.rand (7, 7).astype('>U12'):
        >>> def check_array2d_type (
            array: NDArray[Array[str], Shape [M, N], DType ['>U12']])
        
    """
    def __getitem__ (self, M, N) -> S: 
        """ Get the type of rown and type of columns 
        and return Tuple of ``M`` and ``N``. """
        ... 
    
class DType (Generic [_T]): 
    """ DType can be Any Type so it holds '_T' type variable. """
    def __getitem__  (self, _T) -> _T: 
        """ Get Generic Type object and return Type Variable"""
        ...  
       
class ArrayLike(Generic[_T, D]): 
    """ Array Type here means the 1D array i.e singular column. 
    For multi-dimensional array we used NDArray instead. 
    """
    
    def __getitem__ (self, _T) -> Union ['ArrayLike', _T]: 
        """ Return Type of the given Type variable. """ 
        ... 
    
    
class NDArray(ArrayLike[_T, DType [_T]], Generic [_T, D ]) :
    """NDarray has ``M``rows, ``N`` -columns, `Shape` and `DType` object. 
    and Dtype. `Shape` is unbound for this class since it does not make sense
    to specify more integers. However, `DType` seems useful to provide. 
    
    :Example: 
        >>> import numpy as np 
        >>> _T= TypeVar (_T, str , float) # Dtype here is gone to be "str" 
        >>> array = np.c_[np.arange(7), np.arange(7).astype ('str')]
        >>> def test_array (array: NDArray[_T, DType [_T]]):...
    """
    def __getitem__ (self,_T ) -> _T: 
        """ Return type variable. Truly the ``NDArray``"""
        ... 
    
class _F (Generic [_T]): 
    """ Generic class dedicated for functions, methods and class and 
    return the given types i.e callable object with arguments or `Any`. 
    
    :Example: 
        >>> import functools 
        >>> def decorator (appender ='get only the documention and pass.'):
                @functools.wraps(func):
                def wrapper(*args, **kwds)
                    func.__doc__ = appender + func.__doc__
                    return func (*args, **kwds) 
                return wrapper 
        >>> @decorator  # do_nothing = decorator (anyway)
            def anyway(*args, **kwds):
                ''' Im here to '''
                ...
        >>> def check_F(anyway:_F): 
                pass 
    """
    def __getitem__ (self, item: Callable [...,_T]
                     ) -> Union ['_F', Callable[..., _T], _T, Any]:
        """ Accept any type of variable supposing to be a callable object 
        functions, methods or even classes and return the given type 
        object or another callable object  with its own or different specific 
        parameters or itself or Any."""
        return self 
    
class _Sub (Generic [_T]): 
    """ Return subset of whatever Array"""
    ... 
     
class _SP(Generic [_T, D]): 
    """ Station position arrays hold integer values of the survey location.
    Most likely, the station position is given according to the dipole length.
    Assume the dipole length is ``10 meters`` and survey is carried out on 
    21 stations. The station position array  should be an array of interger 
    values from 0. to 200 meters. as like:: 
        
        >>> import numpy as np 
        >>> positions: _SP = np.arange(0, 21 * 10, 10.
                                     ).astype (np.int32) # integer values 
    """
    ... 
    
class Series (DType[_T], Generic [_T]): 
    """ To reference the pandas `Series`_ object. 
    
    .. _Series: https://pandas.pydata.org/docs/reference/api/pandas.Series.html
    
    :Example:
        >>> import numpy as np
        >>> import pandas as pd 
        >>> from gofast.typing import DType, Series  
        >>> ser = pd.Series (np.arange (21), name ='nothing')
        
    .. code: Python 
        
        def check_type (serObj:Series): 
            ''' pass anyway'''
            ... 
        check_type (seObj: Series[DType[str]]=ser ) 
    
    """
    def __getitem__ (self, item: _T) -> 'Series': 
        """ Get the type variable of item _T and return `Series`_ object."""
        return self 
          
class DataFrame (Series[_T], Generic[_T]): 
    """ Type hint variable to illutsrate the `pandas DataFrame`_ object. 
    
    .. _pandas DataFrame: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
    .. _Series: https://pandas.pydata.org/docs/reference/api/pandas.Series.html
    
    Indeed, `pandas DataFrame`_ can be considered as an aggregation of `Series`_, 
    thus, the generic type hint variable is supposed to hold a `Series`_
    object. 
    
    :Example:
        
        >>> import numpy as np
        >>> import pandas as pd 
        >>> from gofast.typing import DType, DataFrame 
        
    .. code: Python 
         
        df =pd.DataFrame ({serie1: np.arange(7), 
                           serie2: np.linspace (0, 1000, 7), 
                           serie3: [f'0b{i} for i in range(7)]
                                    })
        def check_type (dfObj:DataFrame): 
            ... 
        ckeck_type (dfObj: DataFrame [DType [object]] =df)
    
    """
    
    def __getitem__(self, item: _T)->'DataFrame':
        """ Get the type hint variable of `pandas DataFrame`_ and return the 
        object type variable."""
        
        return self     
    
if __name__=='__main__': 
    def test (array:_Sub[_SP[ArrayLike[int, DType[int]], DType [int]]]):... 
    def test2 (array:_Sub[_SP[ArrayLike, DType [int]]]):... 
    
    DFSTR  = DataFrame [Series[DType[str]]]
    DF = DataFrame [DType [object]]
    



























