import os
import sys
import argparse
from urllib.request import (HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener)
from urllib.error import URLError
import lxml.etree as ET


def main():
    parser = argparse.ArgumentParser(description="Fetch and transform a Dynatrace dashboard report.")
    parser.add_argument("--dtserver", default="changeme:8020", help="Dynatrace Server IP and REST port (e.g., 127.0.0.1:8020)")
    parser.add_argument("--dashboard", default="changeme", help="URL encoded Dashboard name")
    parser.add_argument("--timeframe", default="Last5Min", help="Timeframe for the report (e.g., Last5Min)")
    args = parser.parse_args()

    try:
        username = os.environ['DTUSER']
        password = os.environ['DTPASS']
    except KeyError:
        print("Error: DTUSER and DTPASS environment variables must be set.", file=sys.stderr)
        sys.exit(1)

    xsl_filename = "report.xsl"
    feed_url = f"http://{args.dtserver}/rest/management/reports/create/{args.dashboard}?type=XML&format=XML+Export&filter=tf:{args.timeframe}"

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    try:
        password_mgr = HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, feed_url, username, password)
        opener = build_opener(HTTPBasicAuthHandler(password_mgr))
        install_opener(opener)
        with opener.open(feed_url) as f:
            dom = ET.parse(f)

    except URLError as e:
        print(f'URLError: "{e}"', file=sys.stderr)
        raise
    except ET.LxmlError as e:
        print(f'XML Parsing Error: "{e}"', file=sys.stderr)
        raise

    appdir = os.path.dirname(os.path.dirname(__file__))
    xsl_file = os.path.join(appdir, "bin", xsl_filename)

    try:
        xslt = ET.parse(xsl_file)
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
        print(str(newdom))
    except ET.LxmlError as e:
        print(f'XSLT Parsing Error: "{e}"', file=sys.stderr)
        raise


if __name__ == "__main__":
    main()




