"""
Beautiful menu system for DeepCLI
"""

from typing import List, Optional, Callable, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich import box
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import asyncio


class MenuItem:
    """Represents a menu item"""
    def __init__(
        self,
        key: str,
        title: str,
        description: str,
        action: Optional[Callable] = None,
        icon: str = "•",
        color: str = "cyan"
    ):
        self.key = key
        self.title = title
        self.description = description
        self.action = action
        self.icon = icon
        self.color = color


class MenuSystem:
    """Beautiful menu system for DeepCLI"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.menu_stack: List[str] = []
        self.menus: Dict[str, List[MenuItem]] = {}
        self._setup_menus()
    
    def _setup_menus(self):
        """Setup all menus"""
        # Main menu
        self.menus["main"] = [
            MenuItem(
                "1", "💬 Chat Assistant",
                "Interactive chat with DeepSeek AI",
                icon="💬",
                color="cyan"
            ),
            MenuItem(
                "2", "🧑‍💻 Coder Agent",
                "AI-powered coding assistant that can write and execute code",
                icon="🧑‍💻",
                color="green"
            ),
            MenuItem(
                "3", "🧠 Memory Bank",
                "Manage persistent memories and context",
                icon="🧠",
                color="yellow"
            ),
            MenuItem(
                "4", "🛠️ Tools & Commands",
                "Access specialized tools and slash commands",
                icon="🛠️",
                color="blue"
            ),
            MenuItem(
                "5", "📊 Analytics",
                "View usage statistics and performance metrics",
                icon="📊",
                color="magenta"
            ),
            MenuItem(
                "6", "⚙️ Settings",
                "Configure DeepCLI preferences",
                icon="⚙️",
                color="white"
            ),
            MenuItem(
                "0", "👋 Exit",
                "Exit DeepCLI",
                icon="👋",
                color="red"
            )
        ]
        
        # Coder Agent submenu
        self.menus["coder"] = [
            MenuItem(
                "1", "✨ Create Code",
                "Generate code from natural language description",
                icon="✨",
                color="green"
            ),
            MenuItem(
                "2", "🐛 Debug Code",
                "Analyze and fix code issues",
                icon="🐛",
                color="yellow"
            ),
            MenuItem(
                "3", "🔧 Refactor Code",
                "Improve and optimize existing code",
                icon="🔧",
                color="cyan"
            ),
            MenuItem(
                "4", "🧪 Generate Tests",
                "Create unit tests for your code",
                icon="🧪",
                color="magenta"
            ),
            MenuItem(
                "5", "📝 Document Code",
                "Generate documentation and comments",
                icon="📝",
                color="blue"
            ),
            MenuItem(
                "6", "🚀 Execute Code",
                "Run code in a sandboxed environment",
                icon="🚀",
                color="red"
            ),
            MenuItem(
                "7", "💡 Explain Code",
                "Get detailed explanations of code functionality",
                icon="💡",
                color="yellow"
            ),
            MenuItem(
                "8", "🔄 Convert Code",
                "Convert code between programming languages",
                icon="🔄",
                color="cyan"
            ),
            MenuItem(
                "0", "↩️ Back",
                "Return to main menu",
                icon="↩️",
                color="white"
            )
        ]
        
        # Tools submenu
        self.menus["tools"] = [
            MenuItem(
                "1", "🏗️ Architecture Design",
                "Design system architectures with AI guidance",
                icon="🏗️",
                color="cyan"
            ),
            MenuItem(
                "2", "🔍 Code Analysis",
                "Analyze codebases for patterns and issues",
                icon="🔍",
                color="yellow"
            ),
            MenuItem(
                "3", "🌐 API Builder",
                "Design and implement REST/GraphQL APIs",
                icon="🌐",
                color="green"
            ),
            MenuItem(
                "4", "🗄️ Database Designer",
                "Design database schemas and queries",
                icon="🗄️",
                color="blue"
            ),
            MenuItem(
                "5", "🎨 UI/UX Assistant",
                "Get help with frontend and design tasks",
                icon="🎨",
                color="magenta"
            ),
            MenuItem(
                "0", "↩️ Back",
                "Return to main menu",
                icon="↩️",
                color="white"
            )
        ]
    
    def _get_ascii_banner(self) -> Text:
        """Get the ASCII art banner with colors"""
        # ASCII art for "BASED GOD CODER CLI"
        ascii_art = """
