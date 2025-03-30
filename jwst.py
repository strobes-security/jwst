#!/usr/bin/env python3
"""
JWST (James Webb Screenshot Telescope) - A tool that analyzes screenshots of websites 
and identifies features using OpenAI's Vision capabilities.

Created as a modern version of the original Eyeballer tool, JWST uses advanced AI
to analyze website screenshots for penetration testing and security assessments.
"""

import os
import json
import argparse
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
import concurrent.futures

try:
    import requests
    from openai import OpenAI
    from tqdm import tqdm
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("Please install required packages: pip install openai requests tqdm rich")
    exit(1)

console = Console()

class JWST:
    """Class to analyze website screenshots using OpenAI's Vision capabilities."""
    
    SUPPORTED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.webp']
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize the JWST class.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: OpenAI model to use
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    @staticmethod
    def encode_image(image_path: str) -> str:
        """Encode image as base64 string.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_screenshot(self, image_path: str) -> Dict[str, Any]:
        """Analyze a screenshot using OpenAI's Vision capabilities.
        
        Args:
            image_path: Path to the screenshot
            
        Returns:
            Dictionary containing analysis results
        """
        base64_image = self.encode_image(image_path)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert web penetration tester analyzing website screenshots. "
                            "Identify the following features with yes/no and confidence score (0-1):\n"
                            "1. Is it an old-looking site? (outdated design, broken CSS, early 2000s look)\n"
                            "2. Is there a login page? (look for input fields, username/password prompts)\n"
                            "3. Is it a full webapp? (complex functionality beyond basic pages)\n"
                            "4. Is it a custom 404 page? (error page with custom styling)\n"
                            "5. Is it a parked domain? (placeholder page with ads, no real functionality)\n"
                            "6. What technologies are likely being used? (frameworks, CMS, etc.)\n"
                            "7. Are there any obvious security issues visible?\n\n"
                            "Format your response as a JSON with these keys: old_looking, login_page, webapp, "
                            "custom_404, parked_domain, technologies, security_issues. For each feature except "
                            "'technologies' and 'security_issues', include a boolean 'detected' field and a float "
                            "'confidence' field between 0 and 1. For 'technologies' and 'security_issues', provide lists."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this website screenshot and provide the requested information as JSON:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            console.print(f"[bold red]Error analyzing {image_path}: {str(e)}[/bold red]")
            return {
                "error": str(e),
                "filename": os.path.basename(image_path)
            }
    
    def analyze_directory(self, directory_path: str, output_format: str = "json", 
                          output_file: Optional[str] = None, max_workers: int = 4) -> Dict[str, Any]:
        """Analyze all screenshots in a directory.
        
        Args:
            directory_path: Path to directory containing screenshots
            output_format: Output format (json or table)
            output_file: Path to output file (if None, prints to stdout)
            max_workers: Maximum number of worker threads for parallel processing
            
        Returns:
            Dictionary mapping filenames to analysis results
        """
        # Find all image files in directory
        image_files = []
        for ext in self.SUPPORTED_EXTENSIONS:
            image_files.extend(list(Path(directory_path).glob(f"*{ext}")))
        
        if not image_files:
            console.print(f"[bold yellow]No supported image files found in {directory_path}[/bold yellow]")
            return {}
        
        console.print(f"[bold green]Found {len(image_files)} images to analyze[/bold green]")
        
        # Analyze images in parallel
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze_screenshot, str(img_file)): img_file 
                for img_file in image_files
            }
            
            for future in tqdm(concurrent.futures.as_completed(future_to_file), 
                              total=len(image_files), 
                              desc="Analyzing screenshots"):
                img_file = future_to_file[future]
                filename = os.path.basename(str(img_file))
                try:
                    results[filename] = future.result()
                except Exception as e:
                    console.print(f"[bold red]Error processing {filename}: {str(e)}[/bold red]")
                    results[filename] = {"error": str(e)}
        
        # Output results
        if output_format == "json":
            output_json = json.dumps(results, indent=2)
            if output_file:
                with open(output_file, "w") as f:
                    f.write(output_json)
                console.print(f"[bold green]Results saved to {output_file}[/bold green]")
            else:
                print(output_json)
        else:  # table format
            table = Table(title="Screenshot Analysis Results")
            table.add_column("Filename", style="cyan")
            table.add_column("Old Looking", style="magenta")
            table.add_column("Login Page", style="green")
            table.add_column("Webapp", style="blue")
            table.add_column("Custom 404", style="yellow")
            table.add_column("Parked", style="red")
            table.add_column("Technologies", style="bright_cyan")
            
            for filename, result in results.items():
                if "error" in result:
                    table.add_row(filename, f"ERROR: {result['error']}", "", "", "", "", "")
                    continue
                    
                tech_str = ", ".join(result.get("technologies", []))[:30]
                if len(tech_str) == 30:
                    tech_str += "..."
                    
                table.add_row(
                    filename,
                    f"{'✓' if result.get('old_looking', {}).get('detected', False) else '✗'} ({result.get('old_looking', {}).get('confidence', 0):.2f})",
                    f"{'✓' if result.get('login_page', {}).get('detected', False) else '✗'} ({result.get('login_page', {}).get('confidence', 0):.2f})",
                    f"{'✓' if result.get('webapp', {}).get('detected', False) else '✗'} ({result.get('webapp', {}).get('confidence', 0):.2f})",
                    f"{'✓' if result.get('custom_404', {}).get('detected', False) else '✗'} ({result.get('custom_404', {}).get('confidence', 0):.2f})",
                    f"{'✓' if result.get('parked_domain', {}).get('detected', False) else '✗'} ({result.get('parked_domain', {}).get('confidence', 0):.2f})",
                    tech_str
                )
            
            console.print(table)
            
            if output_file:
                with open(output_file, "w") as f:
                    f.write(json.dumps(results, indent=2))
                console.print(f"[bold green]Results also saved to {output_file}[/bold green]")
        
        return results


def main():
    """Main function to parse arguments and run the tool."""
    parser = argparse.ArgumentParser(description="JWST - Analyze website screenshots using OpenAI")
    parser.add_argument("directory", help="Directory containing website screenshots")
    parser.add_argument("--output", "-o", help="Output file (defaults to stdout)")
    parser.add_argument("--format", "-f", choices=["json", "table"], default="json",
                        help="Output format (json or table, defaults to json)")
    parser.add_argument("--api-key", help="OpenAI API key (defaults to OPENAI_API_KEY environment variable)")
    parser.add_argument("--model", default="gpt-4o-mini", 
                       help="OpenAI model to use (defaults to gpt-4o-mini)")
    parser.add_argument("--workers", type=int, default=4,
                       help="Maximum number of parallel workers (defaults to 4)")
    
    args = parser.parse_args()
    
    telescope = JWST(api_key=args.api_key, model=args.model)
    telescope.analyze_directory(args.directory, args.format, args.output, args.workers)


if __name__ == "__main__":
    main()
