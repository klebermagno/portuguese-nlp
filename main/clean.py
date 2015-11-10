# Author Cagil
# Edit 28 Apr 2015
# Edit Log 21 Oct 2015
# Unescape added, it is optional
import argparse,os,sys,io
from BeautifulSoup import BeautifulSoup,Comment
UNESCAPE = True
import HTMLParser
h = HTMLParser.HTMLParser()
def main():
    parser = argparse.ArgumentParser(description = "Parses & removes unnecessary html tags from raw classifier files")
    parser.add_argument("--raw_dir", required = False, default=None ,type=str , help = "Raw data dir")
    parser.add_argument("--parsed_dir", required = False, default=None ,type=str , help = "Parsed data dir")
    #parser.add_argument("--clean", required = False, default=False ,type=bool , help = "Output Dir")
    parser.add_argument("--divide", required = False, default=True,action='store_false', dest='boolean_switch', help = "Parsed data dir")
    parser.add_argument("--debug", required = False, default=False,action='store_true', dest='debug', help = "Parsed data dir")
    args = parser.parse_args()
    #print(args.class1)
    if args.raw_dir and args.parsed_dir:
        get_pages(args.raw_dir,args.parsed_dir,args.boolean_switch,debug=args.debug)
    else:
        sys.stderr.write("Error")

def get_pages(raw_dir,parsed_dir,divide,debug=False):
    classes = gen_walk(raw_dir)
    for label,sub_path in classes.items():
        i = 0 ; path = ""
        create_dirs(parsed_dir,label,divide)
        for raw_filename in gen_walk_inner(sub_path):
            if divide:
                path = "test"  if i < 1 else "training"
                i = (i + 1) % 4 #2
            infilename = os.path.join(raw_dir,label,raw_filename)
            outfilename = os.path.join(parsed_dir,path,label,raw_filename)
            write_parsed_page(infilename,outfilename,debug=debug)
        sys.stdout.write("Last file for [%s] written to file: %s\n" %(label,outfilename))
        sys.stdout.write("Completed [Writing to File: %s]\n" %label)

def write_parsed_page(infilename,outfilename,debug=False):
    with io.open(infilename, 'r',encoding="latin1") as infile:
        page = BeautifulSoup(infile)
    try:
        title_text = page.html.head.title.string.split()
        title = " ".join(title_text)
        title = title.strip(u"Folha de S.Paulo").strip().strip("-").strip()
    except AttributeError:
        sys.stderr.write("Title AttributeError at %s\n" %outfilename)
        title = ""
    except TypeError:
        sys.stderr.write("Title TypeError at %s\n" %outfilename)
        title = u""
        print(page.html.head.title)
    clean_page(page)
    if debug:
        sys.stdout.write("[CLEAN PAGE] %s\n" %page)
    content = parse_html(page)
    if content is None:
        sys.stderr.write("No td, No div at %s\n" %outfilename)
        return
    if debug:
        sys.stdout.write("[CONTENT] %s\n" %content)
    clean_more(content)
    #unicode_content = content.renderContents().decode('utf-8').strip("|\n ?")
    unicode_content = content.text.strip("|\n ?")
    nl_free_content = unicode_content.replace(u"\n",u" ")
    with io.open(outfilename, 'w') as outfile:
        if UNESCAPE:
            title = h.unescape(title)
            nl_free_content = h.unescape(nl_free_content)
        outfile.write("%s\n" %title)
        outfile.write(nl_free_content)
    if debug:
        sys.stdout.write("[CLEANED CONTENT] %s\n" %content)
        sys.stdout.write("[UNICODE CONTENT] %s\n" %unicode_content)
        sys.stdout.write("[INFILENAME]%s\n" %infilename)
        sys.stdout.write("[OUTFILENAME]%s\n" %outfilename)
        sys.stdout.write("************************************************************\n")
        sys.stdout.write("************************************************************\n")

def parse_html(page):
    try:
        table = page.find("table", {"id": "main"})
        if table is not None:
            page = table
    except:
        print("***************")
    try:
        tds = page.findAll("td")
        content = tds[-2] # throws IndexError if tds empty
        for td_ind in range(1,len(tds)):
            content = tds[-1*td_ind]
            if content.find("b"):
                #print(-1*td_ind)
                break
    except IndexError:
        try:
            content = page.find("div", {"id": "articleNew"})
        except:
            sys.stderr.write("Error line 56")
            return None
    return content

def clean_page(page):
    scripts = page.findAll("script")
    [scr.extract() for scr in scripts]
    comments = page.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

def clean_more(page):
    imgs = page.findAll("img")
    [img.extract() for img in imgs]
    brs = page.findAll("br")
    [br.extract() for br in brs]
    links = page.findAll("a")
    [link.extract() for link in links]
    comments = page.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

def gen_walk(path):
    classes = {}
    for dirname, dirnames, _ in os.walk(path):
        # print path to all subdirectories first.
        for class_name in dirnames:
            sub_path = os.path.join(dirname, class_name)
            classes[class_name] = sub_path
    return classes

def gen_walk_inner(sub_path):
    for _, _, filenames in os.walk(sub_path):
        if '.DS_Store' in filenames:
            # don't go into any .git directories.
            filenames.remove('.DS_Store')

        for filename in filenames:
            yield filename # os.path.join(sub_dirname, filename)


def create_dirs(parsed_dir,label,divide):
    if divide:
        directory = os.path.join(parsed_dir,"test",label)
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.makedirs(os.path.join(parsed_dir,"training",label))
    else:
        directory = os.path.join(parsed_dir,label)
        if not os.path.exists(directory):
            os.makedirs(directory)

if __name__ == "__main__":
    main()