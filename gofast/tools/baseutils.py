# -*- coding: utf-8 -*-
#   License: BSD-3-Clause
#   Author: LKouadio <etanoyau@gmail.com>
from __future__ import ( 
    annotations , 
    print_function 
    )
import os
import copy
import shutil 
from six.moves import urllib 
import pathlib
import warnings 
from joblib import Parallel, delayed
import numpy as np 
import pandas as pd 

from .._typing import ( 
    Any, 
    List, 
    NDArray, 
    DataFrame, 
    )
from ..exceptions import FileHandlingError 
from ..property import  Config
from .funcutils import ( 
    is_iterable, 
    ellipsis2false,
    smart_format,
    sPath, 
    to_numeric_dtypes, 
    assert_ratio
    )
from ._dependency import ( 
    import_optional_dependency 
    )
from .validator import array_to_frame

def read_data (
    f: str|pathlib.PurePath, 
    sanitize: bool= ..., 
    reset_index: bool=..., 
    comments: str="#", 
    delimiter: str=None, 
    columns: List[str]=None,
    npz_objkey: str= None, 
    verbose: bool= ..., 
    **read_kws
 ) -> DataFrame: 
    """ Assert and read specific files and url allowed by the package
    
    Readable files are systematically convert to a data frame.  
    
    Parameters 
    -----------
    f: str, Path-like object 
       File path or Pathlib object. Must contain a valid file name  and 
       should be a readable file or url 
        
    sanitize: bool, default=False, 
       Push a minimum sanitization of the data such as: 
           - replace a non-alphabetic column items with a pattern '_' 
           - cast data values to numeric if applicable 
           - drop full NaN columns and rows in the data 
           
    reset_index: bool, default=False, 
      Reset index if full NaN columns are dropped after sanitization. 
      
      .. versionadded:: 0.2.5
          Apply minimum data sanitization after reading data. 
     
    comments: str or sequence of str or None, default='#'
       The characters or list of characters used to indicate the start 
       of a comment. None implies no comments. For backwards compatibility, 
       byte strings will be decoded as 'latin1'. 

    delimiter: str, optional
       The character used to separate the values. For backwards compatibility, 
       byte strings will be decoded as 'latin1'. The default is whitespace.

    npz_objkey: str, optional 
       Dataset key to indentify array in multiples array storages in '.npz' 
       format.  If key is not set during 'npz' storage, ``arr_0`` should 
       be used. 
      
       .. versionadded:: 0.2.7 
          Capable to read text and numpy formats ('.npy' and '.npz') data. Note
          that when data is stored in compressed ".npz" format, provided the 
          '.npz' object key  as argument of parameter `npz_objkey`. If None, 
          only the first array should be read and ``npz_objkey='arr_0'``. 
          
    verbose: bool, default=0 
       Outputs message for user guide. 
       
    read_kws: dict, 
       Additional keywords arguments passed to pandas readable file keywords. 
        
    Returns 
    -------
    f: :class:`pandas.DataFrame` 
        A dataframe with head contents by default.  
        
    See Also 
    ---------
    np.loadtxt: 
        load text file.  
    np.load 
       Load uncompressed or compressed numpy `.npy` and `.npz` formats. 
    watex.tools.baseutils.save_or_load: 
        Save or load numpy arrays.
       
    """
    def min_sanitizer ( d, /):
        """ Apply a minimum sanitization to the data `d`."""
        return to_numeric_dtypes(
            d, sanitize_columns= True, 
            drop_nan_columns= True, 
            reset_index=reset_index, 
            verbose = verbose , 
            fill_pattern='_', 
            drop_index = True
            )
    sanitize, reset_index, verbose = ellipsis2false (
        sanitize, reset_index, verbose )
    if ( isinstance ( f, str ) 
            and str(os.path.splitext(f)[1]).lower()in (
                '.txt', '.npy', '.npz')
            ): 
        f = save_or_load(f, task = 'load', comments=comments, 
                         delimiter=delimiter )
        # if extension is .npz
        if isinstance(f, np.lib.npyio.NpzFile):
            npz_objkey = npz_objkey or "arr_0"
            f = f[npz_objkey] 

        if columns is not None: 
            columns = is_iterable(columns, exclude_string= True, 
                                  transform =True, parse_string =True 
                                  )
            if len( columns )!= f.shape [1]: 
                warnings.warn(f"Columns expect {f.shape[1]} attributes."
                              f" Got {len(columns)}")
            
        f = pd.DataFrame(f, columns=columns )
        
    if isinstance (f, pd.DataFrame): 
        if sanitize: 
            f = min_sanitizer (f)
        return  f 
    
    cpObj= Config().parsers 
    f= _check_readable_file(f)
    _, ex = os.path.splitext(f) 
    if ex.lower() not in tuple (cpObj.keys()):
        raise TypeError(f"Can only parse the {smart_format(cpObj.keys(), 'or')} files"
                        )
    try : 
        f = cpObj[ex](f, **read_kws)
    except FileNotFoundError:
        raise FileNotFoundError (
            f"No such file in directory: {os.path.basename (f)!r}")
    except BaseException as e : 
        raise FileHandlingError (
            f"Cannot parse the file : {os.path.basename (f)!r}. "+  str(e))
    if sanitize: 
        f = min_sanitizer (f)
        
    return f 
    
