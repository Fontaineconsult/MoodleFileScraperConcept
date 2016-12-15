
#Welcome. This is a basic web scraper used at SF State to automate downloading of files uploaded to Moodle (iLearn). It is still an early version. This will only work with Moodle based LMS
#However, it is highly customized for our workflow, so in this current state it probably is useless to anyone else. However, as a proof of concept, hopefully it will help you somehow.

# THIS IS JUST A PROOF OF CONCEPT. THIS SCRIPT WAS DESIGNED SPECIFICALLY FOR THE SF STATE ECOSYSTM. PLEASE DON'T TRY TO RUN.

import requests #used to make HTTP requests
from bs4 import BeautifulSoup #a webscaper 
import re #regular expressions used for parsing download link strings
import os #for accessing the operating system file structure



#Ilearn_Session = raw_input("iLearn Page: ")
#Working_dir = raw_input("Save Files Where?: ")

url = #This is the login page for your LMS
USERNAME = # Put username here
PASSWORD = # Put password here

# The script relies on 2 static text files and an additional text file for every course you search. 
# The proceedure is as follows: The script launches and looks for a .txt file containing a URL to each individual course webpage. An HTTP GET request is made for that page and all content is
# loaded into memory. The BS4 webscraper then isolates download links and places them into the 'files_to_download' list. Each download link is checked against a .txt file containing previous
# downloads so the scraper won't download duplicate files.

files_to_download = []
indirect_links = []
updated_courses = []

# YAYDAYADYADYADYAD 

def Open_iLearn_Session(url,USERNAME,PASSWORD, Cur_Session):

    with requests.Session() as c:
        c.get(url)
        login_data = dict(username=USERNAME, password=PASSWORD)
        c.post(url, data=login_data, headers={"Referer": "https://ay1617.ilearn.support.at.sfsu.edu"})
        full_page = c.get(Cur_Session)
        Clean_Page = BeautifulSoup(full_page.content, "html.parser")
        page_title_find = Clean_Page.find("title")
        Page_Title = str(page_title_find)[15:-8]
        Resources = filter_links(Clean_Page,"Init_List")
        id_content_type(Resources, c)
        get_ind_dl_links(indirect_links, c)
        download_all(files_to_download, c, Page_Title)
def filter_links(linklist,State):
    regex = re.compile("https:.{55}=[0-9]{6}|https:.{60}=[0-9]{6}|https:.{60}=[0-9]{5}|https:.{60}=[0-9]{4}")

    if State == "Full":

       return linklist
    elif State == "Full_List":
        for link in linklist.find_all('a', href=True):
              print link['href']
    elif State == "Init_List":
        Link_List = [link['href'] for link in linklist.find_all('a', href=True)]
        Final = [m.group(0) for l in Link_List for m in [regex.search(l)] if m]

        return Final
def id_content_type(Resources, session_obj):
    for link in Resources:
        pagecode = session_obj.get(link)
        header = pagecode.headers
        if header['Content-Type'] == 'application/pdf':
            files_to_download.append(link)
        elif header['Content-Type'] == 'text/html; charset=utf-8':
            indirect_links.append(link)
        elif header['Content-Type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            files_to_download.append(link)
def get_ind_dl_links(links, session_obj):
    regex1 = re.compile(".*.pdf|.*.docx|.*.ppt")
    for link in links:
        Page = session_obj.get(link)
        Clean_Page = BeautifulSoup(Page.content, "html.parser")
        Link_List = [link['href'] for link in Clean_Page.find_all('a', href=True)]

        Final_Link = [m.group(0) for l in Link_List for m in [regex1.search(l)] if m]
        if Final_Link != []:

            files_to_download.append(Final_Link[0])
def download_all(link_list, session_obj, Page_Title):
    count = 0

    coursename = Page_Title[0:12].translate(None,' -')
    char_count = 0
    for character in coursename:
        if character.isalpha():
            char_count += 1
        else:
            break
    if char_count == 3:
        coursename = coursename[:3] + " " + coursename[3:]

    path = r'Z:\Edit Files\semesters\%s\%s\iLearn Files' % (cur_semester, coursename)
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

    for file_link in link_list:

        if os.path.isfile("course_content.txt") == True:

            course_file_r = open('course_content.txt', 'r')
        else:
            course_file_r = open('course_content.txt', 'a+')

        course_content = course_file_r.read().decode('utf8')

        dl_file = session_obj.get(file_link)
        file_header = dl_file.headers

        if 'Content-Disposition' in file_header:
            global file
            title_type = file_header['Content-Disposition']
            title = title_type[22:-1]
            title = title.translate(None, '?')
            file = title

        else:
            title_gross = file_link

            title = title_gross.rsplit('/', 1)[-1]
            file = title.encode('utf-8').translate(None, '?')

        if file_link in course_content:

            print " %s | File Previously Downloaded" % (file)
            course_file_r.close()
        else:
            course_file_r.close()

            course_file_w = open('course_content.txt', 'a')
            course_file_w.write((file_link + '\n').encode('utf8'))
            course_file_w.close()

            if os.path.isfile(file) == False:
                count += 1
                with open("%s" % file, "wb") as code:
                    code.write(dl_file.content)

    if count > 0:
        updated_courses.append(coursename)

    print "%d files downloaded for course: %s" % (count, Page_Title)
def load_class_list():

    class_list = open("iLearn_list.txt", "r")
    ilearn_pages = class_list.readlines()
    list_length = len(ilearn_pages)
    class_list.close()

    return ilearn_pages
def download_initiator_loop():
    global files_to_download
    global indirect_links
    ilearn_courses = load_class_list()
    print ilearn_courses
    for course in ilearn_courses:
        print course
        course_indv = course
        Open_iLearn_Session(url,USERNAME,PASSWORD,course_indv)
        print "Course Completed"
        files_to_download = []
        indirect_links = []

print "Welcome to the iLearn File Download Automator Version 1! Hit any key when you are ready to begin."
raw_input()

try:
    infotext = open("Z:\Edit Files\semesters\semester_info.txt", "r")
    cur_semester = infotext.readline()
except WindowsError:
    print "Semester Info.TXT file not found"

print "The current semester is %s" % cur_semester
print "continue?"
raw_input()

os.chdir("Z:\Edit Files\semesters\%s" % cur_semester)
download_initiator_loop()
print "All Done"
print ""
print "---------------------------------------"
if len(updated_courses) > 0:
    print "The following courses have been updated:"
    print ""
    for item in updated_courses:
        print item
else:
    print "No courses have been updated :-)"

raw_input()