██████╗  █████╗ ███████╗███████╗██████╗      ██████╗  ██████╗ ██████╗ 
██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗    ██╔════╝ ██╔═══██╗██╔══██╗
██████╔╝███████║███████╗█████╗  ██║  ██║    ██║  ███╗██║   ██║██║  ██║
██╔══██╗██╔══██║╚════██║██╔══╝  ██║  ██║    ██║   ██║██║   ██║██║  ██║
██████╔╝██║  ██║███████║███████╗██████╔╝    ╚██████╔╝╚██████╔╝██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝      ╚═════╝  ╚═════╝ ╚═════╝ 
                                                                        
         ██████╗ ██████╗ ██████╗ ███████╗██████╗      ██████╗██╗     ██╗
        ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║     ██║
        ██║     ██║   ██║██║  ██║█████╗  ██████╔╝    ██║     ██║     ██║
        ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗    ██║     ██║     ██║
        ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║    ╚██████╗███████╗██║
         ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═════╝╚══════╝╚═╝"""
        
        # Create colored text
        text = Text()
        lines = ascii_art.strip().split('\n')
        colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        
        for i, line in enumerate(lines):
            color = colors[i % len(colors)]
            text.append(line + '\n', style=f"bold {color}")
        
        return text
    
    def display_menu(self, menu_name: str = "main") -> None:
        """Display a beautiful menu"""
        self.console.clear()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=15),
            Layout(name="menu"),
            Layout(name="footer", size=3)
        )
        
        # Header with ASCII art
        header_content = Layout()
        header_content.split_column(
            Layout(self._get_ascii_banner(), size=12),
            Layout(Text("- made by @Lucariolucario55 on Telegram", style="dim italic"), size=1),
            Layout(Text("Powered by DeepSeek Models", style="dim"), size=1)
        )
        
        layout["header"].update(Panel(
            Align.center(header_content),
            border_style="blue",
            box=box.DOUBLE
        ))
        
        # Menu
        menu_items = self.menus.get(menu_name, self.menus["main"])
        
        table = Table(
            show_header=False,
            box=None,
            padding=(0, 2),
            expand=True
        )
        table.add_column("Key", style="bold", width=8)
        table.add_column("Option", style="bold")
        table.add_column("Description", style="dim")
        
        for item in menu_items:
            table.add_row(
                f"[{item.color}]{item.icon} [{item.key}][/{item.color}]",
                f"[{item.color}]{item.title}[/{item.color}]",
                item.description
            )
        
        menu_title = {
            "main": "🏠 Main Menu",
            "coder": "🧑‍💻 Coder Agent",
            "tools": "🛠️ Tools & Commands"
        }.get(menu_name, "Menu")
        
        layout["menu"].update(Panel(
            table,
            title=menu_title,
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        # Footer
        footer_text = "[dim]Use number keys to select • Type 'help' for assistance[/dim]"
        layout["footer"].update(Panel(
            Align.center(footer_text),
            border_style="dim",
            box=box.ROUNDED
        ))
        
        self.console.print(layout)
    
    def get_menu_choice(self, menu_name: str) -> Optional[MenuItem]:
        """Get user's menu choice"""
        menu_items = self.menus.get(menu_name, self.menus["main"])
        valid_keys = [item.key for item in menu_items]
        
        # Create completer
        completer = WordCompleter(
            valid_keys + ['help', 'exit'],
            ignore_case=True
        )
        
        while True:
            try:
                choice = prompt(
                    "\nYour choice: ",
                    completer=completer
                ).strip()
                
                if choice.lower() == 'help':
                    self.show_help()
                    continue
                elif choice.lower() == 'exit':
                    return None
                elif choice in valid_keys:
                    return next(item for item in menu_items if item.key == choice)
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")
            except (EOFError, KeyboardInterrupt):
                return None
    
    def show_help(self):
        """Show help information"""
        help_panel = Panel(
            "[cyan]Navigation:[/cyan]\n"
            "• Use number keys to select menu items\n"
            "• Press Enter to confirm your choice\n"
            "• Type 'exit' or press Ctrl+C to quit\n\n"
            "[cyan]Tips:[/cyan]\n"
            "• The Coder Agent can write, debug, and execute code\n"
            "• Memory Bank persists information across sessions\n"
            "• Use Tools for specialized development tasks",
            title="Help",
            border_style="yellow"
        )
        self.console.print(help_panel)
        input("\nPress Enter to continue...")
    
    async def run(self, start_menu: str = "main") -> Optional[MenuItem]:
        """Run the menu system"""
        current_menu = start_menu
        
        while True:
            self.display_menu(current_menu)
            choice = self.get_menu_choice(current_menu)
            
            if choice is None:
                return None
            
            # Handle navigation
            if choice.title == "↩️ Back":
                current_menu = "main"
            elif choice.key == "0" and current_menu == "main":
                return None
            elif choice.key == "2" and current_menu == "main":
                current_menu = "coder"
            elif choice.key == "4" and current_menu == "main":
                current_menu = "tools"
            else:
                return choice
    
    def show_loading(self, message: str = "Processing..."):
        """Show a loading animation"""
        with self.console.status(f"[cyan]{message}[/cyan]", spinner="dots"):
            import time
            time.sleep(1)  # Simulate processing


def create_main_menu() -> MenuSystem:
    """Create and return the main menu system"""
    return MenuSystem()


async def show_menu() -> Optional[MenuItem]:
    """Show the menu and get user's choice"""
    menu = create_main_menu()
    return await menu.run()