def _check_readable_file (f): 
    """ Return file name from path objects """
    msg =(f"Expects a Path-like object or URL. Please, check your"
          f" file: {os.path.basename(f)!r}")
    if not os.path.isfile (f): # force pandas read html etc 
        if not ('http://'  in f or 'https://' in f ):  
            raise TypeError (msg)
    elif not isinstance (f,  (str , pathlib.PurePath)): 
         raise TypeError (msg)
    if isinstance(f, str): f =f.strip() # for consistency 
    return f 


def array2hdf5 (
    filename: str, /, 
    arr: NDArray=None , 
    dataname: str='data',  
    task: str='store', 
    as_frame: bool =..., 
    columns: List[str, ...]=None, 
)-> NDArray | DataFrame: 
    """ Load or write array to hdf5
    
    Parameters 
    -----------
    arr: Arraylike ( m_samples, n_features) 
      Data to load or write 
    filename: str, 
      Hdf5 disk file name whether to write or to load 
    task: str, {"store", "load", "save", default='store'}
       Action to perform. user can use ['write'|'store'] interchnageably. Both 
       does the same task. 
    as_frame: bool, default=False 
       Concert loaded array to data frame. `Columns` can be supplied 
       to construct the datafame. 
    columns: List, Optional 
       Columns used to construct the dataframe. When its given, it must be 
       consistent with the shape of the `arr` along axis 1 
       
    Returns 
    ---------
    None| data: ArrayLike or pd.DataFrame 
    
    Examples 
    ----------
    >>> import numpy as np 
    >>> from gofast.tools.baseutils import array2hdf5
    >>> data = np.random.randn (100, 27 ) 
    >>> array2hdf5 ('test.h5', data   )
    >>> load_data = array2hdf5 ( 'test.h5', data, task ='load')
    >>> load_data.shape 
    Out[177]: (100, 27)
    """
    import_optional_dependency("h5py")
    import h5py 
    
    arr = is_iterable( arr, exclude_string =True, transform =True )
    act = copy.deepcopy(task)
    task = str(task).lower().strip() 
    
    if task in ("write", "store", "save"): 
        task ='store'
    assert task in {"store", "load"}, ("Expects ['store'|'load'] as task."
                                         f" Got {act!r}")
    # for consistency 
    arr = np.array ( arr )
    h5fname = str(filename).replace ('.h5', '')
    if task =='store': 
        if arr is None: 
            raise TypeError ("Array cannot be None when the task"
                             " consists to write a file.")
        with h5py.File(h5fname + '.h5', 'w') as hf:
            hf.create_dataset(dataname,  data=arr)
            
    elif task=='load': 
        with h5py.File(h5fname +".h5", 'r') as hf:
            data = hf[dataname][:]
            
        if  ellipsis2false( as_frame )[0]: 
            data = pd.DataFrame ( data , columns = columns )
            
    return data if task=='load' else None 
   
