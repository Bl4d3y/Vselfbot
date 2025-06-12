import discord
import importlib
import pkgutil
from pathlib import Path
from collections import defaultdict

class SelfBot(discord.Client):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.command_registry = defaultdict(dict)
        self.dev_command_registry = defaultdict(dict)
        self.load_commands()

    def load_commands(self):
        cmd_dir = Path(__file__).parent.parent / "commands"
        for module_info in pkgutil.iter_modules([str(cmd_dir)]):
            module_name = module_info.name
            module = importlib.import_module(f"commands.{module_name}")
            module_header = module_name.replace("_", " ").title()

            if hasattr(module, "COMMANDS"):
                for name, value in module.COMMANDS.items():
                    if isinstance(value, tuple):
                        self.command_registry[module_header][name] = value
                    else:
                        self.command_registry[module_header][name] = (value, "No description")

            if hasattr(module, "DEV_COMMANDS"):
                for name, value in module.DEV_COMMANDS.items():
                    if isinstance(value, tuple):
                        self.dev_command_registry[module_header][name] = value
                    else:
                        self.dev_command_registry[module_header][name] = (value, "No description")

    async def on_ready(self):
        print(f"✅ Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        mentions_me = self.user in message.mentions

        if not is_dm and not mentions_me:
            return

        content = message.content
        if not is_dm:
            content = content.replace(f"<@{self.user.id}>", "").strip()

        if not content.startswith(self.config["PREFIX"]):
            return

        content = content[len(self.config["PREFIX"]):].strip()
        parts = content.split()
        if not parts:
            return

        cmd, *args = parts

        if cmd == "cmds":
            await self.show_command_pages(message, args)
            return

        for registry in (self.command_registry, self.dev_command_registry):
            for mod_cmds in registry.values():
                if cmd in mod_cmds:
                    return await mod_cmds[cmd][0](self, message, args)

    async def show_command_pages(self, message, args):
        is_dev = message.author.id in self.config["DEV_ID"]
        target = None
        page = 1

        if args:
            if args[0].lower() == "dev":
                if not is_dev:
                    return await message.channel.send("❌ You are not authorized to view dev commands.")
                target = "dev"
                if len(args) > 1 and args[1].isdigit():
                    page = int(args[1])
            elif args[0].isdigit():
                page = int(args[0])
            else:
                return await message.channel.send("❌ Invalid arguments. Use `!cmds [dev] [page]`")

        registry = self.dev_command_registry if target == "dev" else self.command_registry

        all_commands = []
        for module, cmds in sorted(registry.items()):
            all_commands.append((module, sorted([(cmd, desc) for cmd, (func, desc) in cmds.items()])))

        if not all_commands:
            return await message.channel.send("❌ No commands found.")

        per_page = 1
        total_pages = len(all_commands)

        if page < 1 or page > total_pages:
            return await message.channel.send(
                f"❌ Invalid page. Use `{self.config['PREFIX']}cmds {target or ''} 1-{total_pages}`."
            )

        module, cmds = all_commands[page - 1]
        prefix = self.config["PREFIX"]

        lines_preview = [
            f"🔹 {prefix}{cmd} - {desc or 'No description'}"
            for cmd, desc in cmds
        ]
        max_line_length = max(len(line) for line in lines_preview)
        box_width = max(50, max_line_length + 6)

        lines = ["```"]
        title = f" MODULE: {module.upper()} "
        lines.append("┌" + title.center(box_width - 2, "─") + "┐")
        lines.append("│" + " " * (box_width - 2) + "│")
        for cmd, desc in cmds:
            cmd_line = f"🔹 {prefix}{cmd}"
            desc_text = desc or "No description"
            spacing = box_width - len(cmd_line) - len(desc_text) - 6
            lines.append(f"│  {cmd_line}{' ' * max(spacing, 1)}{desc_text}  │")
        lines.append("│" + " " * (box_width - 2) + "│")
        lines.append("└" + f" Page {page}/{total_pages} ".center(box_width - 2, "─") + "┘")
        lines.append("```")

        await message.channel.send("\n".join(lines))
