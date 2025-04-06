# app.py
import os
import json
import requests
import chainlit as cl
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# API configurations
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"
FORECAST_API_URL = "https://api.weatherapi.com/v1/forecast.json"
RAPID_API_KEY = os.environ.get("RAPID_API_KEY", "93f68119d1msh10c8c9f2e1dac20p1b1474jsne199faed7ae9")
GOOGLE_SEARCH_URL = "https://google-search74.p.rapidapi.com/"

# Debug mode for showing reasoning process
DEBUG_MODE = True

async def extract_query_info(message):
    """Analyze the user message to determine what they're asking for"""
    # Check if this is a weather-related query
    weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy", "humidity", "wind", "climate"]
    is_weather_query = any(keyword in message.lower() for keyword in weather_keywords)
    
    # Check if user wants forecast instead of current weather
    forecast_keywords = ["forecast", "tomorrow", "next week", "upcoming", "predict", "will it", "expected"]
    is_forecast_request = any(keyword in message.lower() for keyword in forecast_keywords)
    
    # Check if user wants to search for something
    search_keywords = ["search", "google", "find", "lookup", "who is", "what is", "tell me about"]
    is_search_request = any(keyword in message.lower() for keyword in search_keywords)
    
    # Extract location for weather queries
    location = None
    if is_weather_query:
        location_keywords = ["in", "for", "at", "near"]
        for keyword in location_keywords:
            if f" {keyword} " in message:
                parts = message.split(f" {keyword} ")
                if len(parts) > 1:
                    location = parts[1].split("?")[0].split(".")[0].strip()
                    break
        
        # Default location if none is detected
        if not location:
            location = "London"
    
    # Extract search query if this is a search request
    search_query = None
    if is_search_request:
        # Try to extract what to search for after keywords
        for keyword in search_keywords:
            if keyword in message.lower():
                start_idx = message.lower().find(keyword) + len(keyword)
                search_query = message[start_idx:].strip()
                if search_query.startswith((":", "about", "for")):
                    search_query = search_query[search_query.find(" ")+1:]
                break
        
        # If we couldn't extract, use the whole message
        if not search_query:
            search_query = message
    
    return {
        "is_weather_query": is_weather_query,
        "is_forecast": is_forecast_request,
        "is_search_request": is_search_request,
        "location": location,
        "search_query": search_query
    }

async def google_search(query):
    """Perform a Google search via RapidAPI"""
    try:
        headers = {
            "x-rapidapi-key": RAPID_API_KEY,
            "x-rapidapi-host": "google-search74.p.rapidapi.com"
        }
        
        params = {
            "query": query,
            "limit": "5",
            "related_keywords": "true"
        }
        
        response = requests.get(GOOGLE_SEARCH_URL, headers=headers, params=params)
        
        if response.status_code != 200:
            return {
                "error": f"Google Search API returned status code {response.status_code}",
                "original_query": query
            }
            
        return response.json()
    except Exception as e:
        return {
            "error": f"Failed to perform search: {str(e)}",
            "original_query": query
        }

async def get_weather_data(location):
    """Fetch current weather data for a location"""
    try:
        response = requests.get(WEATHER_API_URL, params={
            "key": WEATHER_API_KEY,
            "q": location
        })
        
        if response.status_code != 200:
            return {"error": f"Weather API returned status code {response.status_code}"}
            
        data = response.json()
        return data
    except Exception as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}

async def get_forecast_data(location, days=3):
    """Fetch weather forecast data for a location"""
    try:
        response = requests.get(FORECAST_API_URL, params={
            "key": WEATHER_API_KEY,
            "q": location,
            "days": days
        })
        
        if response.status_code != 200:
            return {"error": f"Forecast API returned status code {response.status_code}"}
            
        data = response.json()
        return data
    except Exception as e:
        return {"error": f"Failed to fetch forecast data: {str(e)}"}

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="""👋 Welcome to the Multi-Function Assistant!

I can help with two main functions:
1. Weather information - Ask me about current conditions or forecasts
2. Web searches - Just include words like "search" or "google" in your query

Examples:
- "What's the weather in Tokyo?"
- "Search for Rohith Reddy Vangala"
- "Tell me about the forecast in Paris and lookup tourist attractions there"
"""
    ).send()
    
    # Set initial chat state with system message
    system_message = {
        "role": "system",
        "content": """You are a helpful multi-function assistant that can provide both weather information 
        and search results. When the user asks about weather, provide accurate information based on the 
        weather data included in the context. When they ask for a search, provide information based on 
        the search results. If they ask for both, combine the information appropriately.
        
        Only use the data provided to answer questions, not your training data. 
        Be concise, friendly and informative."""
    }
    
    cl.user_session.set("messages", [system_message])

