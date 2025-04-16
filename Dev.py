import os
import time
import sys
import re
from Editor import Editor
from Tester import Tester
from Reviewer import Reviewer

class AutomatedDevelopment:
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or os.path.dirname(os.path.abspath(__file__))
        self.editor = Editor(root_dir=self.project_dir)
        self.tester = Tester(project_dir=self.project_dir)
        self.reviewer = Reviewer("llama3.2")  # Using the simplified Reviewer class
        self.max_iterations = 5
        self.target_file = None
        self.user_prompt = ""
        
    def run(self, initial_prompt=None):
        """Main development cycle"""
        print("Starting automated development process...")
        
        # Initialize project settings
        self._initialize_project()
        
        # Get initial user prompt for code generation
        if initial_prompt:
            self.user_prompt = initial_prompt
        else:
            self.user_prompt = self._get_user_prompt()
            
        # Determine target file based on prompt
        self._determine_target_file()
        
        for iteration in range(self.max_iterations):
            print(f"\n--- Iteration {iteration+1}/{self.max_iterations} ---")
            
            # Step 1: Generate/edit code
            self._edit_code(iteration)
            
            # Step 2: Generate & run tests automatically
            test_results = self._auto_test_code()
            
            # Step 3: Review results
            feedback = self._review_results(test_results)
            
            # Step 4: Process feedback and make it actionable
            actionable_feedback = self._process_feedback(feedback)
            
            # Check if we're done
            if "SUCCESS" in feedback.upper() or test_results['successful_actions'] == test_results['total_actions']:
                print("Development complete! Application working correctly.")
                break
                
            # Update editor with actionable feedback for next iteration
            self.editor.add_error(feedback)
            
            time.sleep(1)  # Brief pause between iterations
    
    def _get_user_prompt(self):
        """Get the initial prompt from the user describing what they want to create"""
        print("\n=== Project Description ===")
        print("Please describe what you'd like to create.")
        print("For example: 'A calculator app with basic arithmetic operations and memory functions'")
        print("Or: 'A to-do list application with the ability to add, complete, and delete tasks'")
        
        user_input = input("\nWhat would you like to create? ")
        
        if not user_input.strip():
            print("Using default prompt: A simple calculator app with basic arithmetic operations")
            return "A simple calculator app with basic arithmetic operations"
        
        return user_input.strip()
    
    def _determine_target_file(self):
        """Determine the target file based on the user prompt"""
        # First, determine the programming language from the prompt
        language_indicators = {
            "python": ["python", "flask", "django", "pandas", "numpy"],
            "javascript": ["javascript", "js", "node", "react", "vue", "angular"],
            "typescript": ["typescript", "ts", "angular"],
            "rust": ["rust", "cargo"],
            "c": ["c programming", "c language"],
            "cpp": ["c++", "cpp"],
            "java": ["java", "spring"],
            "go": ["golang", "go language"],
            "ruby": ["ruby", "rails"]
        }
        
        # Default language is python
        
        language = "python"
        
        # Determine language from prompt
        for lang, indicators in language_indicators.items():
            if any(indicator in self.user_prompt.lower() for indicator in indicators):
                language = lang
                break
        
        # Language-specific file extensions
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "rust": ".rs",
            "c": ".c",
            "cpp": ".cpp",
            "java": ".java",
            "go": ".go",
            "ruby": ".rb"
        }
        
        # Project type indicators with appropriate filenames per language
        project_type_indicators = {
            "calculator": {
                "python": "calculator.py",
                "javascript": "calculator.js",
                "typescript": "calculator.ts",
                "rust": "calculator.rs",
                "c": "calculator.c",
                "cpp": "calculator.cpp",
                "java": "Calculator.java",
                "go": "calculator.go",
                "ruby": "calculator.rb"
            },
            "todo": {
                "python": "todo.py",
                "javascript": "todo.js",
                "typescript": "todo.ts",
                "rust": "todo.rs",
                "c": "todo.c",
                "cpp": "todo.cpp",
                "java": "Todo.java",
                "go": "todo.go",
                "ruby": "todo.rb"
            },
            "web": {
                "python": "app.py",
                "javascript": "server.js",
                "typescript": "server.ts",
                "rust": "main.rs",
                "c": "server.c",
                "cpp": "server.cpp",
                "java": "Application.java",
                "go": "server.go",
                "ruby": "app.rb"
            },
            "game": {
                "python": "game.py",
                "javascript": "game.js",
                "typescript": "game.ts",
                "rust": "game.rs",
                "c": "game.c",
                "cpp": "game.cpp",
                "java": "Game.java",
                "go": "game.go",
                "ruby": "game.rb"
            },
            "api": {
                "python": "api.py",
                "javascript": "api.js",
                "typescript": "api.ts",
                "rust": "api.rs",
                "c": "api.c",
                "cpp": "api.cpp",
                "java": "ApiService.java",
                "go": "api.go",
                "ruby": "api.rb"
            }
        }
        
        # Try to find a matching project type first
        self.target_file = f"main{extensions.get(language, '.py')}"  # Default with language extension
        
        for indicator, filenames in project_type_indicators.items():
            if indicator.lower() in self.user_prompt.lower():
                self.target_file = filenames.get(language, filenames.get("python"))
                break
        
        # For complex or ambiguous cases, ask the LLM for a good filename
        if "advanced" in self.user_prompt.lower() or "complex" in self.user_prompt.lower() or len(self.user_prompt.split()) > 15:
            suggested_filename = self._query_llm_for_filename(self.user_prompt, language)
            if suggested_filename:
                self.target_file = suggested_filename
        
        # Ensure full path
        self.target_file = os.path.join(self.project_dir, self.target_file)
        
        # Update editor's programming language to match target file
        _, file_extension = os.path.splitext(self.target_file)
        extension_to_language = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'c++',
            '.h': 'c',
            '.java': 'java',
            '.go': 'go',
            '.rb': 'ruby'
        }
        detected_language = extension_to_language.get(file_extension.lower(), language)
        
        # Clear existing languages and set to the one we're using
        self.editor.prog_langs.clear()
        self.editor.add_language(detected_language)
        
        print(f"Target file: {self.target_file} (Language: {detected_language})")
    
    def _query_llm_for_filename(self, prompt, language):
        """Query the LLM to suggest an appropriate filename based on the project description"""
        try:
            # Construct a JSON-focused prompt for the LLM
            json_prompt = f"""Based on this project description: "{prompt}", 
suggest an appropriate filename with the correct extension for {language}.
Respond ONLY with a JSON object in this exact format: {{"filename": "your_suggested_filename"}}
Make sure the extension is appropriate for {language}."""
            
            # Query the LLM through the reviewer (which uses Ollama)
            response = self.reviewer.review("", json_prompt, "")
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON pattern in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    json_response = json.loads(json_match.group(0))
                    if "filename" in json_response:
                        print(f"LLM suggested filename: {json_response['filename']}")
                        return json_response["filename"]
                except json.JSONDecodeError:
                    print("Could not parse JSON from LLM response")
            
            print("LLM did not return a valid filename suggestion")
            return None
            
        except Exception as e:
            print(f"Error querying LLM for filename: {e}")
            return None
    
    def _initialize_project(self):
        """Set up initial project parameters"""
        # No longer add python by default - language will be set by _determine_target_file
        
        # Update project description based on user prompt if available
        if self.user_prompt:
            self.editor.set_focus(self.user_prompt)
        else:
            self.editor.set_focus("Application")
        
        # Define project details
        project_details = {
            "project_type": "simple cli app",
            "root_directory": self.project_dir,
            "os": "cross-platform",
            "project_description": self.user_prompt or "An application"
        }
        
        for key, value in project_details.items():
            if hasattr(self.editor, key):
                setattr(self.editor, key, value)
    
    def _edit_code(self, iteration):
        """Generate or edit code based on iteration and feedback"""
        if iteration == 0:
            # First iteration: Generate code based on user prompt
            print(f"Generating initial code based on prompt: '{self.user_prompt}'")
            
            # Use Ollama to generate the initial code
            success = self.editor.generate_initial_code(
                self.user_prompt, 
                os.path.basename(self.target_file)
            )
            
            if not success:
                print("Failed to generate code with Ollama, using simple template")
                # Create a minimal Python file
                with open(self.target_file, 'w') as f:
                    f.write(f"""
# {os.path.basename(self.target_file)}
# Purpose: {self.user_prompt}

def main():
    print("Hello, World!")
    print("This is a placeholder for: {self.user_prompt}")
    
if __name__ == "__main__":
    main()
""")
                print("Added default template into file")
        else:
            # Generate edits based on feedback
            edits = self.editor.generate_edits()
            
            if edits:
                print(f"Applying {len(edits)} edits to code...")
                applied_edits = self.editor.apply_edits(edits)
                
                if applied_edits:
                    print(f"Successfully applied {len(applied_edits)} edits")
                    for edit in applied_edits:
                        print(f"- Applied edit to {edit.get('filepath')}: {edit.get('suggestion', 'Code update')}")
                else:
                    print("Could not automatically apply edits, generating manual changes...")
                    self._apply_manual_edits(edits)
            else:
                print("No edits to apply in this iteration")
    
    def _apply_manual_edits(self, edits):
        """Apply edits manually by requesting code from the AI"""
        for edit in edits:
            if edit.get('edit_type') == 'manual' and 'suggestion' in edit and 'filepath' in edit:
                # Load file if needed
                filepath = edit['filepath']
                if filepath not in self.editor.file_contents:
                    self.editor.load_file(filepath)
                
                if filepath not in self.editor.file_contents:
                    continue
                
                # Use the Ollama API via editor's query_ai_for_implementation method
                updated_code = self.editor.query_ai_for_implementation(
                    edit['suggestion'],
                    filepath,
                    self.editor.file_contents[filepath]
                )
                
                if updated_code and updated_code != self.editor.file_contents[filepath]:
                    success = self.editor.save_file(filepath, updated_code)
                    if success:
                        print(f"- Updated {filepath} with AI-generated code")
    
    def _auto_test_code(self):
        """Generate and run tests for the code automatically"""
        print("Generating and running tests automatically...")
        
        # Reset tester's actions
        self.tester.actions = []
        self.tester.results = []
        
        # Generate tests using Ollama
        target_file_rel = os.path.relpath(self.target_file, self.project_dir)
        print(f"Generating tests for {target_file_rel}")
        
        # Generate and add tests to the queue
        success = self.tester.add_generated_tests(self.target_file, num_tests=3)
        
        if not success or not self.tester.actions:
            print("Test generation failed, adding basic test")
            run_command = self.tester.get_run_command(target_file_rel)
            self.tester.add_cli_action(run_command, "", 3, None)
        
        # Execute all tests
        print("Executing tests...")
        results = self.tester.execute_all_actions()
        
        return results
    
    def _review_results(self, test_results):
        """Review test results using the reviewer agent"""
        # Format test results as text
        test_output = self.tester._format_test_results(test_results)
        
        # Get line range formatting instructions
        line_range_instructions = self.reviewer.get_line_range_format_instructions()
        
        prompt = (
            f"Review these test results for the code which implements: '{self.user_prompt}'. "
            f"There were {test_results['successful_actions']} successful tests "
            f"out of {test_results['total_actions']} total tests. "
            f"Identify any issues and suggest specific fixes. "
            f"If there are code changes needed, please provide the exact code that should be used.\n\n"
            f"⚠️ CRITICAL: For EVERY code change, you MUST specify the exact line numbers to edit.\n"
            f"USE EXACTLY THIS FORMAT: \"Line X: Comment\" or \"Lines X-Y: Comment\"\n"
            f"If you don't specify line numbers, the ENTIRE file will be replaced!\n\n"
            f"{line_range_instructions}\n\n"
            f"Format your response with clear sections for ISSUES, SUGGESTIONS, and CODE if applicable."
        )
        
        # Additional context from test results
        context = f"Success rate: {test_results['success_rate']}"
        if 'first_failure' in test_results:
            context += f"\nFirst failure at action {test_results['first_failure']['action_index']}: "
            if 'error' in test_results['first_failure']['result']:
                context += test_results['first_failure']['result']['error']
            elif 'stderr' in test_results['first_failure']['result']:
                context += test_results['first_failure']['result']['stderr']
        
        # Debug statement before calling review
        print(f"Requesting review from Ollama model '{self.reviewer.model_name}'")
        
        # Review the test results as text
        feedback = self.reviewer.review(test_output, prompt, context)
        
        # Debug statement after receiving response
        print(f"Received review feedback ({len(feedback)} characters)")
        
        return feedback
    
    def _process_feedback(self, feedback):
        """Process feedback to make it actionable"""
        print("Processing feedback for actionable items...")
        
        # Parse feedback into actionable items
        actionable_items = self.editor.parse_reviewer_feedback(feedback)
        
        # Print actionable items
        if actionable_items:
            print(f"Identified {len(actionable_items)} actionable items:")
            for i, item in enumerate(actionable_items):
                print(f"{i+1}. Issue: {item.get('issue', 'Unknown issue')}")
                print(f"   Suggestion: {item.get('suggestion', 'No suggestion')}")
                if 'line_start' in item:
                    line_range = f"Line {item['line_start']}"
                    if item.get('line_end') and item['line_end'] != item['line_start']:
                        line_range += f"-{item['line_end']}"
                    print(f"   {line_range}")
                if 'file' in item:
                    print(f"   File: {item.get('file')}")
                if 'code' in item:
                    print(f"   Code: {item.get('code', '')[:50]}..." if len(item.get('code', '')) > 50 else f"   Code: {item.get('code', '')}")
                print()
        else:
            print("No actionable items identified in feedback")
        
        return actionable_items

if __name__ == "__main__":
    # Check for command line arguments
    initial_prompt = None
    if len(sys.argv) > 1:
        initial_prompt = sys.argv[1]
    
    auto_dev = AutomatedDevelopment()
    auto_dev.run(initial_prompt)