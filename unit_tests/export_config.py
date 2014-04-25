import requests

def export_config (url, output_filename):
    """Exports a Jenkins configuration file to disk
    
    Parameters
    ----------
    url : string
        Source URL to the configuration file on a Jenkins server
        Typically ends with '/config.xml' (e.g.: http://jenkins/job/job1/config.xml')
    output_filename : string
        Path and file name to store the exported configuration
    """
    r = requests.get(url)
    assert(r.status_code == 200)
    
    f = open(output_filename, 'w')
    f.write(r.text)
    f.close()
    
    print "Export completed successfully"
    
if __name__ == '__main__':
    export_config('http://localhost:8080/job/job2a/config.xml', '/home/kevin/delme.xml')
    
    