# Ryo AI Assistant

A sophisticated voice-activated AI assistant built with Python, featuring wake word detection, speech-to-text, AI-powered responses, and text-to-speech capabilities.

## Features

- 🎤 **Wake Word Detection**: Uses Porcupine for reliable "Hey Ryo" detection
- 🗣️ **Speech Recognition**: Whisper-based speech-to-text processing
- 🤖 **AI Integration**: Multiple AI model support (Google Gemini, Ollama)
- 🔊 **Text-to-Speech**: Edge TTS for natural voice responses
- 🖥️ **GUI Interface**: CustomTkinter-based modern interface
- 📝 **Todo Management**: Built-in task management system
- ⌨️ **Hotkey Controls**: Global hotkeys for mute/unmute functionality
- 🔌 **Plugin System**: Extensible architecture for additional features

## Quick Start

### Prerequisites

- Python 3.8+
- macOS (tested on Mac M1)
- Microphone access
- Internet connection for AI models

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ryo-assistant.git
   cd ryo-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp config/env.example config/.env
   # Edit config/.env with your API keys
   ```

4. **Run the assistant**
   ```bash
   python core/main.py
   ```

## Usage

### Voice Commands

- **Wake Word**: Say "Hey Ryo" to activate
- **Natural Conversation**: Ask questions, request help, or chat naturally
- **Todo Commands**: 
  - "Add todo: [task description]"
  - "List todos"
  - "Complete todo [number]"
  - "Delete todo [number]"
- **Stop/Cancel**: Say "stop", "cancel", or "nevermind"

### Keyboard Shortcuts

- **Ctrl+Shift**: Toggle mute/unmute
- **Esc**: Exit the application

## Project Structure

```
ryo-assistant/
├── ai/                 # AI model integrations
├── assets/             # Audio files and resources
├── config/             # Configuration files
├── core/               # Main application logic
├── data/               # Data storage (todos, etc.)
├── gui/                # User interface components
├── plugins/            # Plugin system
├── voice/              # Voice processing modules
└── src/                # Additional source files
```

## Configuration

### AI Models

The assistant supports multiple AI models:

- **Google Gemini**: Default AI model (requires API key)
- **Ollama**: Local AI models (requires Ollama installation)

Configure models in `config/.env`:
```env
GOOGLE_API_KEY=your_google_api_key
OLLAMA_BASE_URL=http://localhost:11434
```

### Voice Settings

- **Wake Word**: "Hey Ryo" (customizable)
- **Speech Recognition**: Whisper model
- **Text-to-Speech**: Edge TTS voices

## Development

### Running Tests

```bash
# Test voice commands
python test_voice_commands.py

# Test todo functionality
python test_todo.py

# Test GUI components
python test_todo_gui.py
```

### Adding Plugins

1. Create a new file in `plugins/`
2. Implement the plugin interface
3. Register the plugin in the main application

## Troubleshooting

### Common Issues

1. **Audio Device Busy**: Ensure no other applications are using the microphone
2. **Wake Word Not Detecting**: Check microphone permissions and audio levels
3. **AI Model Errors**: Verify API keys and internet connection

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export RYO_DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Porcupine](https://github.com/Picovoice/porcupine) for wake word detection
- [Whisper](https://github.com/openai/whisper) for speech recognition
- [Edge TTS](https://github.com/rany2/edge-tts) for text-to-speech
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [Ollama](https://ollama.ai/) for local AI models 