# AI Assistant with Text-to-Speech

This project is a Text or Voice Input AI Assistant that uses the OpenAI API to generate responses and the ElevenLabs Text-to-Speech API to convert the responses into audio quickly.

## Features

- Real-time speech-to-speech conversation
- Customizable voice selection
- Easy-to-use command-line interface
- Powered by OpenAI and ElevenLabs
- **Paid ElevenLabs subscription required**

# Getting Started

### Prerequisites

- Ensure you have [Miniconda](https://docs.anaconda.com/free/miniconda/#latest-miniconda-installer-links) installed on your system.

- Get your [OpenAI API Key](https://platform.openai.com/api-keys)

- Get your [ElevenLabs API Key](https://elevenlabs.io/app/subscription)

- To run ```main_ws.py``` you will need a [Azure](https://portal.azure.com/) OpenAI Deployment and Speech Service Resource

## Installation

1. Fork and clone the repository:

```bash
git clone https://github.com/<username>/OAI-QuickChat.git

cd OAI-QuickChat
```

- Create a conda environment:

```bash
conda create -n qchat python=3.12 -y
```

- Install the required packages:

```bash
pip install -r requirements.txt
```

- Create a `.env` file in the project root directory using the provided `.env.template` file. Fill in the required API keys and voice ID:

```bash
cp .env.template .env
```

- Edit the `.env` file and add your OpenAI API key, ElevenLabs API key, and desired ElevenLabs voice ID.

## Usage

- Run the AI Assistant:

    ```python main.py --voice``` to talk to the assistant.

    ```python main.py``` to type your requests in the terminal.
<br>
<br>

- To run the AzureOpenAI websockets version of the assistant:

    ```python main_ws.py``` to type your requests in the terminal.

    ```python main_ws.py --voice``` to talk to the assistant.
<br>
<br>

- To exit the AI Assistant, press `CTRL+C`.

## Customization

You can customize the voice used by the AI Assistant by changing the `ELEVENLABS_VOICE_ID` in the `.env` file.

A link to the pre-made voices is in the `.env.template` file.

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
- [ElevenLabs](https://www.elevenlabs.io/)