if __name__ == "__main__":
    import os

    from dotenv import load_dotenv
    from langchain_google_genai import ChatGoogleGenerativeAI

    # Load environment variables
    load_dotenv()

    # Load API key
    api_key = os.getenv("GOOGLE_API_KEY")

    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key
    )

    # Send prompt
    response = llm.invoke("Generate one Java interview question")

    # Print response
    print(response.content)