def lowertify (*values, strip = True, return_origin: bool =... ): 
    """ Strip and convert value to lowercase. 
    
    :param value: str , value to convert 
    :return: value in lowercase and original value. 
    
    :Example: 
        >>> from gofast.tools.baseutils import lowertify 
        >>> lowertify ( 'KIND')
        Out[19]: ('kind',)
        >>> lowertify ( "KIND", return_origin =True )
        Out[20]: (('kind', 'KIND'),)
        >>> lowertify ( "args1", 120 , 'ArG3') 
        Out[21]: ('args1', '120', 'arg3')
        >>> lowertify ( "args1", 120 , 'ArG3', return_origin =True ) 
        Out[22]: (('args1', 'args1'), ('120', 120), ('arg3', 'ArG3'))
        >>> (kind, kind0) , ( task, task0 ) = lowertify(
            "KIND", "task ", return_origin =True )
        >>> kind, kind0, task, task0 
        Out[23]: ('kind', 'KIND', 'task', 'task ')
        """
    raw_values = copy.deepcopy(values ) 
    values = [ str(val).lower().strip() if strip else str(val).lower() 
              for val in values]

    return tuple (zip ( values, raw_values)) if ellipsis2false (
        return_origin)[0]  else tuple (values)

def save_or_load(
    fname:str, /,
    arr: NDArray=None,  
    task: str='save', 
    format: str='.txt', 
    compressed: bool=...,  
    comments: str="#",
    delimiter: str=None, 
    **kws 
): 
    """Save or load Numpy array. 
    
    Parameters 
    -----------
    fname: file, str, or pathlib.Path
       File or filename to which the data is saved. 
       - >.npy , .npz: If file is a file-object, then the filename is unchanged. 
       If file is a string or Path, a .npy extension will be appended to the 
       filename if it does not already have one. 
       - >.txt: If the filename ends in .gz, the file is automatically saved in 
       compressed gzip format. loadtxt understands gzipped files transparently.
       
    arr: 1D or 2D array_like
      Data to be saved to a text, npy or npz file.
      
    task: str {"load", "save"}
      Action to perform. "Save" for storing file into the format 
      ".txt", "npy", ".npz". "load" for loading the data from storing files. 
      
    format: str {".txt", ".npy", ".npz"}
       The kind of format to save and load.  Note that when loading the 
       compressed data saved into `npz` format, it does not return 
       systematically the array rather than `np.lib.npyio.NpzFile` files. 
       Use either `files` attributes to get the list of registered files 
       or `f` attribute dot the data name to get the loaded data set. 

    compressed: bool, default=False 
       Compressed the file especially when file format is set to `.npz`. 

    comments: str or sequence of str or None, default='#'
       The characters or list of characters used to indicate the start 
       of a comment. None implies no comments. For backwards compatibility, 
       byte strings will be decoded as 'latin1'. This is useful when `fname`
       is in `txt` format. 
      
     delimiter: str,  optional
        The character used to separate the values. For backwards compatibility, 
        byte strings will be decoded as 'latin1'. The default is whitespace.
        
    kws: np.save ,np.savetext,  np.load , np.loadtxt 
       Additional keywords arguments for saving and loading data. 
       
    Return 
    ------
    None| data: ArrayLike 
    
    Examples 
    ----------
    >>> import numpy as np 
    >>> from gofast.tools.baseutils import save_or_load 
    >>> data = np.random.randn (2, 7)
    >>> # save to txt 
    >>> save_or_load ( "test.txt" , data)
    >>> save_or_load ( "test",  data, format='.npy')
    >>> save_or_load ( "test",  data, format='.npz')
    >>> save_or_load ( "test_compressed",  data, format='.npz', compressed=True )
    >>> # load files 
    >>> save_or_load ( "test.txt", task ='load')
    Out[36]: 
    array([[ 0.69265852,  0.67829574,  2.09023489, -2.34162127,  0.48689125,
            -0.04790965,  1.36510779],
           [-1.38349568,  0.63050939,  0.81771051,  0.55093818, -0.43066737,
            -0.59276321, -0.80709192]])
    >>> save_or_load ( "test.npy", task ='load')
    Out[39]: array([-2.34162127,  0.55093818])
    >>> save_or_load ( "test.npz", task ='load')
    <numpy.lib.npyio.NpzFile at 0x1b0821870a0>
    >>> npzo = save_or_load ( "test.npz", task ='load')
    >>> npzo.files
    Out[44]: ['arr_0']
    >>> npzo.f.arr_0
    Out[45]: 
    array([[ 0.69265852,  0.67829574,  2.09023489, -2.34162127,  0.48689125,
            -0.04790965,  1.36510779],
           [-1.38349568,  0.63050939,  0.81771051,  0.55093818, -0.43066737,
            -0.59276321, -0.80709192]])
    >>> save_or_load ( "test_compressed.npz", task ='load')
    ...
    """
    r_formats = {"npy", "txt", "npz"}
   
    (kind, kind0), ( task, task0 ) = lowertify(
        format, task, return_origin =True )
    
    assert  kind.replace ('.', '') in r_formats, (
        f"File format expects {smart_format(r_formats, 'or')}. Got {kind0!r}")
    kind = '.' + kind.replace ('.', '')
    assert task in {'save', 'load'}, ( 
        "Wrong task {task0!r}. Valid tasks are 'save' or 'load'") 
    
    save= {'.txt': np.savetxt, '.npy':np.save,  
           ".npz": np.savez_compressed if ellipsis2false(
               compressed)[0] else np.savez 
           }
    if task =='save': 
        arr = np.array (is_iterable( arr, exclude_string= True, 
                                    transform =True ))
        save.get(kind) (fname, arr, **kws )
        
    elif task =='load': 
         ext = os.path.splitext(fname)[1].lower() 
         if ext not in (".txt", '.npy', '.npz', '.gz'): 
             raise ValueError ("Unrecognized file format {ext!r}."
                               " Expect '.txt', '.npy', '.gz' or '.npz'")
         if ext in ('.txt', '.gz'): 
            arr = np.loadtxt ( fname , comments= comments, 
                              delimiter= delimiter,   **kws ) 
         else : 
            arr = np.load(fname,**kws )
         
    return arr if task=='load' else None 
 
