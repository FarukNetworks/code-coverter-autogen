import autogen
import argparse
import os
import inquirer
import dotenv

dotenv.load_dotenv()

# Function to prompt user for input and output languages
def choose_languages():
    languages = [
        'Python',
        'JavaScript',
        'Java',
        'C#',
        'C++',
        'Ruby',
        'Go',
        'Visual Basic',
        'PHP',
        'Swift'
    ]
    
    questions = [
        inquirer.List('input_lang',
                      message="Select the source programming language",
                      choices=languages,
                      ),
        inquirer.List('output_lang',
                      message="Select the target programming language",
                      choices=languages,
                      ),
    ]
    
    answers = inquirer.prompt(questions)
    return answers['input_lang'], answers['output_lang']

# Get input and output languages from user
input_lang, output_lang = choose_languages()

# Add argument parsing
parser = argparse.ArgumentParser(description='Translate code from one language to another')
parser.add_argument('--input-dir', type=str, default='input-app', help='Input directory containing source code')
parser.add_argument('--output-dir', type=str, default='output-app', help='Output directory for translated code')

args = parser.parse_args()

# Create output directory if it doesn't exist
os.makedirs(args.output_dir, exist_ok=True)

# Replace the config setup
config_list = [
    {
        'model': 'gpt-4o-mini',  # or your preferred model
        'api_key': os.getenv('OPENAI_API_KEY')
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.1
}

# Modified task to handle code translation
def get_translation_task(file_path, source_code, input_lang, output_lang):
    return f"""Translate the following {input_lang} code to {output_lang}. 
    
File: {file_path}

IMPORTANT INSTRUCTIONS:
1. Maintain exact functionality of the original code
2. Use modern {output_lang} idioms and best practices
3. Preserve all comments and documentation
4. Maintain proper error handling
5. Keep the same code structure and organization
6. Ensure proper type safety where applicable
7. Handle edge cases appropriately

SOURCE CODE:
{source_code}

Provide only the translated code without explanations, wrapped in triple backticks with the appropriate language identifier."""

# Modified translator with more specific instructions
translator = autogen.AssistantAgent(
    name="Translator",
    llm_config=llm_config,
    system_message=f"""You are an expert programmer specializing in translating from {input_lang} to {output_lang}.
    Follow these strict guidelines:
    1. Maintain exact functionality and behavior
    2. Use idiomatic {output_lang} patterns and modern best practices
    3. Preserve all comments and documentation
    4. Implement proper error handling
    5. Use appropriate type annotations where applicable
    6. Follow {output_lang} naming conventions strictly
    7. Optimize for readability and maintainability
    8. Preserve the original code structure
    """,
)

# Modified critic with more thorough review criteria
critic = autogen.AssistantAgent(
    name="Critic",
    llm_config=llm_config,
    system_message=f"""You are a senior code review expert specializing in {output_lang}.
    Thoroughly verify that the translated code:
    1. Maintains identical functionality to the source
    2. Uses idiomatic {output_lang} patterns correctly
    3. Follows all {output_lang} best practices and conventions
    4. Includes proper error handling
    5. Has appropriate type safety
    6. Maintains code organization and structure
    7. Preserves all comments and documentation
    8. Is optimized for performance where possible
    Provide specific, actionable feedback if any improvements are needed.
    """,
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": args.output_dir,
        "use_docker": False,
    }
)

def reflection_message(recipient, messages, sender, config):
    return f"Review the following code translation for correctness and best practices:\n\n{recipient.chat_messages_for_summary(sender)[-1]['content']}"

user_proxy.register_nested_chats(
    [
        {
            "recipient": critic,
            "message": reflection_message,
            "summary_method": "last_msg",
            "max_turns": 1
        }
    ],
    trigger=translator
)

# Define a mapping of languages to file extensions
language_extensions = {
    'Python': '.py',
    'JavaScript': '.js',
    'Java': '.java',
    'C#': '.cs',
    'C++': '.cpp',
    'Ruby': '.rb',
    'Go': '.go',
    'Visual Basic': '.vb',
    'PHP': '.php',
    'Swift': '.swift'
}

def clean_code_output(content):
    """Extract clean code from the model's response, removing any markdown or explanations."""
    if "```" in content:
        # Extract code between triple backticks
        code_blocks = content.split("```")
        for i in range(1, len(code_blocks), 2):  # Only look at blocks between backticks
            block = code_blocks[i].strip()
            if not block:
                continue
            # Remove language identifier if present
            lines = block.split("\n")
            if lines and any(lang in lines[0].lower() for lang in ['python', 'javascript', 'java', 'csharp', 'cpp', 'ruby', 'go', 'vb', 'php', 'swift']):
                return "\n".join(lines[1:]).strip()
            return block.strip()
    return content.strip()

# Process all files in the input directory
for root, _, files in os.walk(args.input_dir):
    for file in files:
        input_path = os.path.join(root, file)
        relative_path = os.path.relpath(input_path, args.input_dir)
        
        # Determine the output file extension based on the target language
        output_extension = language_extensions.get(output_lang, '.txt')  # Default to .txt if not found
        output_file_name = os.path.splitext(relative_path)[0] + output_extension
        output_path = os.path.join(args.output_dir, output_file_name)
        
        # Read source code
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except UnicodeDecodeError:
            with open(input_path, 'r', encoding='ISO-8859-1') as f:
                source_code = f.read()
        
        # Generate translation task
        translation_task = get_translation_task(relative_path, source_code, input_lang, output_lang)
        
        # Initiate translation
        chat_result = user_proxy.initiate_chat(
            recipient=translator,
            message=translation_task,
            max_turns=2,
            summary_method="last_msg"
        )

        # Get the last message from the chat result
        translated_code = clean_code_output(chat_result.summary)

        print(translated_code)

        # Verify we have actual code before saving
        if translated_code:  # Avoid saving explanatory text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_code)
        else:
            print(f"Warning: No valid code extracted for {relative_path}")