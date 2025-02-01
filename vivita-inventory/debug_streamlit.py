import os
import sys
import streamlit as st

def main():
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)
    print("Current working directory:", os.getcwd())
    print("PYTHONPATH:", os.environ.get('PYTHONPATH', 'Not set'))
    print("Streamlit version:", st.__version__)
    
    try:
        st.title("Debug App")
        st.write("If you can see this, Streamlit is working!")
    except Exception as e:
        print("Error running Streamlit:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