#XXX TODO      
def request_data (
    url:str, /, 
    task: str='get',
    data: Any=None, 
    as_json: bool=..., 
    as_text: bool = ..., 
    stream: bool=..., 
    raise_status: bool=..., 
    save2file: bool=..., 
    filename:str =None, 
    **kws
): 
    """ Fetch remotely data
 
    Request data remotely 
    https://docs.python-requests.org/en/latest/user/quickstart/#raw-response-content
    
    
    r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
    r.status_code
    200
    r.headers['content-type']
    'application/json; charset=utf8'
    r.encoding
    'utf-8'
    r.text
    '{"type":"User"...'
    r.json()
    {'private_gists': 419, 'total_private_repos': 77, ...}
    
    """
    import_optional_dependency('requests' ) 
    import requests 
    
    as_text, as_json, stream, raise_status, save2file = ellipsis2false(
        as_text, as_json,  stream, raise_status , save2file)
    
    if task=='post': 
        r = requests.post(url, data =data , **kws)
    else: r = requests.get(url, stream = stream , **kws)
    
    if save2file and stream: 
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    if raise_status: 
        r.raise_for_status() 
        
    return r.text if as_text else ( r.json () if as_json else r )

def get_remote_data(
    rfile:str, /,  
    savepath: str=None, 
    raise_exception: bool =True
): 
    """ Try to retrieve data from remote.
    
    Parameters 
    -------------
    rfile: str or PathLike-object 
       Full path to the remote file. It can be the path to the repository 
       root toward the file name. For instance, to retrieve the file 
       ``'AGSO.csv'`` which is located in ``gofast/etc/`` directory then the 
       full path should be ``'gofast/etc/AGSO.csv'``
        
    savepath: str, optional 
       Full path to place where to downloaded files should be located. 
       If ``None`` data is saved to the current directory.
     
    raise_exception: bool, default=True 
      raise exception if connection failed. 
      
    Returns 
    ----------
    status: bool, 
      ``False`` for failure and ``True`` otherwise i.e. successfully 
       downloaded. 
       
    """
    connect_reason ="""\
    ConnectionRefusedError: No connection could  be made because the target 
    machine actively refused it.There are some possible reasons for that:
     1. Server is not running as well. Hence it won't listen to that port. 
         If it's a service you may want to restart the service.
     2. Server is running but that port is blocked by Windows Firewall
         or other firewall. You can enable the program to go through 
         firewall in the inbound list.
    3. there is a security program on your PC, i.e a Internet Security 
        or Antivirus that blocks several ports on your PC.
    """  
    #git_repo , git_root= AGSO_PROPERTIES['GIT_REPO'], AGSO_PROPERTIES['GIT_ROOT']
    # usebar bar progression
    print(f"---> Please wait while fetching {rfile!r}...")
    try: import_optional_dependency ("tqdm")
    except:pbar = range(3) 
    else: 
        import tqdm  
        data =os.path.splitext( os.path.basename(rfile))[0]
        pbar = tqdm.tqdm (total=3, ascii=True, 
                          desc =f'get-{os.path.basename(rfile)}', 
                          ncols =97
                          )
    status=False
    root, rfile  = os.path.dirname(rfile), os.path.basename(rfile)
    for k in range(3):
        try :
            urllib.request.urlretrieve(root,  rfile )
        except: 
            try :
                with urllib.request.urlopen(root) as response:
                    with open( rfile,'wb') as out_file:
                        data = response.read() # a `bytes` object
                        out_file.write(data)
            except TimeoutError: 
                if k ==2: 
                    print("---> Established connection failed because"
                       "connected host has failed to respond.")
            except:pass 
        else : 
            status=True
            break
        try: pbar.update (k+1)
        except: pass 
    
    if status: 
        try: 
            pbar.update (3)
            pbar.close ()
        except:pass
        # print(f"\n---> Downloading {rfile!r} was successfully done.")
    else: 
        print(f"\n---> Failed to download {rfile!r}.")
    # now move the file to the right place and create path if dir not exists
    if savepath is not None: 
        if not os.path.isdir(savepath): 
            sPath (savepath)
        shutil.move(os.path.realpath(rfile), savepath )
        
    if not status:
        if raise_exception: 
            raise ConnectionRefusedError(connect_reason.replace (
                "ConnectionRefusedError:", "") )
        else: print(connect_reason )
    
    return status


