import requests

def export_config (jenkins_url, output_filename):
    """Exports a Jenkins configuration file to disk
    
    Parameters
    ----------
    jenkins_url : string
        Source URL to the configuration file on a Jenkins server
        Typically ends with '/config.xml' (e.g.: http://jenkins/job/job1/config.xml')
    output_filename : string
        Path and file name to store the exported configuration
    """
    r = requests.get(jenkins_url)
    assert(r.status_code == 200)
    
    f = open(output_filename, 'w')
    f.write(r.text)
    f.close()
    
    print ("Export completed successfully")
    
if __name__ == '__main__':
    r = requests.get("http://localhost:8080/job/test_job_1/config.xml")
    assert(r.status_code == 200)
    as_text = r.text
    as_byte = r.content
    
    print (type(as_text))
    print (type(as_byte))
    
    print (as_text)
    print (as_byte)
    print (as_text.encoding)
    pass
    
    