@cl.on_message
async def main(message: cl.Message):
    """Process user messages and generate responses using MCP"""
    user_message = message.content
    
    # Start building the reasoning process log
    reasoning_log = [
        "# Model Context Protocol: Multi-Function Assistant",
        "",
        "## Input Analysis",
        f"- User query: \"{user_message}\"",
    ]
    
    # Extract query information
    query_info = await extract_query_info(user_message)
    is_weather_query = query_info["is_weather_query"]
    is_forecast = query_info["is_forecast"]
    is_search_request = query_info["is_search_request"]
    location = query_info["location"]
    search_query = query_info["search_query"]
    
    if is_weather_query:
        reasoning_log.append(f"- Weather query detected")
        reasoning_log.append(f"- Location extracted: \"{location}\"")
        reasoning_log.append(f"- Forecast requested: {is_forecast}")
    
    if is_search_request:
        reasoning_log.append(f"- Search request detected")
        reasoning_log.append(f"- Search query: \"{search_query}\"")
    
    # Tool execution plan
    reasoning_log.append("")
    reasoning_log.append("## Tool Execution Plan")
    
    # Plan which tools to use based on the query
    tool_plan = []
    
    if is_weather_query:
        if is_forecast:
            tool_plan.append("Weather Forecast API - Get multi-day forecast")
        else:
            tool_plan.append("Current Weather API - Get current conditions")
    
    if is_search_request:
        tool_plan.append("Google Search API - Get information based on search query")
    
    # If no tools were selected, default to search
    if not tool_plan:
        tool_plan.append("Google Search API - No specific intent detected, using search as fallback")
        is_search_request = True
        search_query = user_message
    
    # Add the plan to the log
    for i, step in enumerate(tool_plan):
        reasoning_log.append(f"{i+1}. {step}")
    
    # Execute the tool plan
    reasoning_log.append("")
    reasoning_log.append("## Tool Execution")
    
    # Initialize results placeholders
    weather_data = None
    search_results = None
    
    # Get weather data if requested
    if is_weather_query:
        if is_forecast:
            reasoning_log.append("### Tool: Weather Forecast API")
            reasoning_log.append(f"- Input: \"{location}\"")
            weather_data = await get_forecast_data(location)
        else:
            reasoning_log.append("### Tool: Current Weather API")
            reasoning_log.append(f"- Input: \"{location}\"")
            weather_data = await get_weather_data(location)
        
        if "error" in weather_data:
            reasoning_log.append(f"- Error: {weather_data['error']}")
            await cl.Message(content=f"I encountered a problem getting weather data: {weather_data['error']}").send()
        else:
            if is_forecast:
                reasoning_log.append(f"- Forecast data received for: {weather_data['location']['name']}, {weather_data['location']['country']}")
                reasoning_log.append(f"- Forecast days: {len(weather_data['forecast']['forecastday'])}")
                
                # Display forecast data
                forecast_display = f"📊 Weather Forecast for {weather_data['location']['name']}, {weather_data['location']['country']}:\n\n"
                
                for day in weather_data['forecast']['forecastday']:
                    date = day['date']
                    condition = day['day']['condition']['text']
                    max_temp = day['day']['maxtemp_c']
                    min_temp = day['day']['mintemp_c']
                    
                    forecast_display += f"📅 **{date}**\n"
                    forecast_display += f"• Condition: {condition}\n"
                    forecast_display += f"• Max temp: {max_temp}°C / {day['day']['maxtemp_f']}°F\n"
                    forecast_display += f"• Min temp: {min_temp}°C / {day['day']['mintemp_f']}°F\n"
                    forecast_display += f"• Chance of rain: {day['day']['daily_chance_of_rain']}%\n\n"
                
                await cl.Message(content=forecast_display).send()
            else:
                reasoning_log.append(f"- Current weather data received for: {weather_data['location']['name']}, {weather_data['location']['country']}")
                reasoning_log.append(f"- Current temperature: {weather_data['current']['temp_c']}°C / {weather_data['current']['temp_f']}°F")
                reasoning_log.append(f"- Weather condition: {weather_data['current']['condition']['text']}")
                
                # Display current weather data
                weather_info = {
                    "location": f"{weather_data['location']['name']}, {weather_data['location']['country']}",
                    "temperature": f"{weather_data['current']['temp_c']}°C / {weather_data['current']['temp_f']}°F",
                    "condition": weather_data['current']['condition']['text'],
                    "humidity": f"{weather_data['current']['humidity']}%",
                    "wind": f"{weather_data['current']['wind_kph']} kph, {weather_data['current']['wind_dir']}"
                }
                
                await cl.Message(
                    content=f"📊 Current weather for {weather_info['location']}:\n"
                            f"• Temperature: {weather_info['temperature']}\n"
                            f"• Condition: {weather_info['condition']}\n"
                            f"• Humidity: {weather_info['humidity']}\n"
                            f"• Wind: {weather_info['wind']}"
                ).send()
    
    # Get search results if requested
    if is_search_request:
        reasoning_log.append("")
        reasoning_log.append("### Tool: Google Search API")
        reasoning_log.append(f"- Input: \"{search_query}\"")
        
        search_results = await google_search(search_query)
        
        if "error" in search_results:
            reasoning_log.append(f"- Error: {search_results['error']}")
            await cl.Message(content=f"I encountered a problem with the search: {search_results['error']}").send()
        else:
            reasoning_log.append(f"- Search results received: {len(search_results.get('results', []))} items")
            
            # Display a preview of search results
            search_display = f"🔍 Search results for \"{search_query}\":\n\n"
            
            for i, result in enumerate(search_results.get('results', [])[:3]):
                title = result.get('title', 'No title')
                snippet = result.get('snippet', 'No description')
                search_display += f"**{i+1}. {title}**\n{snippet}\n\n"
            
            await cl.Message(content=search_display).send()
    
    # Update messages for MCP
    reasoning_log.append("")
    reasoning_log.append("## Model Context Protocol Structure")
    
    messages = cl.user_session.get("messages")
    
    reasoning_log.append(f"- System message: \"{messages[0]['content'][:50]}...\"")
    
    # Build context based on what data we have
    user_context = {
        "original_query": user_message,
    }
    
    if weather_data and "error" not in weather_data:
        user_context["weather_data"] = weather_data
        reasoning_log.append("- Including weather data in context")
    
    if search_results and "error" not in search_results:
        user_context["search_results"] = search_results
        reasoning_log.append("- Including search results in context")
    
    # Add user's question + all context data
    user_message_with_context = f"{user_message}\n\n{json.dumps(user_context, indent=2)}"
    
    messages.append({
        "role": "user",
        "content": user_message_with_context
    })
    
    reasoning_log.append(f"- Total context size: {len(user_message_with_context)} characters")
    
    # Create an OpenAI API request following the MCP structure
    reasoning_log.append("")
    reasoning_log.append("## AI Processing")
    reasoning_log.append(f"- Sending to model: gpt-4-turbo")
    reasoning_log.append(f"- Temperature: 0.7")
    reasoning_log.append(f"- Max tokens: 500")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    # Get and process the response
    response_text = response.choices[0].message.content
    reasoning_log.append(f"- Response received: \"{response_text[:50]}...\"")
    
    # Add the assistant's response to the message history
    messages.append({
        "role": "assistant",
        "content": response_text
    })
    cl.user_session.set("messages", messages)
    
    # Final reasoning summary
    reasoning_log.append("")
    reasoning_log.append("## Process Summary")
    
    summary_points = ["1. Analyzed user query for intent (weather and/or search)"]
    
    if is_weather_query:
        summary_points.append(f"2. Used Weather API to get {'forecast' if is_forecast else 'current'} data")
        next_num = 3
    else:
        next_num = 2
        
    if is_search_request:
        summary_points.append(f"{next_num}. Used Google Search API to get information about \"{search_query}\"")
        next_num += 1
        
    summary_points.append(f"{next_num}. Constructed MCP structure with original query + all tool outputs")
    summary_points.append(f"{next_num+1}. Generated natural language response using LLM")
    summary_points.append(f"{next_num+2}. Updated conversation context for future queries")
    
    for point in summary_points:
        reasoning_log.append(point)
    
    # Display reasoning process if debug mode is on
    if DEBUG_MODE:
        await cl.Message(content="\n".join(reasoning_log)).send()
    
    # Send the final response to the user
    if is_weather_query and is_search_request:
        icon = "🌐🌤️"
    elif is_weather_query:
        icon = "🌤️"
    else:
        icon = "🔍"
        
    await cl.Message(content=f"{icon} {response_text}").send()

# Run the Chainlit app
if __name__ == "__main__":
    print("Multi-Function Assistant - run with: chainlit run app.py")