import streamlit
import streamlit.web.cli as stcli
import os, sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    sys.argv = [
        "streamlit",
        "run",
        "./src/app.py",
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())