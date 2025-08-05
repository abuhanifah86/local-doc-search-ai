# Local Document Search AI - Instructions

Follow these steps to run the Local Document Search AI application:

1. **Navigate to the Project Folder**  
   Make sure you are in the same folder as `app.py`.

2. **Run Anaconda Prompt as Administrator**  
   It is preferable to run as administrator to avoid complications when extra privileges are required.

3. **Install Ollama**  
   Download and install Ollama from [https://ollama.com](https://ollama.com).

4. **Download Required Model**  
   Download a model such as `phi4` or `Gemma3`.  
   Example command:  
   ```
   ollama pull phi4:latest
   ```

5. **Create Conda Virtual Environment**  
   Create a virtual environment for the app (only needed once).  
   Example command:  
   ```
   conda create --name=docs python=3.10
   ```

6. **Activate the Virtual Environment**  
   Example command:  
   ```
   conda activate docs
   ```

7. **Install Python Dependencies**  
   Install all required Python libraries (only needed once).  
   Example command:  
   ```
   pip install -r requirements.txt
   ```

8. **Run the App Using Streamlit**  
   Example command:  
   ```
   streamlit run app.py
   ```

9. **Access the App in Your Browser**  
   The app will open automatically, or you can visit [http://localhost:8501](http://localhost:8501).

10. **Begin Using the App**  
   You can now start using the Local Document Search AI.