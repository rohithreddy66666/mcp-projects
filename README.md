# 🌦️ Intro Weather & Google Search Assistant using MCP

A multi-functional AI assistant built with **Chainlit**, leveraging **OpenAI's GPT models**, **WeatherAPI**, and **Google Search API via RapidAPI**. This assistant follows the **Model Context Protocol (MCP)** approach for structured and explainable AI interactions.

---

## 🚀 Features

- ✅ Real-time **current weather** and **3-day forecast** using [WeatherAPI](https://www.weatherapi.com/)
- 🔍 Web **search queries** using [Google Search API](https://rapidapi.com/)
- 🧠 Built on **Model Context Protocol (MCP)** principles by Anthropic
- 🔐 Secure configuration using environment variables (`.env`)
- 📊 Reasoning process and tool decisions displayed in **debug mode**
- 🧩 Modular & extensible Chainlit application

---

## 📁 Project Structure

intro-weather-and-google-api-with-mcp/ ├── app.py # Main Chainlit application ├── requirements.txt # Python dependencies └── README.md # You're reading it!

yaml
Copy
Edit

---

## 🔧 Setup Instructions

### 1️⃣ Clone the repo (if not done yet)
```bash
git clone <your-repo-url>
cd mcp-projects
2️⃣ Create the project folder & move files (if needed)

mkdir intro-weather-and-google-api-with-mcp
mv app.py requirements.txt intro-weather-and-google-api-with-mcp/
cd intro-weather-and-google-api-with-mcp
3️⃣ Install dependencies

pip install -r requirements.txt
4️⃣ Create a .env file
Add your API keys inside .env:
OPENAI_API_KEY=your_openai_key
WEATHER_API_KEY=your_weatherapi_key
RAPID_API_KEY=your_rapidapi_key
Never commit your .env file – it's already ignored via .gitignore.

▶️ Run the App

chainlit run app.py
Then, open the URL provided (typically http://localhost:8000) in your browser.

💡 Example Prompts
What's the weather in New York?

Forecast in Tokyo for the next few days

Search for Rohith Reddy Vangala

Tell me about AMD MI300 and check the weather in Paris

🧠 What is MCP (Model Context Protocol)?
This assistant is structured around Anthropic's Model Context Protocol (MCP) – a systematic approach to multi-function LLM agents. It includes:

Intent detection (weather vs. search)

Tool execution planning

Reasoning trace (debug mode)

Structured context construction

Memory persistence per session

Each message is evaluated and contextualized before being sent to the model, ensuring consistent and transparent decision-making.

📦 Requirements (from requirements.txt)
chainlit
requests
python-dotenv
openai
Add any other dependencies you need here.

📚 References
Chainlit Documentation: https://docs.chainlit.io/

WeatherAPI: https://www.weatherapi.com/

Google Search API on RapidAPI: https://rapidapi.com/

OpenAI API: https://platform.openai.com/

Model Context Protocol by Anthropic: https://www.anthropic.com/index/model-context-protocol

👨‍💻 Author
Rohith Reddy Vangala
Passionate about NLP, GenAI, and multi-modal assistants
Feel free to connect on LinkedIn

📜 License
MIT License – feel free to use, modify, and distribute.

Designed with ❤️ using Chainlit + OpenAI + MCP Protocol.

---
