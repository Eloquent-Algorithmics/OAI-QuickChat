# AI Assistant with Text-to-Speech

This project is a CLI AI Assistant that uses OpenAI's API to generate responses and ElevenLabs Text-to-Speech API to convert the responses into audio.

## Features

- Real-time text-to-speech conversion
- Customizable voice selection
- Easy-to-use command-line interface
- Powered by OpenAI and ElevenLabs
- ** Paid ElevenLabs subscription required **

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Eloquent-Algorithmics/OAI-QuickChat.git
```
```
cd OAI-QuickChat
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory using the provided `.env.template` file. Fill in the required API keys and voice ID:

```bash
cp .env.template .env
```

4. Edit the `.env` file and add your OpenAI API key, ElevenLabs API key, and desired ElevenLabs voice ID.

## Usage

1. Run the AI Assistant:

```bash
python main.py
```

2. Enter your question or command when prompted:

```
How can I help you? What is the capital of France?
```

3. The AI Assistant will generate a response and play it as audio.

4. To exit the AI Assistant, press `CTRL+C`.

## Customization

You can customize the voice used by the AI Assistant by changing the `ELEVENLABS_VOICE_ID` in the `.env` file. Available voice IDs are listed in the `.env.template` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to your fork.
4. Create a pull request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Acknowledgements

- [OpenAI](https://www.openai.com/)
- [ElevenLabs](https://www.elevenlabs.ai/)
