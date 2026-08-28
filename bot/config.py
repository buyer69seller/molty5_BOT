"""
Configuration & constants for Molty Royale AI Agent.
All env vars loaded here. Never hardcode secrets.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

AGENT_NAME = "buy6_9sell"
BASE_API_URL = "https://cdn.clawroyale.ai/api"
WS_JOIN_URL = "wss://cdn.clawroyale.ai/ws/join"
API_KEY = "mr_live_5uFKB4CBSSaWNpbxpWaiyOteqg3JRhy2"

# ── Skill / API version ──────────────────────────────────────────────
SKILL_VERSION = "1.15.0"

# ── URLs ──────────────────────────────────────────────────────────────
API_BASE = "https://cdn.clawroyale.ai/api"
WS_URL = "wss://cdn.clawroyale.ai/ws/join"

# ── Economy constants (from economy.md) ───────────────────────────────
PAID_ENTRY_FEE_MOLTZ = 500
PAID_ENTRY_FEE_SMOLTZ = 500
FREE_ROOM_POOL = 1000
GUARDIAN_KILL_POOL_SHARE = 0.60  # 60%

# ── Rate limits ───────────────────────────────────────────────────────
REST_RATE_LIMIT = 300   # calls/min per IP
WS_RATE_LIMIT = 120     # messages/min per connection
COOLDOWN_DURATION = 60  # seconds

# ── Credential paths ─────────────────────────────────────────────────
DEV_AGENT_DIR = Path("dev-agent")
CREDENTIALS_FILE = DEV_AGENT_DIR / "credentials.json"
OWNER_INTAKE_FILE = DEV_AGENT_DIR / "owner-intake.json"
AGENT_WALLET_FILE = DEV_AGENT_DIR / "agent-wallet.json"
OWNER_WALLET_FILE = DEV_AGENT_DIR / "owner-wallet.json"
MEMORY_DIR = Path.home() / ".molty-royale"
MEMORY_FILE = MEMORY_DIR / "molty-royale-context.json"

# ── Environment variables ─────────────────────────────────────────────
AGENT_NAME = os.getenv("AGENT_NAME", "")
ADVANCED_MODE = os.getenv("ADVANCED_MODE", "true").lower() == "true"
ROOM_MODE = os.getenv("ROOM_MODE", "free")  # free | auto | paid
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
API_KEY = os.getenv("API_KEY", "")
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY", "")
AGENT_WALLET_ADDRESS = os.getenv("AGENT_WALLET_ADDRESS", "")
OWNER_EOA = os.getenv("OWNER_EOA", "")
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY", "")

# ── First-Run Intake answers (setup.md lines 29-39) ──────────────────
# These replace the interactive yes/no prompts for Railway/Docker.
# All default to "yes/auto" so zero-config deployment works.
AUTO_WHITELIST = os.getenv("AUTO_WHITELIST", "true").lower() == "false"        # Q4: auto-check + approve
AUTO_SC_WALLET = os.getenv("AUTO_SC_WALLET", "true").lower() == "false"       # Q6: auto-create SC wallet
ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "true").lower() == "true"         # Q7: cross-game learning
ENABLE_AGENT_TOKEN = os.getenv("ENABLE_AGENT_TOKEN", "false").lower() == "true"  # Q8: agent token
AUTO_IDENTITY = os.getenv("AUTO_IDENTITY", "true").lower() == "true"         # Q9: ERC-8004 auto-register

