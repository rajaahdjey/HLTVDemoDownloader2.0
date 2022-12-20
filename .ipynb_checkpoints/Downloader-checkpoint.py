#comment out whichever library is already installed! 

!pip install patool
!pip3 install rarfile
!sudo apt install unrar


from multiprocessing.dummy import Pool as ThreadPool
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
import re
import os
import time
import patoolib
from tqdm.notebook import tqdm
from requests import get  # to make GET request
import os
import rarfile
import pandas as pd


def get_match_ids(teamid):
    # Create an offset variable for lists that are paginated on HLTV
    offset = 0
    # Build the URL

    # Create an array of all of the Demo URLs on the page
    match_ids = find_match_ids_at_url("https://www.hltv.org/results?startDate=2022-01-01&endDate=2022-03-31&stars=2&offset=%s&map=%s&matchType=Lan" % (offset, map_name))
    # If the length is = 50, offset by 50 and loop again
    if len(match_ids) == 50:
        print("Parsed first page. Found %s IDs" % (len(match_ids)))

        # Set a boolean to close the while loop and a page variable we can increment when paginating
        more_pages = True
        page = 1

        # While check is true, offset by 50
        while more_pages:
            offset += 50

            # Same URL building and parsing as above
            more_match_ids = find_match_ids_at_url("https://www.hltv.org/results?startDate=2022-01-01&endDate=2022-03-31&stars=2&offset=%s&map=%s&matchType=Lan" % (offset, map_name))
            for match in more_match_ids:
                match_ids.append(match)

            # Determine if there are additional pages to be found, if not the while loop ends
            if len(more_match_ids) < 50:
                more_pages = False
                page += 1
                print("Parsed page %s. Found %s IDs." % (page, len(match_ids)))
            else:
                # Prints the current page and the number of parsed IDs
                page += 1
                print("Parsed page %s. %s IDs found so far." % (page, len(match_ids)))

    elif len(match_ids) < 50:
        print("Total demos: %s" % len(match_ids))
    elif len(match_ids) > 50:
        print("HLTV altered demo page layout :(")
    return match_ids


def find_match_ids_at_url(url):
    # Get the HTML using get_html()
    html = get_html(url).decode('utf-8')

    # Create an array of all of the Demo URLs on the page
    match_ids = re.findall(r'<a href=\"/matches/(.*?)\"(?: class="a-reset">)', html)

    return match_ids


def convert_to_demo_ids(match_ids, threads):
    # Tell the user what is happening
    print("Converting Match IDs to Demo IDs")

    # Define the number of threads
    pool = ThreadPool(threads)

    # Calls get_demo_ids() and adds the value returned each call to an array called demo_ids
    demo_ids = pool.map(get_demo_ids, match_ids)
    pool.close()
    pool.join()

    # Create an array to add any captured errors to
    errors = []

    # Find any errors, add them to the errors array, and remove them from demo_ids
    for demo_id in demo_ids:
        if "/" in demo_id:
            errors.append(demo_id)
    demo_ids = [x for x in demo_ids if x not in errors]

    # Print the errors (if there are any)
    print_errors(errors)
    return demo_ids


def get_demo_ids(match_id):
    # URL building and opening
    url = "https://www.hltv.org/matches/%s" % (match_id)
    html = get_html(url).decode('utf-8')
    demo_id = re.findall(r'"/download/demo/(.*?)"', html)

    # Check if re.findall()'s array is empty
    # If it has an element, add that Demo ID to the demo_ids array
    if len(demo_id) > 0:
        # Loop through the demo_ids array and remove everything up to the last / to get the real Demo ID
        for i in range(0, len(demo_id)):
            print("Converted %s" % (match_id))
            # Return the Demo ID
            return demo_id[0]

    # If there is no element, print which match has no demo
    elif len(demo_id) < 1:
        print("No demo found for %s" % (match_id))
        # Return the Match ID with a space char so we can find it later
        return " %s" % match_id

def extract_rar(dirname,filename):
    try:
        os.mkdir("extracted_demos/")
    except:
       print("Folder Already Present or other error") 
    rar = rarfile.RarFile(f"{dirname}/{filename}.rar")
    rar.extractall(filename.split('.')[0])

def downloader(demo_ids, threads=1):
    # Temporarily use 1 due to 503 errors
    # Convert the DemoIDs to URLs
    urls = convert_to_urls(demo_ids)

    # Make a folder for the event to save the files in
    directory = make_dir()

    # Download_the_rar_files
    for url in tqdm(urls):
        filename = url.rsplit('/', 1)[-1]
        print("Downloading from URL: ",url)
        print("FileName: ",filename)
        try:
            download(url,f"{directory}/{filename}.rar")
        except:
            print("There is an error in the download")
        extract_rar(directory,filename)
        os.remove(f"{directory}/{filename}.rar") #once rar is extracted, remove the rar file.
        demo_name = ""
        for dirname, _, filenames in os.walk('/kaggle/working/'+filename.split('.')[0]):
            for demo_file in filenames:
                if ".dem" in demo_file:
                    demo_name = os.path.join(dirname, demo_file)
                    print("Demo Name Location:",demo_name)
                    init_json_name = (demo_name.split("/")[-1].split(".")[0])+".json"
                    rename_to_do = demo_name.split("/")[-2]+"_"+(demo_name.split("/")[-1].split(".")[0])+".json"    
                demo_parser = DemoParser(demofile = demo_name,
                                        parse_rate=64, 
                                        trade_time=5, 
                                        buy_style="hltv"
                                        )
                data = demo_parser.parse()
                try:
                    os.rename(init_json_name,rename_to_do)
                except:
                    print("Error to rename")
                os.remove(demo_name)
        #os.rmdir(dirname)
        
        #break

    print("Transferred demos")
    return True

def download(url, file_name):
    # open in binary mode
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    with open(file_name, "wb") as file:
        # get request
        response = get(url,headers=headers)
        # write to file
        file.write(response.content)

def convert_to_urls(demo_ids):
    return ["https://www.hltv.org/download/demo/%s" % demo_id for demo_id in demo_ids]


def make_dir():
    # Ask the user what the event name is
    event_name = "ESL_Pro_League_Sea16"

    # Create a global variable so the different threads can access it
    global directory
    directory = "./%s" % (event_name)
    os.makedirs(directory,exist_ok=True)

    # Return the string so we can use it
    return directory

def get_html(url):
    # Open the URL
    opener = urllib.request.build_opener()

    # Spoof the user agent
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7')]
    
    try:
      time.sleep(5)
      response = opener.open(url)
    except:
      time.sleep(20)
      response = opener.open(url)

    # Read the response as HTML
    html = response.read()
    return html


def print_errors(errors):
    # Print URL(s) for the match(es) with no demo file(s)
    if len(errors) == 1:
        print("%s match has no demo:" % (len(errors)))
        for i in range(0, len(errors)):
            print("%s: https://www.hltv.org/matches/%s" % (i+1, errors[i]))
    elif len(errors) > 0:
        print("%s matches have no demo:" % (len(errors)))
        for i in range(0, len(errors)):
            print("%s: https://www.hltv.org/matches/%s" % (i+1, errors[i]))
    else:
        print("No errors found!")
    return True

def extract_demos(directory,demo_ids):
    for demo_name in demo_ids:
        patoolib.extract_archive(f"{directory}/{demo_name}.rar", outdir=os.mkdir(f"{directory}/{demo_name}"))


# Calls the method for a given Event ID.
map_name = "de_mirage"
processes = 8
match_ids = get_match_ids(map_name)
demo_ids = convert_to_demo_ids(match_ids, processes)
downloader(demo_ids)