def download_file(url, local_filename , dstpath =None ):
    """download a remote file. 
    
    Parameters 
    -----------
    url: str, 
      Url to where the file is stored. 
    loadl_filename: str,
      Name of the local file 
      
    dstpath: Optional 
      The destination path to save the downloaded file. 
      
    Return 
    --------
    None, local_filename
       None if the `dstpath` is supplied and `local_filename` otherwise. 
       
    Example 
    ---------
    >>> from gofast.tools.baseutils import download_file
    >>> url = 'https://raw.githubusercontent.com/WEgeophysics/gofast/master/gofast/datasets/data/h.h5'
    >>> local_filename = 'h.h5'
    >>> download_file(url, local_filename, test_directory)    
    
    """
    import_optional_dependency("requests") 
    import requests 
    print("{:-^70}".format(f" Please, Wait while {os.path.basename(local_filename)}"
                          " is downloading. ")) 
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    local_filename = os.path.join( os.getcwd(), local_filename) 
    
    if dstpath: 
         move_file ( local_filename,  dstpath)
         
    print("{:-^70}".format(" ok! "))
    
    return None if dstpath else local_filename

def fancier_downloader(url, local_filename, dstpath =None ):
    """ Download remote file with a bar progression. 
    
    Parameters 
    -----------
    url: str, 
      Url to where the file is stored. 
    loadl_filename: str,
      Name of the local file 
      
    dstpath: Optional 
      The destination path to save the downloaded file. 
      
    Return 
    --------
    None, local_filename
       None if the `dstpath` is supplied and `local_filename` otherwise. 
    Example
    --------
    >>> from gofast.tools.baseutils import fancier_downloader
    >>> url = 'https://raw.githubusercontent.com/WEgeophysics/gofast/master/gofast/datasets/data/h.h5'
    >>> local_filename = 'h.h5'
    >>> download_file(url, local_filename)

    """
    import_optional_dependency("requests") 
    import requests 
    try : 
        import_optional_dependency("tqdm")
        from tqdm import tqdm
    except: 
        # if tqm is not install 
        return download_file (url, local_filename, dstpath  )
        
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        # Get the total file size from header
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        block_size = 1024 # 1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', 
                            unit_scale=True, ncols=77, ascii=True)
        with open(local_filename, 'wb') as f:
            for data in r.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()
        
    local_filename = os.path.join( os.getcwd(), local_filename) 
    
    if dstpath: 
         move_file ( local_filename,  dstpath)
         
    return local_filename


