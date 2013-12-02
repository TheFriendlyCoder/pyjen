from os import path

def get_sample_data_file(filename):
    """Given a filename, this method generates the full path to the file in the sample data folder

    This method assumes that sample data is source data that
    typically represents data found in the real world under
    typical use of Jenkins. These files should never be modified
    during unit test execution.
    
    This method does basic validation to ensure the specified
    sample data file does exist. If it does not an appropriate
    unit test exception will be thrown.
    
    Parameters
    ----------
    filename : string
        name of the file to be located
    
    Returns
    -------
    string
        Full path and file name of the sample data to be loaded
    """
    
    working_path = path.dirname(path.realpath(__file__))
    retval =  working_path + "/sample_data/" + filename
    
    assert(path.exists(retval))
    
    return retval

def get_test_data_file(filename):
    """Given a filename, this method generates the full path to the file in the test data folder
    
    Test data is considered miscellaneous unit test data, such
    as those used to validate the output of a process under test.
    
    This method does basic validation to ensure the specified
    test data file does exist. If it does not an appropriate
    unit test exception will be thrown.
    
    Parameters
    ----------
    filename : string
        name of the file to be located
    
    Returns
    -------
    string
        Full path and file name of the test data to be loaded
    """
    
    working_path = path.dirname(path.realpath(__file__))
    retval =  working_path + "/test_data/" + filename
    
    assert(path.exists(retval))
    
    return retval