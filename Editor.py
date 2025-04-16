import os
import requests
import json
import re
from typing import Optional, Dict, Any, List, Tuple

"""
Programming agent

Input: initial prompt/ reviewer feedback

formatting:
project type: frontend/backend/simple cli app
root directory: "string path"
programming language: python/c/C++/Rust
operating system, environment details i.e. version details
project description: what is it meant to be doing?
edits focus: are we building a component, are we editing/improving a certain section? (should we include line ranges, component names?)
list of errors: [compiler error messages, reviewer's description]
causes of respective errors: [(relevant filepaths, description of errors)]
file contents: [attached using filepath] {relative directories from project root}
previous inputs

there are some usual stpes that you would resort to first before anything else, have you already tried them

what to generate {OUTPUT}
list of edits: (line ranges to replace, what you ahve to make )
list of commands: [(cli/ gui userinput), string command]

future:: using KAG, type of error would be able to give AI the ability to see where system maybe feeling. Graph can describe system, objects and classes at play, and can help narrow down
"""

class Editor:
  def __init__(self, project_desc="", project_type=None, root_dir="", prog_langs=None, os_details=""):
    self.project_desc = project_desc
    self.project_type = project_type or "cli"  # Default to CLI if not specified
    self.root_dir = root_dir
    self.prog_langs = set(prog_langs or [])  # Using set to avoid duplicates
    self.os_details = os_details
    self.edits_focus = ""
    self.errors = []
    self.error_causes = []
    self.file_contents = {}  # Map of filepath -> content
    self.previous_inputs = []
    self.feedback_history = []  # Track feedback from reviewer
    self.code_changes = []  # Track applied code changes
    self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    
  def set_project_type(self, project_type):
    """Set project type from predefined options"""
    valid_types = ["frontend", "backend", "fullstack", "cli", "library", "mobile"]
    if project_type.lower() in valid_types:
      self.project_type = project_type.lower()
    else:
      raise ValueError(f"Project type must be one of: {', '.join(valid_types)}")
    
  def add_language(self, language):
    """Add a programming language to the project"""
    self.prog_langs.add(language)
    
  def remove_language(self, language):
    """Remove a programming language from the project"""
    if language in self.prog_langs:
      self.prog_langs.remove(language)
      
  def set_focus(self, focus_description, line_ranges=None, component_names=None):
    """Set the focus of edits"""
    self.edits_focus = focus_description
    self.focus_line_ranges = line_ranges
    self.focus_components = component_names
    
  def add_error(self, error_message, filepath=None, error_description=None):
    """Add an error and its cause"""
    self.errors.append(error_message)
    self.error_causes.append((filepath, error_description))
    self.feedback_history.append(error_message)
    
  def load_file(self, filepath):
    """Load file contents from disk relative to project root"""
    full_path = f"{self.root_dir}/{filepath}".replace("//", "/")
    try:
      with open(full_path, 'r') as f:
        content = f.read()
        self.file_contents[filepath] = content
        return content
    except Exception as e:
      print(f"Error loading file {full_path}: {e}")
      return None
      
  def save_file(self, filepath, content):
    """Save file contents to disk"""
    full_path = f"{self.root_dir}/{filepath}".replace("//", "/")
    try:
      # Ensure directories exist
      os.makedirs(os.path.dirname(full_path), exist_ok=True)
      
      with open(full_path, 'w') as f:
        f.write(content)
        self.file_contents[filepath] = content
        return True
    except Exception as e:
      print(f"Error saving file {full_path}: {e}")
      return False
  
  def generate_code_with_ollama(self, prompt: str, temperature: float = 0.7) -> str:
    """Generate code using Ollama API based on a prompt
    
    Args:
        prompt: The prompt describing what code to generate
        temperature: Creativity parameter (0.0 to 1.0)
        
    Returns:
        Generated code as a string
    """
    try:
        payload = {
            "model": self.ollama_model,
            "prompt": self._create_code_generation_prompt(prompt),
            "temperature": temperature,
            "stream": False
        }
        
        print(f"Requesting code generation from Ollama ({self.ollama_model})...")
        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json=payload
        )
        
        if response.status_code != 200:
            print(f"Error: Ollama API returned status code {response.status_code}")
            print(f"Error message: {response.text}")
            return f"# Error generating code: {response.text}"
        
        result = response.json()
        generated_text = result.get("response", "# No response received from Ollama")
        
        # Extract code from the response (might contain markdown codeblocks)
        code = self._extract_code_from_response(generated_text)
        
        return code
    
    except Exception as e:
        print(f"ERROR: Failed to get response from Ollama: {e}")
        return f"# Error: Could not get response from Ollama: {e}"
  
  def _create_code_generation_prompt(self, user_prompt: str) -> str:
    """Create a detailed prompt for code generation
    
    Args:
        user_prompt: User's description of what they want to create
        
    Returns:
        Formatted prompt for Ollama
    """
    # Determine the primary language to use based on file extension or user preference
    primary_language = next(iter(self.prog_langs), "Python") if self.prog_langs else "Python"
    
    prompt = f"""You are an expert software engineer. Write code according to these requirements:

PROJECT DETAILS:
- Project type: {self.project_type}
- Target programming language: {primary_language}  
- Programming languages: {', '.join(self.prog_langs) if self.prog_langs else primary_language}
- Operating system: {self.os_details}
- Project description: {self.project_desc}

USER REQUEST:
{user_prompt}

IMPORTANT: Generate code ONLY in {primary_language} programming language.
Use proper syntax, conventions and best practices specific to {primary_language}.
Include appropriate file structure and organization for {primary_language} projects.

Please write clean, well-documented, and error-handled code that fulfills this request.
Include helpful comments and docstrings in the style appropriate for {primary_language}.
Do not include explanations outside of the code - I only need the code itself.
"""
    return prompt

  def _extract_code_from_response(self, response: str) -> str:
    """Extract code blocks from the LLM response
    
    Args:
        response: The raw response from Ollama
        
    Returns:
        Extracted code, removing markdown formatting if present
    """
    import re
    
    # Determine likely language from prog_langs
    target_language = next(iter(self.prog_langs), "python") if self.prog_langs else "python"
    
    # Map common language names to their markdown code block identifiers
    lang_identifiers = {
      "python": ["python", "py"],
      "javascript": ["javascript", "js"],
      "typescript": ["typescript", "ts"],
      "rust": ["rust", "rs"],
      "c": ["c"],
      "c++": ["cpp", "c++"],
      "go": ["go", "golang"],
      "java": ["java"],
      "ruby": ["ruby", "rb"]
    }
    
    # Get identifiers for our target language
    target_identifiers = lang_identifiers.get(target_language.lower(), [target_language.lower()])
    
    # First try to find code blocks with our target language
    for identifier in target_identifiers:
      pattern = f'```{identifier}\\s*\\n(.*?)\\n```'
      code_blocks = re.findall(pattern, response, re.DOTALL)
      if code_blocks:
        return "\n\n".join(code_blocks)
    
    # If not found, look for any code block
    code_blocks = re.findall(r'```(?:\w+)?\s*\n(.*?)\n```', response, re.DOTALL)
    if code_blocks:
      return "\n\n".join(code_blocks)
    
    # If no code blocks found, just return the whole response
    # (removing any potential markdown header/explanations)
    lines = response.split('\n')
    filtered_lines = []
    in_explanation = False
    
    for line in lines:
      # Skip lines that look like explanations or instructions
      if re.match(r'^(Here|This|The|I|Now|First|Next|Then|Finally|Note).*', line) and not in_explanation:
        in_explanation = True
        continue
      
      if in_explanation and line.strip() == '':
        in_explanation = False
        continue
          
      if not in_explanation:
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)
  
  def generate_initial_code(self, user_prompt: str, target_filepath: str) -> bool:
    """Generate initial code based on user prompt and save to file
    
    Args:
        user_prompt: User's description of what they want to create
        target_filepath: Path where the generated code should be saved
        
    Returns:
        True if successful, False otherwise
    """
    print(f"Generating initial code from prompt: '{user_prompt}'")
    
    try:
        # Determine language from file extension
        _, file_extension = os.path.splitext(target_filepath)
        
        # Map file extensions to languages
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
        
        # Determine language from file extension
        file_language = extension_to_language.get(file_extension.lower(), 'python')
        
        # Ensure the language is in prog_langs
        self.prog_langs.add(file_language)
        
        # Generate code using Ollama
        generated_code = self.generate_code_with_ollama(user_prompt)
        
        if not generated_code or generated_code.startswith("# Error"):
            print("Failed to generate code")
            return False
            
        # Save the generated code to file
        success = self.save_file(target_filepath, generated_code)
        
        if success:
            print(f"Successfully generated and saved {file_language} code to {target_filepath}")
            
            # Add to code changes list for tracking
            self.code_changes.append({
                'filepath': target_filepath,
                'code': generated_code,
                'description': f"Initial code generated from prompt: {user_prompt[:50]}..."
            })
            
        return success
    except Exception as e:
        print(f"Error generating initial code: {e}")
        return False
      
  def generate_edits(self):
    """Generate list of edits based on errors and file contents"""
    edits = []
    
    # Use the most recent feedback if available
    if self.feedback_history:
      edits = self.generate_edits_from_feedback(self.feedback_history[-1])
    
    return edits
    
  def generate_edits_from_feedback(self, feedback):
    """Generate edits from reviewer feedback
    
    Args:
      feedback: The feedback text from the reviewer
      
    Returns:
      List of edit objects that can be applied by apply_edits
    """
    edits = []
    
    # Parse the feedback into actionable items
    actionable_items = self.parse_reviewer_feedback(feedback)
    
    # Convert actionable items to edits
    for item in actionable_items:
      edit = {
        'edit_type': 'manual',
        'suggestion': item.get('description', '')
      }
      
      # Add line range if available
      if 'line_start' in item and 'line_end' in item:
        edit['line_start'] = item['line_start']
        edit['line_end'] = item['line_end']
      
      # Add code if available
      if 'code' in item:
        edit['code'] = item['code']
        edit['edit_type'] = 'replace'
      
      # Try to determine filepath
      filepath = item.get('file')
      if not filepath and self.file_contents:
        # Use the first file we know about if no file is specified
        filepath = next(iter(self.file_contents))
      
      # Only add edits with a valid filepath
      if filepath:
        edit['filepath'] = filepath
        edits.append(edit)
    
    return edits
    
  def generate_commands(self):
    """Generate list of commands to fix issues"""
    commands = []
    # Generate appropriate CLI commands based on project type,
    # programming languages and detected errors
    return commands
    
  def apply_edit(self, filepath, line_start, line_end, replacement_text):
    """Apply an edit to a specific file between specified line ranges
    
    Args:
      filepath: Path to the file to edit
      line_start: Starting line number (1-based index)
      line_end: Ending line number (1-based index, inclusive)
      replacement_text: Text to replace the specified lines with
      
    Returns:
      True if the edit was applied successfully, False otherwise
    """
    if filepath not in self.file_contents:
      self.load_file(filepath)
      
    if filepath in self.file_contents:
      lines = self.file_contents[filepath].split('\n')
      
      # Convert to 0-based indexing for Python lists
      start_idx = max(0, line_start - 1)
      end_idx = min(len(lines), line_end)
      
      # Validate line range
      if start_idx < 0 or end_idx > len(lines) or start_idx >= end_idx:
        print(f"Invalid line range: {line_start}-{line_end} for file with {len(lines)} lines")
        return False
      
      # Replace the specified lines
      new_lines = lines[:start_idx] + replacement_text.split('\n') + lines[end_idx:]
      new_content = '\n'.join(new_lines)
      
      # Update in memory and save to disk
      self.file_contents[filepath] = new_content
      return self.save_file(filepath, new_content)
    
    return False
  
  def log_input(self, input_text):
    """Log previous inputs for context"""
    self.previous_inputs.append(input_text)
    
  def get_standard_fixes(self):
    """Return list of standard fixes to try before complex solutions"""
    return [
      "Check for syntax errors",
      "Verify all imports/dependencies are installed",
      "Check file permissions",
      "Restart development server/environment",
      "Clear cache files",
      "Check for outdated packages"
    ]
  
  def parse_line_range(self, comment_text):
    """Parse a comment for line range specification
    
    Args:
      comment_text: Text of the comment to parse
      
    Returns:
      A tuple of (start_line, end_line, remaining_text) or None if no line range is found
    """
    # Multiple patterns to match different line range formats
    patterns = [
      # Standard format: "Line X: text" or "Lines X-Y: text"
      r'^(?:Line[s]?\s+(\d+)(?:-(\d+))?):\s*(.+)',
      # Alternative format: "On line X, text" or "On lines X-Y, text"
      r'On\s+lines?\s+(\d+)(?:-(\d+))?,\s*(.+)',
      # Format with "at": "At line X, text" or "At lines X-Y, text"
      r'At\s+lines?\s+(\d+)(?:-(\d+))?,\s*(.+)',
      # Format in issue description: "Issue in line X: text" or "Issue in lines X-Y: text"
      r'Issue\s+in\s+lines?\s+(\d+)(?:-(\d+))?:\s*(.+)'
    ]
    
    if not comment_text:
      return None
      
    comment_text = comment_text.strip()
    
    # Try each pattern
    for pattern in patterns:
      match = re.match(pattern, comment_text, re.DOTALL | re.IGNORECASE)
      if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        text = match.group(3).strip()
        return (start, end, text)
    
    # If no pattern matched directly, look for line mentions anywhere in text
    anywhere_patterns = [
      r'lines?\s+(\d+)(?:-(\d+))?',  # "line X" or "lines X-Y" 
      r'(?:in|at|on)\s+lines?\s+(\d+)(?:-(\d+))?'  # "in line X" or "at lines X-Y"
    ]
    
    for pattern in anywhere_patterns:
      match = re.search(pattern, comment_text, re.IGNORECASE)
      if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        # Return the whole comment since we can't easily separate it
        return (start, end, comment_text)
    
    return None

  def infer_line_ranges_from_code(self, code_snippet, file_content):
    """Try to infer where a code snippet should go in a file
    
    Args:
      code_snippet: The code snippet to place
      file_content: The current file content
      
    Returns:
      A tuple of (start_line, end_line) or None if can't be determined
    """
    if not code_snippet or not file_content:
      return None
    
    # Try to find function or class names in the code snippet
    function_match = re.search(r'def\s+([a-zA-Z0-9_]+)', code_snippet)
    class_match = re.search(r'class\s+([a-zA-Z0-9_]+)', code_snippet)
    
    # If we found a function or class name, look for it in the file
    if function_match:
      function_name = function_match.group(1)
      # Look for the function definition in the file
      lines = file_content.split('\n')
      for i, line in enumerate(lines):
        if re.search(rf'def\s+{re.escape(function_name)}\s*\(', line):
          # Find the end of the function
          start_line = i + 1
          end_line = start_line
          indent = len(line) - len(line.lstrip())
          for j in range(start_line, len(lines)):
            if j == len(lines) - 1 or (lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent):
              end_line = j
              break
          return (start_line, end_line)
    
    elif class_match:
      # Similar logic for classes
      class_name = class_match.group(1)
      lines = file_content.split('\n')
      for i, line in enumerate(lines):
        if re.search(rf'class\s+{re.escape(class_name)}\s*', line):
          start_line = i + 1
          end_line = start_line
          indent = len(line) - len(line.lstrip())
          for j in range(start_line, len(lines)):
            if j == len(lines) - 1 or (lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent):
              end_line = j
              break
          return (start_line, end_line)
    
    # If we couldn't find exact matches, look for similar code structure
    lines = file_content.split('\n')
    code_lines = code_snippet.split('\n')
    
    # If the snippet is a function or method, try to replace a similar function
    if any(line.strip().startswith('def ') for line in code_lines):
      # Get the function signature line
      sig_line = next(line for line in code_lines if line.strip().startswith('def '))
      func_name = re.search(r'def\s+([a-zA-Z0-9_]+)', sig_line).group(1)
      
      # Look for similar function names in the file
      for i, line in enumerate(lines):
        if re.search(rf'def\s+{re.escape(func_name)}', line):
          # Find the end of this function
          start_line = i + 1
          indent = len(line) - len(line.lstrip())
          for j in range(start_line, len(lines)):
            if j == len(lines) - 1 or (lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= indent):
              end_line = j + 1
              return (start_line, end_line)
    
    # If all else fails, append to end of file
    return None

  def apply_edits(self, edits):
    """Apply a list of edits to files"""
    applied_edits = []
    
    for edit in edits:
      filepath = edit.get('filepath')
      if not filepath:
        continue
        
      # Load file if not already loaded
      if filepath not in self.file_contents:
        self.load_file(filepath)
      
      if filepath not in self.file_contents:
        continue
      
      # Check for line range specification
      line_start = edit.get('line_start')
      line_end = edit.get('line_end')
      
      # Apply different types of edits
      if edit['edit_type'] == 'replace' and 'code' in edit:
        success = False
        
        # If we have line ranges, apply edit to those specific lines
        if line_start is not None and line_end is not None:
          success = self.apply_edit(filepath, line_start, line_end, edit['code'])
          if success:
            print(f"Applied edit to {filepath} lines {line_start}-{line_end}")
        else:
          # Try to infer line ranges for the code
          file_content = self.file_contents[filepath]
          inferred_range = self.infer_line_ranges_from_code(edit['code'], file_content)
          
          # SAFETY CHECK: Only replace entire file if it's small or empty
          # Otherwise, look for function/class matches or append at end if we can't determine
          if inferred_range:
            line_start, line_end = inferred_range
            success = self.apply_edit(filepath, line_start, line_end, edit['code'])
            if success:
              print(f"Applied edit to {filepath} lines {line_start}-{line_end} (inferred)")
          elif len(file_content.split('\n')) <= 10 or not file_content.strip():
            # Small file or empty file - safe to replace
            success = self.save_file(filepath, edit['code'])
            if success:
              print(f"Replaced entire file {filepath} (small file)")
          else:
            # Large file without clear placement - append to end with a comment
            code_with_comment = f"\n\n# Added code based on feedback:\n{edit['code']}"
            lines = file_content.split('\n')
            new_content = '\n'.join(lines) + code_with_comment
            success = self.save_file(filepath, new_content)
            if success:
              print(f"Appended code to end of {filepath} (could not determine line range)")
        
        if success:
          applied_edits.append(edit)
          self.code_changes.append({
            'filepath': filepath,
            'line_start': line_start,
            'line_end': line_end,
            'code': edit['code'],
            'description': edit.get('suggestion', 'Code update')
          })
      
      elif edit['edit_type'] == 'manual':
        # For manual edits, use Ollama API to generate code changes
        if 'suggestion' in edit:
          # Create a more precise prompt if we have line ranges
          context_prompt = edit['suggestion']
          code_context = self.file_contents[filepath]
          
          if line_start is not None and line_end is not None:
            # Extract the specific lines to focus on
            lines = code_context.split('\n')
            
            # Adjust to 0-based indexing
            start_idx = max(0, line_start - 1)
            end_idx = min(len(lines), line_end)
            
            # Add a few lines of context before and after
            context_start = max(0, start_idx - 3)
            context_end = min(len(lines), end_idx + 3)
            
            focus_lines = '\n'.join(lines[start_idx:end_idx])
            context_lines = '\n'.join(lines[context_start:context_end])
            
            context_prompt = f"Update lines {line_start}-{line_end}: {edit['suggestion']}\n\nFocus on these lines:\n```python\n{focus_lines}\n```\n\nHere's some context around those lines:\n```python\n{context_lines}\n```"
          
          updated_code = self.query_ai_for_implementation(
            context_prompt, 
            filepath, 
            code_context
          )
          
          if updated_code and updated_code != code_context:
            if line_start is not None and line_end is not None:
              # Apply changes only to the specified line range
              success = self.apply_edit(filepath, line_start, line_end, updated_code)
              if success:
                print(f"Applied AI-generated changes to {filepath} lines {line_start}-{line_end}")
            else:
              # Replace entire file
              success = self.save_file(filepath, updated_code)
              if success:
                print(f"Replaced entire file {filepath} with AI-generated code")
            
            if success:
              edit['code'] = updated_code
              applied_edits.append(edit)
              self.code_changes.append({
                'filepath': filepath,
                'line_start': line_start,
                'line_end': line_end,
                'code': updated_code,
                'description': edit.get('suggestion', 'Code update')
              })
    
    return applied_edits
  
  def query_ai_for_implementation(self, prompt, filepath=None, code_context=None):
    """Query Ollama API to get code implementation for a specific suggestion
    
    Args:
      prompt: Description of what needs to be implemented
      filepath: File to modify (for context)
      code_context: Existing code to provide context
      
    Returns:
      Generated code from the AI
    """
    # If we don't have code context but have filepath, load it
    if code_context is None and filepath is not None and filepath in self.file_contents:
      code_context = self.file_contents[filepath]
    
    # Check if prompt contains line range specification
    line_range = self.parse_line_range(prompt)
    if line_range:
      start_line, end_line, prompt_text = line_range
      prompt = f"Update lines {start_line}-{end_line}: {prompt_text}"
    
    # Construct detailed prompt for Ollama
    full_prompt = f"""You are an expert programmer helping to improve code.

Task: {prompt}

Current code:
```python
{code_context}
```

Please provide the exact updated code for ONLY the portion that needs to be changed.
Return ONLY the revised code with no explanations.
The code should be correctly indented and ready to use as a direct replacement.
"""
    
    try:
      payload = {
        "model": self.ollama_model,
        "prompt": full_prompt,
        "temperature": 0.3,  # Lower temperature for more focused code changes
        "stream": False
      }
      
      print(f"Requesting code changes from Ollama ({self.ollama_model})...")
      response = requests.post(
        f"{self.ollama_base_url}/api/generate",
        json=payload
      )
      
      if response.status_code != 200:
        print(f"Error: Ollama API returned status code {response.status_code}")
        return code_context
      
      result = response.json()
      generated_code = result.get("response", "")
      
      # Extract code from response
      updated_code = self._extract_code_from_response(generated_code)
      
      if not updated_code:
        return code_context
      
      return updated_code
      
    except Exception as e:
      print(f"ERROR: Failed to get response from Ollama: {e}")
      return code_context

  def get_reviewer_prompt(self):
    """Generate a prompt for reviewers to ensure feedback is formatted correctly
    
    Returns:
      A string containing formatting instructions for reviewers
    """
    prompt = """
REVIEWER FORMATTING GUIDE

Please format your feedback following these guidelines to ensure it can be properly parsed:

1. For each issue, start with "ISSUE:" followed by a brief description.
   Example: "ISSUE: The calculator doesn't handle negative numbers correctly."

2. For each suggestion, start with "SUGGESTION:" followed by your recommendation.
   Example: "SUGGESTION: Add a check for negative numbers in the validate_input function."

3. ALWAYS specify line numbers for changes using one of these formats:
   - "Line X: Your comment" for a single line
   - "Lines X-Y: Your comment" for a range of lines
   Example: "Line 42: Fix the variable initialization here."
   Example: "Lines 15-20: This loop needs to be optimized."

4. If you're referencing specific files, mention them clearly like:
   "in calculator.py" or "modify app.js"

5. If you have code suggestions, include them within triple backticks:
   ```python
   def example_function():
       # your suggested code here
       pass
   ```

6. For test commands, ensure they are properly formatted and escaped:
   "Test command: python -m pytest test_file.py -v"

Thank you for following this format to help our automated processing!
"""
    return prompt
  def parse_reviewer_feedback(self, feedback):
    """Parse reviewer feedback to extract actionable items.
    
    Args:
        feedback (str): The feedback text from the reviewer
        
    Returns:
        list: A list of dictionaries containing structured feedback items
    """
    actionable_items = []
    lines = feedback.split('\n')
    
    current_item = None
    code_block = []
    in_code_block = False
    
    for line in lines:
        line = line.strip()
        
        # Handle code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                # Extract language if specified
                language = line[3:].strip()
                code_block = []
                if current_item:
                    current_item['code_language'] = language
            else:
                # End of code block
                if current_item:
                    current_item['code'] = '\n'.join(code_block)
            continue
        
        if in_code_block:
            code_block.append(line)
            continue
            
        # Parse issues and suggestions
        if line.startswith('ISSUE:'):
            if current_item:
                actionable_items.append(current_item)
            current_item = {'type': 'issue', 'description': line[6:].strip()}
        elif line.startswith('SUGGESTION:'):
            if current_item:
                actionable_items.append(current_item)
            current_item = {'type': 'suggestion', 'description': line[11:].strip()}
        elif current_item and line:
            # Parse line references
            line_match = re.match(r'Line[s]?\s+(\d+)(?:-(\d+))?\s*:\s*(.*)', line)
            if line_match:
                start_line = int(line_match.group(1))
                end_line = int(line_match.group(2)) if line_match.group(2) else start_line
                comment = line_match.group(3)
                
                current_item['line_start'] = start_line
                current_item['line_end'] = end_line
                current_item['line_comment'] = comment
            else:
                # Append to the description
                current_item['description'] += " " + line
    
    # Add the last item if exists
    if current_item:
        actionable_items.append(current_item)
        
    return actionable_items