def move_file(file_path, directory):
    """ Move file to a directory. 
    
    Create a directory if not exists. 
    
    Parameters 
    -----------
    file_path: str, 
       Path to the local file 
    directory: str, 
       Path to locate the directory.
    
    Example 
    ---------
    >>> from gofast.tools.baseutils import move_file
    >>> file_path = 'path/to/your/file.txt'  # Replace with your file's path
    >>> directory = 'path/to/your/directory'  # Replace with your directory's path
    >>> move_file(file_path, directory)
    """
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Move the file to the directory
    shutil.move(file_path, os.path.join(directory, os.path.basename(file_path)))

def check_file_exists(package, resource):
    """
    Check if a file exists in a package's directory with 
    importlib.resources.

    :param package: The package containing the resource.
    :param resource: The resource (file) to check.
    :return: Boolean indicating if the resource exists.
    
    :example: 
        >>> from gofast.tools.baseutils import check_file_exists
        >>> package_name = 'gofast.datasets.data'  # Replace with your package name
        >>> file_name = 'h.h5'    # Replace with your file name

        >>> file_exists = check_file_exists(package_name, file_name)
        >>> print(f"File exists: {file_exists}")
    """
    import_optional_dependency("importlib")
    import importlib.resources as pkg_resources
    return pkg_resources.is_resource(package, resource)

def _is_readable (
        f:str, 
        *, 
        as_frame:bool=False, 
        columns:List[str]=None,
        input_name='f', 
        **kws
 ) -> DataFrame: 
    """ Assert and read specific files and url allowed by the package
    
    Readable files are systematically convert to a pandas frame.  
    
    Parameters 
    -----------
    f: Path-like object -Should be a readable files or url  
    columns: str or list of str 
        Series name or columns names for pandas.Series and DataFrame. 
        
    to_frame: str, default=False
        If ``True`` , reconvert the array to frame using the columns orthewise 
        no-action is performed and return the same array.
    input_name : str, default=""
        The data name used to construct the error message. 
        
    raise_warning : bool, default=True
        If True then raise a warning if conversion is required.
        If ``ignore``, warnings silence mode is triggered.
    raise_exception : bool, default=False
        If True then raise an exception if array is not symmetric.
        
    force:bool, default=False
        Force conversion array to a frame is columns is not supplied.
        Use the combinaison, `input_name` and `X.shape[1]` range.
        
    kws: dict, 
        Pandas readableformats additional keywords arguments. 
    Returns
    ---------
    f: pandas dataframe 
         A dataframe with head contents... 
    
    """
    if hasattr (f, '__array__' ) : 
        f = array_to_frame(
            f, 
            to_frame= True , 
            columns =columns, 
            input_name=input_name , 
            raise_exception= True, 
            force= True, 
            )
        return f 

    cpObj= Config().parsers 
    
    f= _check_readable_file(f)
    _, ex = os.path.splitext(f) 
    if ex.lower() not in tuple (cpObj.keys()):
        raise TypeError(f"Can only parse the {smart_format(cpObj.keys(), 'or')} "
                        f" files not {ex!r}.")
    try : 
        f = cpObj[ex](f, **kws)
    except FileNotFoundError:
        raise FileNotFoundError (
            f"No such file in directory: {os.path.basename (f)!r}")
    except: 
        raise FileHandlingError (
            f" Can not parse the file : {os.path.basename (f)!r}")

    return f 
    
def scrape_web_data(
    url, element, 
    class_name=None
    ):
    """
    Scrape data from a web page.

    Parameters
    ----------
    url : str
        The URL of the web page to scrape.

    element : str
        The HTML element to search for.

    class_name : str, optional
        The class attribute of the HTML element to 
        narrow down the search.
    
    Returns
    -------
    list of bs4.element.Tag
        A list of BeautifulSoup Tag objects that match the search query.

    Examples
    --------
    >>> url = 'https://example.com'
    >>> element = 'div'
    >>> class_name = 'content'
    >>> data = scrape_web_data(url, element, class_name)
    >>> for item in data:
    >>>     print(item.text)
    # Assuming the function scrape_web_data is defined as above.

    >>> url = 'https://example.com/articles'
    >>> element = 'h1'
    >>> data = scrape_web_data(url, element)

    >>> for header in data:
           print(header.text)  # prints the text of each <h1> tag

    """
    
    import_optional_dependency('requests' ) 
    extra= (" Needs `BeautifulSoup` from `bs4` package" )
    import_optional_dependency('bs4', extra = extra  ) 
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        if class_name:
            elements = soup.find_all(element, class_=class_name)
        else:
            elements = soup.find_all(element)
        return elements
    else:
        response.raise_for_status()  
    
    
