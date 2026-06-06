"""
CLI Interface - Terminal user interface for GitForge-CLI.
终端交互界面。
"""

import os
import sys
import argparse
from typing import Optional, List

from ..core.git_analyzer import GitAnalyzer
from ..core.commit_generator import CommitGenerator
from ..core.changelog_generator import ChangelogGenerator
from ..core.llm_client import GLMClient


class CLIInterface:
    """Command-line interface for GitForge."""

    def __init__(self):
        self.git = GitAnalyzer()
        self.commit_gen = CommitGenerator()
        self.changelog_gen = ChangelogGenerator()

    def print(self, text: str = "") -> None:
        """Print text."""
        print(text)

    def print_header(self, title: str) -> None:
        """Print a header section."""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")

    def print_success(self, message: str) -> None:
        """Print success message."""
        print(f"✅ {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        print(f"❌ {message}", file=sys.stderr)

    def print_info(self, message: str) -> None:
        """Print info message."""
        print(f"ℹ️  {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"⚠️  {message}")

    def show_welcome(self) -> None:
        """Display welcome message."""
        welcome = """
🔨 GitForge-CLI v1.0.0
   Lightweight Terminal Git Workflow Intelligent Enhancement Engine
   轻量级终端Git工作流智能增强引擎

   Commands:
     commit           - Generate AI commit message from staged changes
     commit-batch     - Generate multiple commit message options
     changelog        - Generate CHANGELOG.md from commit history
     validate <msg>   - Validate a commit message
     status           - Show repository status
     config           - Show configuration
     help             - Show this help message
     exit             - Exit GitForge

   Environment:
     GLM_API_KEY      - Your GLM-5.1 API key (required for AI generation)
        """
        print(welcome)

    def cmd_commit(self, language: str = "en", custom_prompt: Optional[str] = None, auto_commit: bool = False) -> None:
        """Handle commit command."""
        if not self.git.is_git_repo():
            self.print_error("Not a git repository. Run 'git init' first.")
            return

        if not self.git.has_staged_changes():
            self.print_warning("No staged changes found.")
            self.print_info("Stage files with: git add <files>")
            return

        # Show changed files
        files = self.git.get_changed_files(staged=True)
        self.print_info(f"Staged files ({len(files)}):")
        for f in files:
            print(f"  • {f}")

        self.print_info("Generating commit message...")
        result = self.commit_gen.generate(language=language, custom_prompt=custom_prompt)

        if result.get("error"):
            self.print_error(result["error"])
            return

        # Display result
        self.print_header("Generated Commit Message")
        print(result["message"])

        # Show validation
        validation = self.commit_gen.validate_message(result["message"])
        if validation["warnings"]:
            self.print_warning("Suggestions:")
            for w in validation["warnings"]:
                print(f"  • {w}")

        # Ask for confirmation
        if auto_commit:
            confirmed = True
        else:
            try:
                response = input("\nUse this message? [Y/n/e(dit)/c(ancel)]: ").strip().lower()
                confirmed = response in ("", "y", "yes")
                if response in ("e", "edit"):
                    # Open editor
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
                        f.write(result["message"])
                        temp_path = f.name
                    editor = os.environ.get("EDITOR", "nano")
                    os.system(f"{editor} {temp_path}")
                    with open(temp_path, "r") as f:
                        new_message = f.read().strip()
                    os.unlink(temp_path)
                    if new_message:
                        result["message"] = new_message
                        confirmed = True
                elif response in ("c", "cancel"):
                    self.print_info("Commit cancelled.")
                    return
            except (EOFError, KeyboardInterrupt):
                print()
                return

        if confirmed:
            if self.git.commit(result["message"]):
                self.print_success("Commit created successfully!")
            else:
                self.print_error("Failed to create commit.")
        else:
            self.print_info("Commit cancelled.")

    def cmd_commit_batch(self, count: int = 3, language: str = "en") -> None:
        """Handle commit-batch command."""
        if not self.git.is_git_repo():
            self.print_error("Not a git repository.")
            return

        if not self.git.has_staged_changes():
            self.print_warning("No staged changes found.")
            return

        self.print_info(f"Generating {count} commit message options...")
        suggestions = self.commit_gen.generate_batch(count=count, language=language)

        if not suggestions:
            self.print_error("Failed to generate suggestions.")
            return

        self.print_header("Commit Message Options")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\nOption {i}:")
            print(f"  {suggestion['message']}")
            print(f"  Type: {suggestion['type'] or 'N/A'}")
            if suggestion['scope']:
                print(f"  Scope: {suggestion['scope']}")

        try:
            choice = input("\nSelect option (1-{}), or c(ancel): ".format(len(suggestions))).strip()
            if choice.lower() in ("c", "cancel"):
                self.print_info("Cancelled.")
                return
            idx = int(choice) - 1
            if 0 <= idx < len(suggestions):
                if self.git.commit(suggestions[idx]["message"]):
                    self.print_success("Commit created!")
                else:
                    self.print_error("Failed to create commit.")
            else:
                self.print_error("Invalid selection.")
        except (ValueError, EOFError, KeyboardInterrupt):
            self.print_info("Cancelled.")

    def cmd_changelog(
        self,
        output: str = "CHANGELOG.md",
        version: Optional[str] = None,
        since: Optional[str] = None,
        language: str = "en",
    ) -> None:
        """Handle changelog command."""
        if not self.git.is_git_repo():
            self.print_error("Not a git repository.")
            return

        self.print_info("Generating changelog...")
        result = self.changelog_gen.generate(
            since_tag=since,
            version=version,
            language=language,
        )

        if result.get("error"):
            self.print_error(result["error"])
            return

        self.print_header("Generated Changelog")
        print(result["changelog"])

        # Write to file
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result["changelog"])
            self.print_success(f"Changelog saved to {output}")
        except IOError as e:
            self.print_error(f"Failed to write file: {e}")

    def cmd_validate(self, message: str) -> None:
        """Handle validate command."""
        validation = self.commit_gen.validate_message(message)
        
        self.print_header("Commit Message Validation")
        print(f"Message: {message}")
        print(f"Valid: {'✅ Yes' if validation['valid'] else '❌ No'}")
        
        if validation["issues"]:
            self.print_error("Issues:")
            for issue in validation["issues"]:
                print(f"  • {issue}")
        
        if validation["warnings"]:
            self.print_warning("Warnings:")
            for warning in validation["warnings"]:
                print(f"  • {warning}")
        
        if validation["valid"] and not validation["warnings"]:
            self.print_success("Perfect commit message!")

    def cmd_status(self) -> None:
        """Handle status command."""
        if not self.git.is_git_repo():
            self.print_error("Not a git repository.")
            return

        info = self.git.get_repo_info()
        self.print_header("📊 Repository Status")
        
        for key, value in info.items():
            print(f"  {key}: {value}")

        staged = self.git.has_staged_changes()
        unstaged = self.git.has_unstaged_changes()
        
        print(f"\n  Staged changes: {'Yes' if staged else 'No'}")
        print(f"  Unstaged changes: {'Yes' if unstaged else 'No'}")

        if staged:
            files = self.git.get_changed_files(staged=True)
            print(f"\n  Staged files ({len(files)}):")
            for f in files:
                print(f"    • {f}")

    def cmd_config(self) -> None:
        """Handle config command."""
        self.print_header("⚙️ Configuration")
        
        llm_info = self.commit_gen.llm_client.get_model_info()
        print(f"LLM Model: {llm_info['model']}")
        print(f"API Configured: {'✅ Yes' if llm_info['configured'] == 'True' else '❌ No'}")
        print(f"Mock Mode: {'Yes' if llm_info['mock_mode'] == 'True' else 'No'}")
        
        if llm_info['configured'] != 'True':
            self.print_info("\nTo configure API key:")
            print("  export GLM_API_KEY='your-api-key'")

    def interactive_shell(self) -> None:
        """Run interactive shell."""
        self.show_welcome()

        while True:
            try:
                user_input = input("\n[gitforge]> ").strip()
                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if cmd in ("exit", "quit", "q"):
                    self.print_info("Goodbye! 👋")
                    break
                elif cmd == "help":
                    self.show_welcome()
                elif cmd in ("commit", "c"):
                    self.cmd_commit()
                elif cmd == "commit-batch":
                    count = int(arg) if arg.isdigit() else 3
                    self.cmd_commit_batch(count=count)
                elif cmd in ("changelog", "cl"):
                    self.cmd_changelog()
                elif cmd == "validate":
                    if not arg:
                        self.print_error("Usage: validate <commit-message>")
                        continue
                    self.cmd_validate(arg)
                elif cmd == "status":
                    self.cmd_status()
                elif cmd == "config":
                    self.cmd_config()
                else:
                    self.print_error(f"Unknown command: {cmd}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                break
            except Exception as e:
                self.print_error(f"Error: {str(e)}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="🔨 GitForge-CLI - Git Workflow Intelligent Enhancement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitforge                          # Start interactive shell
  gitforge commit                   # Generate commit message
  gitforge commit --lang zh         # Generate in Chinese
  gitforge changelog                # Generate changelog
  gitforge validate "feat: add auth" # Validate message
        """,
    )
    parser.add_argument("--api-key", help="GLM API key")
    parser.add_argument("--lang", default="en", choices=["en", "zh", "zh-tw"], help="Output language")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Generate commit message")
    commit_parser.add_argument("--auto", action="store_true", help="Auto-commit without confirmation")
    commit_parser.add_argument("--prompt", help="Custom prompt context")
    commit_parser.add_argument("--batch", action="store_true", help="Generate multiple options")

    # Changelog command
    changelog_parser = subparsers.add_parser("changelog", help="Generate changelog")
    changelog_parser.add_argument("--output", default="CHANGELOG.md", help="Output file path")
    changelog_parser.add_argument("--version", help="Version number")
    changelog_parser.add_argument("--since", help="Generate since tag")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate commit message")
    validate_parser.add_argument("message", help="Commit message to validate")

    # Status command
    subparsers.add_parser("status", help="Show repository status")

    # Config command
    subparsers.add_parser("config", help="Show configuration")

    # Shell command
    subparsers.add_parser("shell", help="Start interactive shell")

    args = parser.parse_args()

    # Set API key if provided
    if args.api_key:
        os.environ["GLM_API_KEY"] = args.api_key

    ui = CLIInterface()

    if not args.command:
        ui.interactive_shell()
        return

    if args.command == "commit":
        if args.batch:
            ui.cmd_commit_batch(language=args.lang)
        else:
            ui.cmd_commit(
                language=args.lang,
                custom_prompt=args.prompt,
                auto_commit=args.auto,
            )
    elif args.command == "changelog":
        ui.cmd_changelog(
            output=args.output,
            version=args.version,
            since=args.since,
            language=args.lang,
        )
    elif args.command == "validate":
        ui.cmd_validate(args.message)
    elif args.command == "status":
        ui.cmd_status()
    elif args.command == "config":
        ui.cmd_config()
    elif args.command == "shell":
        ui.interactive_shell()


if __name__ == "__main__":
    main()
