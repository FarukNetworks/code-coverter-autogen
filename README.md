## AutoGen Code Converter Setup

### Dependencies
- `autogen`: For creating autonomous agents for code translation.
- `argparse`: For parsing command-line arguments.
- `os`: For operating system dependent functionality.
- `inquirer`: For interactive command-line user prompts.
- `dotenv`: For loading environment variables from a `.env` file.

### Configuration
- **Environment Variables**: Ensure that the `OPENAI_API_KEY` is set in the `.env` file for API access.
- **Output Directory**: The output directory for translated code is set to `output-app` by default, and will be created if it does not exist.

### Language Support
- Supported programming languages for translation include:
  - Python
  - JavaScript
  - Java
  - C#
  - C++
  - Ruby
  - Go
  - Visual Basic
  - PHP
  - Swift

### Translation Process
1. **Language Selection**: Users will be prompted to select the source and target programming languages.
2. **Translation Task**: The translation task will maintain the following guidelines:
   - Exact functionality of the original code must be preserved.
   - Use modern idioms and best practices of the target language.
   - All comments and documentation should be preserved.
   - Proper error handling must be implemented.
   - The original code structure and organization should be maintained.
   - Ensure type safety where applicable.
   - Handle edge cases appropriately.

### Logging and Error Handling
- Implement comprehensive error checking for file operations.
- Provide clear error messages and logging for debugging purposes.

### Code Quality
- Follow clean code principles and consistent naming conventions.
- Implement unit tests for translation functions to validate output code.
- Maintain code style consistency and implement code review mechanisms.

### Project Structure
- Organize code by language pairs and separate core translation logic from utilities.
- Maintain clear configuration files and implement a proper testing structure.

### Version Control
- Maintain version control for translation history to track changes and updates.