def audit_data(
    data, 
    /, 
    dropna_threshold=0.5, 
    categorical_threshold=10, 
    standardize=True
    ):
    """
    Cleans and formats a dataset for analysis. 
    This includes handling missing values,
    converting data types, and standardizing numerical columns.

    Parameters
    ----------
    data : pd.DataFrame
        The dataset to be cleaned and formatted.

    dropna_threshold : float, optional
        The threshold for dropping columns with missing values. 
        Columns with a fraction of missing values greater than 
        this threshold will be dropped.
        Default is 0.5 (50%).

    categorical_threshold : int, optional
        The maximum number of unique values in a column for it to 
        be considered categorical.
        Columns with unique values fewer than or equal to this 
        number will be converted to 
        categorical type. Default is 10.

    standardize : bool, optional
        If True, standardize numerical columns to have a mean of 0 
        and a standard deviation of 1.
        Default is True.

    Returns
    -------
    pd.DataFrame
        The cleaned and formatted dataset.

    Example
    -------
    >>> data = pd.DataFrame({
    >>>     'A': [1, 2, np.nan, 4, 5],
    >>>     'B': ['x', 'y', 'z', 'x', 'y'],
    >>>     'C': [1, 2, 3, 4, 5]
    >>> })
    >>> clean_data = audit_data(data)

    """
    data = to_numeric_dtypes(data )
    dropna_threshold= assert_ratio(dropna_threshold)
    
    # Drop columns with too many missing values
    data = data.dropna(thresh=int(
        dropna_threshold * len(data)), axis=1)

    # Fill missing values
    for col in data.columns:
        if data[col].dtype == 'object':
            # For categorical columns, fill with the mode
            data[col] = data[col].fillna(data[col].mode()[0])
        else:
            # For numerical columns, fill with the median
            data[col] = data[col].fillna(data[col].median())

    # Convert columns to categorical if they have fewer
    # unique values than the threshold
    for col in data.columns:
        if data[col].dtype == 'object' or data[col].nunique(
                ) <= categorical_threshold:
            data[col] = data[col].astype('category')

    # Standardize numerical columns
    if standardize:
        num_cols = data.select_dtypes(include=['number']).columns
        data[num_cols] = (
            data[num_cols] - data[num_cols].mean()) / data[num_cols].std()

    return data
    
def speed_rowwise_process(
    data, /, 
    func, 
    n_jobs=-1
    ):
    """
    Processes a large dataset by applying a complex function to each row. 
    
    Function utilizes parallel processing to optimize for speed.

    Parameters
    ----------
    data : pd.DataFrame
        The large dataset to be processed. Assumes the 
        dataset is a Pandas DataFrame.

    func : function
        A complex function to apply to each row of the dataset. 
        This function should take a row of the DataFrame as 
        input and return a processed row.

    n_jobs : int, optional
        The number of jobs to run in parallel. -1 means using 
        all processors. Default is -1.

    Returns
    -------
    pd.DataFrame
        The processed dataset.

    Example
    -------
    >>> def complex_calculation(row):
    >>>     # Example of a complex row-wise calculation
    >>>     return row * 2  # This is a simple placeholder for demonstration.
    >>>
    >>> large_data = pd.DataFrame(np.random.rand(10000, 10))
    >>> processed_data = speed_rowwise_process(large_data, complex_calculation)

    """
    # Function to apply `func` to each row in parallel
    def process_row(row):
        return func(row)

    # Using Joblib's Parallel and delayed to apply the function in parallel
    results = Parallel(n_jobs=n_jobs)(delayed(process_row)(row) 
                                      for row in data.itertuples(index=False))

    # Converting results back to DataFrame
    processed_data = pd.DataFrame(results, columns=data.columns)

    return processed_data
    
    
    
    
    
    
    
    
    