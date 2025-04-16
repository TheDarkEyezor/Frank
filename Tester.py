import os
import subprocess
import time
import re
import requests
import json
import shlex
from typing import List, Dict, Any, Optional

#------------ Tester
""" testing agent
we want this agent to be able to take in commands from the reviewer and traslate them into a an action that can be run with a separate thread, by a separate program?

input formatting:
list of inputs/actions [(cli, user input, wait), (input, action{mouse, keyboard input}, how long]

action:
every action is interpresered with a screenshot

output:
chain of commands along with success/failure code, along wsit5h suspected code snippet/file where failure occurred
error messages from compiler orwait time exceeded
clean up code if needed {getting rid of junk files} (unless flagged for errors][])
passed to reviewer
"""
class Tester:
  def __init__(self, project_dir=""):
    self.project_dir = project_dir
    self.actions = []  # List of actions to execute
    self.results = []  # Results for each action
    self.screenshots = []  # Paths to screenshots taken
    self.error_logs = []  # Captured error messages
    self.temp_files = []  # Files created during testing that might need cleanup
    self.action_queue = []  # Queue for concurrent action execution
    self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    
    # Language-specific run commands mapping
    self.language_commands = {
      # Interpreted languages
      ".py": "python {filepath}",
      ".js": "node {filepath}",
      ".ts": "ts-node {filepath}",
      ".rb": "ruby {filepath}",
      ".php": "php {filepath}",
      ".pl": "perl {filepath}",
      ".sh": "bash {filepath}",
      ".lua": "lua {filepath}",
      
      # Compiled languages with direct run commands
      ".go": "go run {filepath}",
      ".swift": "swift {filepath}",
      ".kt": "kotlin {filepath}",
      ".groovy": "groovy {filepath}",
      
      # Compiled languages requiring build steps
      # For these, we just return the run command assuming the build has been done
      ".java": "java -cp {dirpath} {classname}",
      ".rs": "cargo run --bin {basename} || (cd {dirpath} && rustc {filepath} -o {basename} && ./{basename})",
      ".c": "(cd {dirpath} && gcc {filepath} -o {basename} && ./{basename})",
      ".cpp": "(cd {dirpath} && g++ {filepath} -o {basename} && ./{basename})",
      ".cs": "dotnet run --project {filepath}"
    }
    
  def add_cli_action(self, command, input_text=None, wait_time=5, expected_output=None):
    """Add a CLI command action with optional input and wait time in seconds"""
    self.actions.append(("cli", command, input_text, wait_time, expected_output))
    return self  # For chaining
  
  def add_input_action(self, action_type, parameters, wait_time=1):
    """Add a mouse or keyboard input action
    
    Args:
      action_type: 'mouse' or 'keyboard'
      parameters: For mouse: (x, y, 'click'|'double'|'right'|'drag')
                  For keyboard: Text to type or special key name
      wait_time: Time to wait after action in seconds
    """
    self.actions.append(("input", action_type, parameters, wait_time))
    return self  # For chaining
    
  def take_screenshot(self, name=None):
    """Take a screenshot of the current screen state"""
    import pyautogui
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = name or f"screenshot_{timestamp}.png"
    filepath = f"{self.project_dir}/screenshots/{name}"
    
    try:
      # Ensure screenshot directory exists
      import os
      os.makedirs(f"{self.project_dir}/screenshots", exist_ok=True)
      
      # Take screenshot
      screenshot = pyautogui.screenshot()
      screenshot.save(filepath)
      self.screenshots.append(filepath)
      return filepath
    except Exception as e:
      self.error_logs.append(f"Screenshot error: {e}")
      return None
  
  def build_command(self, command, input_text=None):
    """Build a properly escaped command for CLI execution
    
    Args:
      command: The command to execute
      input_text: Optional input text to provide to the command
      
    Returns:
      A tuple of (command_list, shell_required)
    """
    # Determine if we need to use shell=True
    shell_required = False
    
    # Check if command contains shell-specific features
    shell_features = ['|', '>', '<', '&', ';', '$(', '`', '&&', '||']
    if any(feature in command for feature in shell_features):
      shell_required = True
      return command, shell_required
    
    try:
      # Try to split the command into parts - raises ValueError if unable to parse
      command_parts = shlex.split(command)
      return command_parts, shell_required
    except ValueError:
      # If we can't parse it safely, use shell=True
      shell_required = True
      return command, shell_required
  
  def validate_command(self, command):
    """Validate that a command is safe to execute
    
    Args:
      command: The command to validate (string or list of strings)
      
    Returns:
      True if the command passes validation, False otherwise
    """
    # Convert to string for pattern matching if it's a list
    cmd_str = ' '.join(command) if isinstance(command, list) else command
    
    # Check for minimum command length
    if not cmd_str or len(cmd_str) < 2:
      print("Command validation failed: Command too short")
      return False
    
    # Check for suspicious destructive commands
    suspicious_patterns = [
      r'\brm\s+(-[rf]\s+|--recursive\s+|--force\s+)',
      r'\bremove\s+(-[rf]\s+)',
      r'\bdel\s+(/[sqa]\s+)',
      r'\bformat\s+',
      r'\bdd\s+if=',
      r';\s*rm\s',
      r';\s*del\s',
      r'\bmkfs\b',
      r':(){:',  # Fork bomb pattern
      r'\beval\b',
      r'\bexec\b'
    ]
    
    for pattern in suspicious_patterns:
      if re.search(pattern, cmd_str, re.IGNORECASE):
        print(f"Command validation failed: Matched suspicious pattern {pattern}")
        return False
    
    # Check for too many semicolons (command chaining)
    if cmd_str.count(';') > 3:
      print("Command validation failed: Too many command separators (;)")
      return False
    
    # Check for balanced quotes
    if cmd_str.count('"') % 2 != 0 or cmd_str.count("'") % 2 != 0:
      print("Command validation failed: Unbalanced quotes")
      return False
    
    return True
  
  def execute_cli(self, command, input_text=None, wait_time=5, expected_output=None):
    """Execute a CLI command, capture output, and verify against expected output"""
    import subprocess
    import time
    
    try:
      # Take screenshot before execution
      self.take_screenshot(f"before_cli_{len(self.results)}.png")
      
      # Build and validate command
      cmd, shell_required = self.build_command(command)
      
      if not self.validate_command(cmd):
        result = {
          "command": command,
          "exit_code": -3,
          "stdout": "",
          "stderr": "Command validation failed: potentially unsafe operation",
          "success": False,
          "output_verified": False
        }
        self.results.append(result)
        self.error_logs.append(f"Command validation failed for '{command}'")
        return result
      
      # Set up process
      if input_text:
        process = subprocess.Popen(
          cmd,
          shell=shell_required,
          text=True,
          stdin=subprocess.PIPE,
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=input_text, timeout=wait_time)
      else:
        process = subprocess.Popen(
          cmd,
          shell=shell_required,
          text=True,
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=wait_time)
      
      # Wait for specified time
      time.sleep(min(wait_time, 1))  # Wait at least a bit but don't wait unnecessarily long
      
      # Take screenshot after execution
      self.take_screenshot(f"after_cli_{len(self.results)}.png")
      
      # Verify output if expected_output is provided
      output_verified = True
      output_match = None
      if expected_output is not None:
        # Check if expected output is in stdout
        output_verified = expected_output in stdout
        output_match = expected_output if output_verified else None
        
        if not output_verified:
            self.error_logs.append(f"Output verification failed for '{command}'")
            self.error_logs.append(f"Expected: '{expected_output}'")
            self.error_logs.append(f"Got: '{stdout}'")
      
      # Record result
      result = {
        "command": command,
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "success": process.returncode == 0 and output_verified,
        "output_verified": output_verified,
        "expected_output": expected_output,
        "output_match": output_match
      }
      
      self.results.append(result)
      
      if process.returncode != 0:
        self.error_logs.append(f"Command '{command}' failed with exit code {process.returncode}")
        self.error_logs.append(f"Error: {stderr}")
      
      return result
      
    except subprocess.TimeoutExpired:
      self.error_logs.append(f"Command '{command}' timed out after {wait_time}s")
      self.take_screenshot(f"timeout_cli_{len(self.results)}.png")
      result = {
        "command": command,
        "exit_code": -1,
        "stdout": "",
        "stderr": f"Timeout after {wait_time}s",
        "success": False,
        "output_verified": False
      }
      self.results.append(result)
      return result
    
    except Exception as e:
      self.error_logs.append(f"Error executing '{command}': {e}")
      self.take_screenshot(f"error_cli_{len(self.results)}.png")
      result = {
        "command": command,
        "exit_code": -2,
        "stdout": "",
        "stderr": str(e),
        "success": False,
        "output_verified": False
      }
      self.results.append(result)
      return result
  
  def execute_input(self, action_type, parameters, wait_time=1):
    """Execute mouse or keyboard input"""
    import pyautogui
    import time
    
    try:
      # Take screenshot before action
      self.take_screenshot(f"before_input_{len(self.results)}.png")
      
      # Perform the action
      if action_type == "mouse":
        x, y, click_type = parameters
        
        # Move mouse
        pyautogui.moveTo(x, y)
        
        # Perform click
        if click_type == "click":
          pyautogui.click(x=x, y=y)
        elif click_type == "double":
          pyautogui.doubleClick(x=x, y=y)
        elif click_type == "right":
          pyautogui.rightClick(x=x, y=y)
        elif click_type == "drag":
          end_x, end_y = parameters[3:5]
          pyautogui.dragTo(end_x, end_y, duration=0.5)
      
      elif action_type == "keyboard":
        # Type text or special key
        if isinstance(parameters, list):
          for key in parameters:
            pyautogui.press(key)
        else:
          pyautogui.write(parameters)
          
      # Wait specified time
      time.sleep(wait_time)
      
      # Take screenshot after action
      self.take_screenshot(f"after_input_{len(self.results)}.png")
      
      # Record result
      result = {
        "action_type": action_type,
        "parameters": parameters,
        "success": True
      }
      self.results.append(result)
      return result
      
    except Exception as e:
      self.error_logs.append(f"Input action error: {e}")
      self.take_screenshot(f"error_input_{len(self.results)}.png")
      result = {
        "action_type": action_type,
        "parameters": parameters,
        "success": False,
        "error": str(e)
      }
      self.results.append(result)
      return result
  
  def execute_all_actions(self):
    """Execute all queued actions"""
    for i, action in enumerate(self.actions):
      action_type = action[0]
      
      print(f"Executing action {i+1}/{len(self.actions)}: {action_type}")
      
      if action_type == "cli":
        _, command, input_text, wait_time, expected_output = action
        result = self.execute_cli(command, input_text, wait_time, expected_output)
        
        # Detailed reporting for CLI action failures
        if not result["success"]:
          print("\n=== CLI ACTION FAILED ===")
          print(f"Command: {command}")
          if input_text:
            print(f"Input provided: {input_text[:100]}{'...' if len(input_text) > 100 else ''}")
          print(f"Exit code: {result['exit_code']}")
          
          if expected_output is not None and not result.get('output_verified', True):
            print("\n--- OUTPUT VERIFICATION FAILURE ---")
            print(f"Expected output: '{expected_output}'")
            print(f"Actual output: '{result['stdout'][:200]}{'...' if len(result['stdout']) > 200 else ''}'")
          
          if result['stderr']:
            print(f"Error: {result['stderr']}")
      
      elif action_type == "input":
        _, input_type, parameters, wait_time = action
        result = self.execute_input(input_type, parameters, wait_time)
        
      # Detailed reporting for input action failures
        if not result["success"]:
          print(f"Input action failed: {input_type} {parameters}")
        
      # Stop on first failure
      if not self.results[-1]["success"]:
        print(f"Action {i+1} failed. Stopping execution.")
        break
    
    return self.generate_report()
  
  def cleanup(self, keep_error_files=False):
    """Clean up temporary files"""
    import os
    
    if keep_error_files and any(not result["success"] for result in self.results):
      print("Keeping temporary files due to errors")
      return
      
    for file_path in self.temp_files:
      try:
        if os.path.exists(file_path):
          os.remove(file_path)
      except Exception as e:
        print(f"Error cleaning up {file_path}: {e}")
  
  def generate_report(self):
    """Generate a comprehensive test report"""
    success_count = sum(1 for result in self.results if result["success"])
    
    report = {
      "total_actions": len(self.actions),
      "successful_actions": success_count,
      "failed_actions": len(self.results) - success_count,
      "success_rate": f"{success_count/len(self.results)*100:.1f}%" if self.results else "N/A",
      "results": self.results,
      "error_logs": self.error_logs,
      "screenshots": self.screenshots
    }
    
    # Look for suspected failure points
    if report["failed_actions"] > 0:
      first_failure = next((i for i, r in enumerate(self.results) if not r["success"]), -1)
      if first_failure >= 0:
        report["first_failure"] = {
          "action_index": first_failure,
          "action": self.actions[first_failure],
          "result": self.results[first_failure]
        }
    
    return report
  
  def find_source_file_for_error(self, error_text):
    """Try to identify the source file involved in an error"""
    import re
    import os
    
    # Common patterns for file paths in error messages
    patterns = [
      r'File "([^"]+)"',
      r'at ([^:]+):\d+',
      r'from ([^:]+):\d+',
      r'([^:\s]+\.py):\d+',
      r'([^:\s]+\.(js|cpp|c|h|java|ts)):\d+'
    ]
    
    for pattern in patterns:
      matches = re.findall(pattern, error_text)
      if matches:
        for match in matches:
          if isinstance(match, tuple):
            match = match[0]
          if os.path.exists(match):
            return match
    
    return None

  def _format_test_results(self, test_results):
    """Format test results as text for the reviewer"""
    output = []
    
    output.append(f"Test Summary: {test_results['successful_actions']}/{test_results['total_actions']} tests passed")
    output.append(f"Success Rate: {test_results['success_rate']}")
    
    if test_results['error_logs']:
        output.append("\nERROR LOGS:")
        for error in test_results['error_logs']:
            output.append(f"- {error}")
    
    output.append("\nTEST RESULTS:")
    for i, result in enumerate(test_results['results']):
        output.append(f"\nTest {i+1}:")
        if 'command' in result:
            output.append(f"Command: {result['command']}")
            output.append(f"Exit Code: {result['exit_code']}")
            if 'expected_output' in result and result['expected_output']:
                output.append(f"Expected Output: '{result['expected_output']}'")
                output.append(f"Output Verified: {result['output_verified']}")
            if result['stdout']:
                output.append(f"Output: {result['stdout'][:500]}")  # Limit output size
            if result['stderr']:
                output.append(f"Error: {result['stderr'][:500]}")  # Limit error size
        elif 'action_type' in result:
            output.append(f"Action: {result['action_type']} - {result['parameters']}")
        output.append(f"Success: {result['success']}")
            
    return "\n".join(output)
  
  def print_test_results(self, test_results=None):
    """Print detailed information about CLI actions, expected results, and test failures
    
    Args:
      test_results: Test results dictionary (if None, uses the last run results)
    """
    if test_results is None:
      test_results = self.generate_report()
    
    print("\n" + "="*80)
    print(f"TEST EXECUTION SUMMARY")
    print("="*80)
    print(f"Total Actions: {test_results['total_actions']}")
    print(f"Passed: {test_results['successful_actions']} | Failed: {test_results['failed_actions']}")
    print(f"Success Rate: {test_results['success_rate']}")
    print("="*80)
    
    # Print CLI actions and their expected results
    print("\nCLI ACTIONS & EXPECTED RESULTS:")
    print("-"*80)
    for i, action in enumerate(self.actions):
      if action[0] == "cli":
        _, command, input_text, wait_time, expected_output = action
        print(f"[{i+1}] Command: {command}")
        if input_text:
          print(f"    Input: {input_text.strip()[:60]}{'...' if len(input_text) > 60 else ''}")
        print(f"    Wait time: {wait_time}s")
        if expected_output:
          print(f"    Expected output: '{expected_output}'")
        print()
    
    # Print test failures with expected vs actual output
    if test_results['failed_actions'] > 0:
      print("\nFAILED TESTS:")
      print("-"*80)
      for i, result in enumerate(test_results['results']):
        if not result.get('success', False):
          print(f"\n[Test {i+1}] Failed")
          if 'command' in result:
            print(f"Command: {result['command']}")
            print(f"Exit Code: {result['exit_code']}")
            
            # Show expected vs actual output for output verification failures
            if 'output_verified' in result and not result['output_verified']:
              print("\nOUTPUT VERIFICATION FAILED:")
              print(f"  Expected: '{result.get('expected_output', '')}'")
              actual = result.get('stdout', '')
              print(f"  Actual  : '{actual[:200]}{'...' if len(actual) > 200 else ''}'")
            
            # Show stderr for command failures
            if result['stderr']:
              print("\nERROR OUTPUT:")
              print(f"{result['stderr'][:500]}{'...' if len(result['stderr']) > 500 else ''}")
          
          elif 'action_type' in result:
            print(f"Action Type: {result['action_type']}")
            print(f"Parameters: {result['parameters']}")
            if 'error' in result:
              print(f"Error: {result['error']}")
          print("-"*40)
    else:
      print("\nAll tests passed successfully!")
    
    print("\n" + "="*80)
    return test_results
    
  def add_test_batch(self, test_cases):
    """Add a batch of test cases at once
    
    Args:
      test_cases: List of test case tuples (command, input_text, wait_time, expected_output)
    
    Returns:
      self for method chaining
    """
    for test_case in test_cases:
      if len(test_case) == 4:  # Unpack only if the format is correct
        command, input_text, wait_time, expected_output = test_case
        self.add_cli_action(command, input_text, wait_time, expected_output)
    
    return self
  
  def execute_all_actions_with_report(self, stop_on_failure=True, detailed_report=True):
    """Execute all queued actions and generate a detailed report
    
    Args:
      stop_on_failure: Whether to stop after first failure
      detailed_report: Whether to generate a detailed report with suggested fixes
      
    Returns:
      Test report with results and suggested fixes
    """
    results = self.execute_all_actions()
    
    if detailed_report and results['failed_actions'] > 0:
      results['suggested_fixes'] = self.suggest_fixes(results)
      
    return results
  
  def suggest_fixes(self, test_results):
    """Suggest fixes for failed tests based on common patterns
    
    Args:
      test_results: Test results from execute_all_actions
      
    Returns:
      List of suggested fixes with rationale
    """
    suggestions = []
    
    # Analyze failed tests
    for i, result in enumerate(test_results['results']):
      if not result.get('success', False):
        suggestion = {'test_index': i}
        
        if 'command' in result:
          suggestion['command'] = result['command']
          
          # Look at error message to determine possible fix
          if result.get('stderr'):
            error_msg = result['stderr']
            
            # Common Python errors
            if "ModuleNotFoundError" in error_msg:
              module = error_msg.split("'")[1] if "'" in error_msg else "unknown"
              suggestion['issue'] = f"Missing module: {module}"
              suggestion['fix'] = f"Install the required module: pip install {module}"
              suggestion['fix_type'] = 'dependency'
            
            elif "SyntaxError" in error_msg:
              suggestion['issue'] = "Syntax error in code"
              suggestion['fix'] = "Fix the syntax error highlighted in the error message"
              suggestion['fix_type'] = 'code'
              
              # Try to identify the file with the error
              source_file = self.find_source_file_for_error(error_msg)
              if source_file:
                suggestion['file'] = source_file
            
            elif "TypeError" in error_msg:
              suggestion['issue'] = "Type error in code"
              suggestion['fix'] = "Ensure correct types are used in operations"
              suggestion['fix_type'] = 'code'
            
            elif "ValueError" in error_msg:
              if "invalid literal for int()" in error_msg or "could not convert string to float" in error_msg:
                suggestion['issue'] = "Invalid conversion from string to number"
                suggestion['fix'] = "Add validation for numeric input before conversion"
                suggestion['fix_type'] = 'code'
            
            elif "IndexError" in error_msg or "KeyError" in error_msg:
              suggestion['issue'] = "Access to non-existent index or key"
              suggestion['fix'] = "Add bounds checking or key existence verification"
              suggestion['fix_type'] = 'code'
            
            elif "ZeroDivisionError" in error_msg:
              suggestion['issue'] = "Division by zero"
              suggestion['fix'] = "Add check to prevent division by zero"
              suggestion['fix_type'] = 'code'
          
          # Look at output verification failures
          elif 'output_verified' in result and not result['output_verified']:
            expected = result.get('expected_output', '')
            actual = result.get('stdout', '')
            
            suggestion['issue'] = "Output verification failed"
            suggestion['fix'] = f"Expected '{expected}' but got '{actual[:50]}...'" if len(actual) > 50 else f"Expected '{expected}' but got '{actual}'"
            suggestion['fix_type'] = 'output'
            
        elif 'action_type' in result:
          suggestion['action_type'] = result['action_type']
          suggestion['parameters'] = result['parameters']
          
          if 'error' in result:
            suggestion['issue'] = f"Input action failed: {result['error']}"
            
            # Common UI interaction errors
            if "failed to locate" in result['error'].lower():
              suggestion['fix'] = "Element not found on screen, check UI state or coordinates"
              suggestion['fix_type'] = 'ui'
            elif "permission" in result['error'].lower():
              suggestion['fix'] = "Permissions issue, ensure the tool has necessary access"
              suggestion['fix_type'] = 'system'
            else:
              suggestion['fix'] = "Check input action parameters and timing"
              suggestion['fix_type'] = 'input'
        
        suggestions.append(suggestion)
    
    return suggestions
  
  def run_test_suite(self, test_suite_name, test_cases):
    """Run a named test suite with the given test cases
    
    Args:
      test_suite_name: Name of the test suite for reporting
      test_cases: List of test case tuples
      
    Returns:
      Test results for the suite
    """
    print(f"Running test suite: {test_suite_name}")
    
    # Reset test state
    self.actions = []
    self.results = []
    
    # Add all test cases
    self.add_test_batch(test_cases)
    
    # Execute tests
    results = self.execute_all_actions_with_report()
    
    # Add test suite info to results
    results['test_suite_name'] = test_suite_name
    
    return results
    
  def generate_tests_with_ollama(self, file_path: str, num_tests: int = 5) -> List[Dict[str, Any]]:
    """Generate test cases for a given file using Ollama
    
    Args:
      file_path: Path to the file to generate tests for
      num_tests: Number of test cases to generate
      
    Returns:
      List of test case dictionaries with command, input, and expected output
    """
    try:
        # Read the file content
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        file_name = os.path.basename(file_path)
        _, file_ext = os.path.splitext(file_path)
        
        # Detect language from file extension
        language = "unknown"
        for ext, cmd_template in self.language_commands.items():
            if file_ext.lower() == ext:
                language = ext[1:]  # Remove the dot from extension
                break
        
        # Get the appropriate run command for this file type
        run_command_template = self.get_run_command(file_path)
        # Replace filepath with file_name to use relative path in the commands
        run_command = run_command_template.replace(file_path, file_name)
        
        # Construct prompt for test generation with improved instructions for CLI command safety
        prompt = f"""You are an expert test engineer. Generate {num_tests} test cases for the following {language} code.
For each test case, provide:
1. A descriptive test name
2. The command to run (use this command as a base: {run_command})
3. The input to provide to the program (as a string with newlines represented as \\n)
4. The expected output to verify against
5. A brief description of what the test is checking

IMPORTANT: Ensure all commands are properly formatted and escaped:
- Avoid unbalanced quotes or parentheses
- Use proper escaping for special characters
- Avoid shell redirection unless necessary (>, <, |)
- Use simple commands that don't require complex shell features
- If input has special characters, escape them properly

Here is the code:

```{language}
{file_content}
```

Format your response as JSON like this:
{{
  "test_cases": [
    {{
      "name": "test_case_name",
      "command": "{run_command}",
      "input": "input\\nwith\\nnewlines",
      "wait_time": 3,
      "expected_output": "Expected output",
      "description": "Description of what this test checks"
    }},
    ...
  ]
}}

Only include the JSON in your response, nothing else."""
        
        # Call Ollama API
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "temperature": 0.3,  # Lower temperature for more consistent test generation
            "stream": False
        }
        
        print(f"Requesting test generation from Ollama ({self.ollama_model})...")
        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json=payload
        )
        
        if response.status_code != 200:
            print(f"Error: Ollama API returned status code {response.status_code}")
            return []
        
        result = response.json()
        generated_text = result.get("response", "")
        
        # Extract JSON data from response
        try:
            # Find JSON in the response (it might be wrapped in markdown code blocks)
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```|```\s*([\s\S]*?)\s*```|(\{[\s\S]*\})', generated_text)
            
            if json_match:
                json_str = next(group for group in json_match.groups() if group)
                test_data = json.loads(json_str)
            else:
                # Try to parse the whole response as JSON
                test_data = json.loads(generated_text)
            
            # Convert to our format and add tests
            test_cases = []
            for tc in test_data.get("test_cases", []):
                # Validate the command before adding it
                command = tc.get("command", run_command)
                if not self.validate_command(command):
                    print(f"Skipping invalid test command: {command}")
                    continue
                    
                test_cases.append({
                    "name": tc.get("name", "Unnamed test"),
                    "command": command,
                    "input": tc.get("input", ""),
                    "wait_time": tc.get("wait_time", 3),
                    "expected_output": tc.get("expected_output", ""),
                    "description": tc.get("description", "")
                })
            
            print(f"Successfully generated {len(test_cases)} test cases")
            return test_cases
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Ollama response: {e}")
            print(f"Raw response: {generated_text[:500]}...")
            return []
            
    except Exception as e:
        print(f"ERROR: Failed to generate tests: {e}")
        return []
      
  def add_generated_tests(self, file_path: str, num_tests: int = 5) -> bool:
    """Generate and add tests for a file to the test queue
    
    Args:
      file_path: Path to the file to generate tests for
      num_tests: Number of test cases to generate
      
    Returns:
      True if successful, False otherwise
    """
    test_cases = self.generate_tests_with_ollama(file_path, num_tests)
    
    if not test_cases:
      return False
      
    print(f"Adding {len(test_cases)} generated tests to the queue:")
    for tc in test_cases:
      print(f"- {tc['name']}: {tc['description']}")
      self.add_cli_action(
        tc['command'],
        tc['input'],
        tc['wait_time'],
        tc['expected_output']
      )
    
    return True

  def get_run_command(self, filepath: str) -> str:
    """Get the appropriate run command for a file based on its extension
    
    Args:
        filepath: Path to the file to run
        
    Returns:
        A command string to execute the file
    """
    # Get file extension, basename and directory path
    _, ext = os.path.splitext(filepath)
    basename = os.path.basename(filepath)
    basename_no_ext = os.path.splitext(basename)[0]
    dirpath = os.path.dirname(filepath)
    
    # If empty directory path, use current directory
    if not dirpath:
      dirpath = "."
      
    # Get classname for Java files (assuming conventional naming)
    classname = basename_no_ext
    
    # Check if we have a predefined command for this extension
    if ext.lower() in self.language_commands:
      command_template = self.language_commands[ext.lower()]
      return command_template.format(
        filepath=filepath,
        basename=basename_no_ext,
        dirpath=dirpath,
        classname=classname
      )
    
    # If no predefined command, try to determine it using LLM
    return self.query_llm_for_run_command(filepath, ext)
  
  def query_llm_for_run_command(self, filepath: str, ext: str) -> str:
    """Query the LLM to determine how to run a file with an unknown extension
    
    Args:
        filepath: Path to the file to run
        ext: File extension
        
    Returns:
        A command string to execute the file
    """
    try:
      prompt = f"""I need to execute a file with the extension '{ext}'. 
What is the appropriate command-line command to run this type of file?
Return just the command with {{filepath}} as a placeholder for the file path.
If compilation is needed first, include that in the command (using && for sequential commands).
For example, for a Python file you would return: "python {{filepath}}"
For a C file you might return: "gcc {{filepath}} -o {{basename}} && ./{{basename}}"
"""
      
      # Call Ollama API
      payload = {
        "model": self.ollama_model,
        "prompt": prompt,
        "temperature": 0.3,
        "stream": False
      }
      
      print(f"Querying LLM for how to run files with extension '{ext}'...")
      response = requests.post(
        f"{self.ollama_base_url}/api/generate",
        json=payload
      )
      
      if response.status_code != 200:
        print(f"Error: Ollama API returned status code {response.status_code}")
        # Fall back to just using the filepath directly as a command if LLM fails
        return filepath
      
      result = response.json()
      command = result.get("response", "").strip()
      
      # Basic validation - the command should contain {filepath}
      if "{filepath}" not in command:
        # If the LLM didn't use the placeholder, add it
        command = command + " {filepath}"
      
      # Format the command
      basename = os.path.splitext(os.path.basename(filepath))[0]
      dirpath = os.path.dirname(filepath) or "."
      
      formatted_command = command.format(
        filepath=filepath,
        basename=basename,
        dirpath=dirpath
      )
      
      # Cache this command for future use
      self.language_commands[ext.lower()] = command
      
      print(f"LLM suggested command for '{ext}' files: {formatted_command}")
      return formatted_command
      
    except Exception as e:
      print(f"Error querying LLM for run command: {e}")
      # Fall back to just trying to execute the file directly
      return f"./{filepath}"